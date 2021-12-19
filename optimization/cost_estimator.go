package optimization

import (
	"context"

	"github.com/pkg/errors"
)

type costEstimator struct {
	settings *Settings
}

func (ce *costEstimator) estimateCost(ctx context.Context, parameterValues []*ParameterValue) (Cost, error) {
	// apply all values to config first
	for _, pv := range parameterValues {
		parameterDesc, err := ce.settings.getParameterByName(pv.Name)
		if err != nil {
			return 0, errors.Wrapf(err, "get parameter by name: %s", pv.Name)
		}

		parameterDesc.ConfigModifier(pv.Value)
	}

	// then run cost estimation
	cost, err := ce.settings.CostFunction(ctx)
	if err != nil {
		return 0, errors.Wrap(err, "cost function call")
	}

	return cost, nil
}

func newCostEstimator(settings *Settings) *costEstimator {
	return &costEstimator{settings: settings}
}
