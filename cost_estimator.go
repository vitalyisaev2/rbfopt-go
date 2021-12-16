package plecoptera

type costEstimator struct {
	settings *Settings
}

func (ce *costEstimator) estimateCost(parameterValues ParameterValues) (Cost, error) {
	panic("not implemented")
}

func newCostEstimator(settings *Settings) *costEstimator {
	return &costEstimator{settings: settings,}
}
