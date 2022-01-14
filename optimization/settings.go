package optimization

import (
	"context"
	"math"

	"github.com/pkg/errors"
)

type Cost = float64

// CostFunction is implemented by clients. Optimization algorithm will try to optimization
// your parameters on the basis of this function. CostFunction call is expected to be expensive,
// so client should check context expiration.
type CostFunction func(ctx context.Context) (Cost, error)

// ErrInvalidParameterCombination notifies optimizer about invalid combination of parameters.
// CostFunction must return MaxCost and ErrInvalidParameterCombination if it happened.
var ErrInvalidParameterCombination = errors.New("Invalid parameter combination")

var errTooHighInvalidParameterCombinationCost = errors.New(
	"Too high value of InvalidParameterCombinationCost: " +
		"visit https://github.com/coin-or/rbfopt/issues/28#issuecomment-629720480 to pick a good one")

// Settings parametrize optimization techniques
type Settings struct {
	Parameters                      []*ParameterDescription
	CostFunction                    CostFunction
	MaxEvaluations                  uint
	MaxIterations                   uint
	InvalidParameterCombinationCost Cost // Reason: https://github.com/coin-or/rbfopt/issues/28
}

func (s *Settings) validate() error {
	if len(s.Parameters) == 0 {
		return errors.New("Parameters are empty")
	}

	if s.CostFunction == nil {
		return errors.New("CostFunction is empty")
	}

	for _, param := range s.Parameters {
		if err := param.validate(); err != nil {
			return errors.Wrapf(err, "validate parameter '%s'", param.Name)
		}
	}

	if s.MaxEvaluations == 0 {
		return errors.New("MaxEvaluations is empty")
	}

	if s.MaxIterations == 0 {
		return errors.New("MaxIterations is empty")
	}

	if s.InvalidParameterCombinationCost == math.MaxFloat64 {
		return errTooHighInvalidParameterCombinationCost
	}

	return nil
}

func (s *Settings) getParameterByName(name string) (*ParameterDescription, error) {
	for _, param := range s.Parameters {
		if param.Name == name {
			return param, nil
		}
	}

	return nil, errors.Errorf("param '%s' does not exist", name)
}
