package plecoptera

import (
	"context"
	"regexp"

	"github.com/go-logr/logr"
	"github.com/pkg/errors"
)

type ConfigModifier func(int)

type Bound struct {
	From int
	To   int
}

// ParameterDescription is something you want to optimize in your service configuration
type ParameterDescription struct {
	Name           string         `json:"name"` // Brief name of your parameter
	ConfigModifier ConfigModifier `json:"-"`
	Bound          *Bound         `json:"bound"` // Some reasonable bounds for the parameters
}

const namePattern = "[a-zA-Z0-9_]"

func (pd *ParameterDescription) validate() error {
	matched, err := regexp.MatchString(namePattern, pd.Name)
	if err != nil {
		return errors.Wrap(err, "regexp match string")
	}

	if !matched {
		return errors.Errorf("name '%s' does not match pattern '%s'", pd.Name, namePattern)
	}

	if pd.ConfigModifier == nil {
		return errors.New("ConfigModifier is empty")
	}

	return nil
}

type Cost = float64

// CostFunction is implemented by clients. Optimization algorithm will try to optimize
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

type ParameterValues map[string]int

type Report struct {
	Values ParameterValues
}

func Optimize(logger logr.Logger, settings *Settings) (*Report, error) {
	if err := settings.validate(); err != nil {
		return nil, errors.Wrap(err, "validate settings")
	}

	estimator := newCostEstimator(settings)

	srv := newServer(logger, estimator)
	defer srv.quit()

	// TODO: call python here

	return nil, nil
}
