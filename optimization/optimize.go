package optimization

import (
	"context"
	"fmt"
	"os"
	"path/filepath"
	"time"

	"github.com/go-logr/logr"
	"github.com/pkg/errors"
)

type ParameterValue struct {
	Name  string
	Value int
}

type Report struct {
	Cost            Cost              `json:"cost"`
	Optimum         []*ParameterValue `json:"optimum"`
	Iterations      int               `json:"iterations"`
	Evaluations     int               `json:"evaluations"`
	FastEvaluations int               `json:"fast_evaluations"`
}

func Optimize(ctx context.Context, settings *Settings) (*Report, error) {
	logger := logr.FromContextOrDiscard(ctx)

	// check settings
	if err := settings.validate(); err != nil {
		return nil, errors.Wrap(err, "validate settings")
	}

	// run HTTP server that will redirect requests from Python optimizer to your Go service
	estimator := newCostEstimator(settings)

	endpoint := "0.0.0.0:8080"
	srv := newServer(logger, endpoint, estimator)
	defer srv.quit()

	// create temporary dir for configs and artifacts
	// FIXME: take root dir from settings
	rootDir := filepath.Join(
		"/tmp",
		fmt.Sprintf("plecoptera_%v", time.Now().Format("20060102_150405")),
	)
	if err := os.MkdirAll(rootDir, 0755); err != nil {
		return nil, errors.Wrap(err, "mkdir all")
	}

	// run Python optimizer
	ctx = logr.NewContext(ctx, logger)
	if err := runRbfOpt(ctx, settings, rootDir, endpoint); err != nil {
		return nil, errors.Wrapf(err, "run python part")
	}

	// obtain final report
	report := estimator.finalReport
	if report == nil {
		return nil, errors.New("protocol error: report is nil")
	}

	return report, nil
}
