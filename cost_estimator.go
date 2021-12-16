package plecoptera

import (
	"context"

	"github.com/pkg/errors"
)

type costEstimator struct {
	settings *Settings
}

func (ce *costEstimator) estimateCost(ctx context.Context, parameterValues ParameterValues) (Cost, error) {
	// apply all values first
	for parameterName, parameterValue := range parameterValues {
		parameterDesc, err := ce.settings.getParameterByName(parameterName)
		if err != nil {
			return 0, errors.Wrapf(err, "get parameter by name: %s", parameterName)
		}

		parameterDesc.ConfigModifier(parameterValue)
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
