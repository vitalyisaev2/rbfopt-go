package optimization

import (
	"context"

	"github.com/pkg/errors"
)

type costEstimator struct {
	settings    *Settings
	finalReport *Report
}

func (ce *costEstimator) estimateCost(ctx context.Context, request *estimateCostRequest) (*estimateCostResponse, error) {
	// apply all values to config first
	for _, pv := range request.ParameterValues {
		parameterDesc, err := ce.settings.getParameterByName(pv.Name)
		if err != nil {
			return nil, errors.Wrapf(err, "get parameter by name: %s", pv.Name)
		}

		parameterDesc.ConfigModifier(pv.Value)
	}

	// then run cost estimation
	cost, err := ce.settings.CostFunction(ctx)
	if err != nil {
		// notify optimizer about the invalid combination of parameters
		if errors.Is(err, ErrInvalidParameterCombination) {
			return &estimateCostResponse{Cost: cost, InvalidParameterCombination: true}, nil
		}

		return nil, errors.Wrap(err, "cost function call")
	}

	return &estimateCostResponse{Cost: cost, InvalidParameterCombination: false}, nil
}

func (ce *costEstimator) registerReport(_ context.Context, request *registerReportRequest) (*registerReportResponse, error) {
	if ce.finalReport != nil {
		return nil, errors.New("report has been already registered")
	}

	if request.Report == nil {
		return nil, errors.New("empty report")
	}

	ce.finalReport = request.Report

	// response is empty, but for the sake of symmetry, return it anyway
	return &registerReportResponse{}, nil
}

func newCostEstimator(settings *Settings) *costEstimator {
	return &costEstimator{settings: settings}
}
