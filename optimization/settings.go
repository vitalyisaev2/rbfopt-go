package optimization

import (
	"context"

	"github.com/pkg/errors"
)

type Cost = float64

// CostFunction is implemented by clients. Optimization algorithm will try to optimization
// your parameters on the basis of this function. CostFunction call is expected to be expensive,
// so client should check context expiration.
type CostFunction func(ctx context.Context) (Cost, error)

// Settings contains optimization techniques
type Settings struct {
	Parameters   []*ParameterDescription
	CostFunction CostFunction
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
