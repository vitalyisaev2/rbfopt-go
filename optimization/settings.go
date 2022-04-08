package optimization

import (
	"context"
	"fmt"
	"math"

	"github.com/pkg/errors"
)

// Cost represents the value returned by cost function.
type Cost = float64

// CostFunction (or objective function) is implemented by clients.
// Optimizer will try to find the best possible combination of your parameters on the basis of this function.
// CostFunction call is expected to be expensive, so client should check context expiration.
type CostFunction func(ctx context.Context) (Cost, error)

// ErrInvalidParameterCombination notifies optimizer about invalid combination of parameters.
// CostFunction must return MaxCost and ErrInvalidParameterCombination if it happened.
var ErrInvalidParameterCombination = errors.New("invalid parameter combination")

var errTooHighInvalidParameterCombinationCost = errors.New(
	"too high value of InvalidParameterCombinationCost: " +
		"visit https://github.com/coin-or/rbfopt/issues/28#issuecomment-629720480 to pick a good one")

type InitStrategy int8

const (
	LHDMaximin InitStrategy = iota
	LHDCorr
	AllCorners
	LowerCorners
	RandCorners
)

func (s InitStrategy) MarshalJSON() ([]byte, error) {
	switch s {
	case LHDMaximin:
		return []byte("\"lhd_maximin\""), nil
	case LHDCorr:
		return []byte("\"lhd_corr\""), nil
	case AllCorners:
		return []byte("\"all_corners\""), nil
	case LowerCorners:
		return []byte("\"lower_corners\""), nil
	case RandCorners:
		return []byte("\"rand_corners\""), nil
	default:
		return nil, errors.New(fmt.Sprintf("unknown InitStarategy: %v", s))
	}
}

// Settings contains the description of what and how to optimize.
type Settings struct {
	// CostFunction itself
	CostFunction CostFunction
	// Arguments of a CostFunctions
	Parameters []*ParameterDescription
	// RBFOpt: limits number of evaluations
	MaxEvaluations uint
	// RBFOpt: limits number of iterations
	MaxIterations uint
	// RBFOpt: reason: https://github.com/coin-or/rbfopt/issues/28
	InvalidParameterCombinationCost Cost
	// Set to true if you don't want to see large values corresponding to the ErrInvalidParametersCombination on your plots
	SkipInvalidParameterCombinationOnPlots bool
	// Strategy to select initial points.
	InitStrategy InitStrategy
}

func (s *Settings) validate() error {
	if len(s.Parameters) == 0 {
		return errors.New("parameter Parameters are empty")
	}

	if s.CostFunction == nil {
		return errors.New("parameter CostFunction is empty")
	}

	for _, param := range s.Parameters {
		if err := param.validate(); err != nil {
			return errors.Wrapf(err, "validate parameter '%s'", param.Name)
		}
	}

	if s.MaxEvaluations == 0 {
		return errors.New("parameter MaxEvaluations is empty")
	}

	if s.MaxIterations == 0 {
		return errors.New("parameter MaxIterations is empty")
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
