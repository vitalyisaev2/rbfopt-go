package optimization

import (
	"context"

	"github.com/go-logr/logr"
	"github.com/pkg/errors"
)

type costEstimator struct {
	attempts    int // attempts made by optimizer
	settings    *Settings
	finalReport *Report
}

func (ce *costEstimator) estimateCost(ctx context.Context, request *estimateCostRequest) (*estimateCostResponse, error) {
	logger := logr.FromContextOrDiscard(ctx)

	// apply all values to config first
	for _, pv := range request.ParameterValues {
		parameterDesc, err := ce.settings.getParameterByName(pv.Name)
		if err != nil {
			return nil, errors.Wrapf(err, "get parameter by name: %s", pv.Name)
		}

		parameterDesc.ConfigModifier(pv.Value)
	}

	ce.attempts++

	// then run cost estimation
	cost, err := ce.settings.CostFunction(ctx)

	response := &estimateCostResponse{Cost: cost}

	if err != nil {
		// notify optimizer about the invalid combination of parameters
		if !errors.Is(err, ErrInvalidParameterCombination) {
			return nil, errors.Wrap(err, "cost function call")
		}

		response.InvalidParameterCombination = true
		response.Cost = ce.settings.InvalidParameterCombinationCost
	}

	if cost >= ce.settings.InvalidParameterCombinationCost {
		return nil, errors.Wrapf(
			errTooHighInvalidParameterCombinationCost,
			"cost=%v, invalid_parameter_combination_cost=%v",
			cost, ce.settings.InvalidParameterCombinationCost,
		)
	}

	logger.V(1).Info(
		"estimate cost",
		"attempts", ce.attempts,
		"request", request,
		"response", response)

	return response, nil
}

func (ce *costEstimator) registerReport(ctx context.Context, request *registerReportRequest) (*registerReportResponse, error) {
	logger := logr.FromContextOrDiscard(ctx)

	if ce.finalReport != nil {
		return nil, errors.New("report has been already registered")
	}

	if request.Report == nil {
		return nil, errors.New("empty report")
	}

	ce.finalReport = request.Report

	logger.V(0).Info("register report", "report", request.Report)

	// response is empty, but for the sake of symmetry, return it anyway
	return &registerReportResponse{}, nil
}

func newCostEstimator(settings *Settings) *costEstimator {
	return &costEstimator{settings: settings}
}
