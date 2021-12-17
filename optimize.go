package plecoptera

import (
	"github.com/go-logr/logr"
	"github.com/pkg/errors"
)

type ParameterValue struct {
	Name  string
	Value int
}

type Report struct {
	Optimum []*ParameterValue
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
