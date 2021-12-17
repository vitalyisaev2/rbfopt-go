package plecoptera

import (
	"context"
	"fmt"
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
	Optimum []*ParameterValue
}

func Optimize(ctx context.Context, settings *Settings) (*Report, error) {
	logger := logr.FromContextOrDiscard(ctx)

	// check settings
	if err := settings.validate(); err != nil {
		return nil, errors.Wrap(err, "validate settings")
	}

	// run HTTP server that will redirect requests from Python optimizer to your Go service
	estimator := newCostEstimator(settings)

	endpoint := ":8080"
	srv := newServer(logger, endpoint, estimator)
	defer srv.quit()

	// FIXME: take root dir from settings
	rootDir := filepath.Join(
		"/tmp",
		fmt.Sprintf("plecoptera_%v", time.Now().Format("20060102_150405")),
	)

	// run Python optimizer
	ctx = logr.NewContext(ctx, logger)
	if err := runRbfOpt(ctx, settings, rootDir, endpoint); err != nil {
		return nil, errors.Wrapf(err, "run python part")
	}

	// get request from service
	report := srv.report
	if report == nil {
		return nil, errors.New("protocol error: report is nil")
	}

	return report, nil
}
