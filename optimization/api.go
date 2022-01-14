package optimization

type estimateCostRequest struct {
	ParameterValues []*ParameterValue `json:"parameter_values"`
}

type estimateCostResponse struct {
	Cost                        float64 `json:"cost"`
	InvalidParameterCombination bool    `json:"invalid_parameter_combination"`
}

type registerReportRequest struct {
	Report *Report `json:"report"`
}

type registerReportResponse struct {
}
