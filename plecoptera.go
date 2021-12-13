package plecoptera

import (
	"github.com/pkg/errors"
	"gonum.org/v1/gonum/optimize"
)

// TODO: check this function as it was copied from gonum
type functionThresholdConverger struct {
	threshold float64
}

func (functionThresholdConverger) Init(dim int) {}

func (f functionThresholdConverger) Converged(loc *optimize.Location) optimize.Status {
	if loc.F < f.threshold {
		return optimize.FunctionThreshold
	}
	return optimize.NotTerminated
}

type Params struct {
	Dimensions   uint
	CostFunction func(args []float64) float64
}

func FindOptimum(params *Params) ([]float64, error) {
	method := &optimize.CmaEsChol{}

	initX := make([]float64, params.Dimensions)

	settings := &optimize.Settings{
		Converger: &functionThresholdConverger{threshold: 0.1},
	}

	problem := optimize.Problem{
		Func: params.CostFunction,
	}

	result, err := optimize.Minimize(problem, initX, settings, method)
	if err != nil {
		return nil, errors.Wrap(err, "minimize")
	}

	return result.Location.X, nil
}
