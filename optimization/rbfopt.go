package optimization

import (
	"bufio"
	"bytes"
	"context"
	"encoding/json"
	"io/ioutil"
	"os/exec"
	"path/filepath"

	"github.com/go-logr/logr"
	"github.com/pkg/errors"
)

type rbfOptSettings struct {
	Endpoint                               string                  `json:"endpoint"`
	Parameters                             []*ParameterDescription `json:"parameters"`
	MaxEvaluations                         uint                    `json:"max_evaluations"`
	MaxIterations                          uint                    `json:"max_iterations"`
	SkipInvalidParameterCombinationOnPlots bool                    `json:"skip_invalid_parameter_combination_on_plots"`
	InitStrategy                           InitStrategy            `json:"init_strategy"`
}

type rbfOptWrapper struct {
	ctx      context.Context
	settings *Settings
	rootDir  string
	endpoint string
}

const rbfOptGoExecutable = "rbfopt-go-wrapper"

func (r *rbfOptWrapper) run() error {
	path := filepath.Join(r.rootDir, "settings.json")

	if err := r.dumpConfig(path); err != nil {
		return errors.Wrap(err, "dump config")
	}

	//nolint:gosec
	cmd := exec.Command(rbfOptGoExecutable, r.rootDir)
	if err := r.executeCommand(r.ctx, cmd); err != nil {
		return errors.Wrap(err, "execute command")
	}

	return nil
}

func (r *rbfOptWrapper) dumpConfig(path string) error {
	cfg := &rbfOptSettings{
		Endpoint:                               r.endpoint,
		Parameters:                             r.settings.Parameters,
		MaxEvaluations:                         r.settings.MaxEvaluations,
		MaxIterations:                          r.settings.MaxIterations,
		SkipInvalidParameterCombinationOnPlots: r.settings.SkipInvalidParameterCombinationOnPlots,
	}

	data, err := json.Marshal(cfg)
	if err != nil {
		return errors.Wrap(err, "json marshal")
	}

	if err := ioutil.WriteFile(path, data, 0644); err != nil {
		return errors.Wrap(err, "write file")
	}

	return nil
}

func (r *rbfOptWrapper) executeCommand(ctx context.Context, cmd *exec.Cmd) error {
	logger, err := logr.FromContext(ctx)
	if err != nil {
		return errors.Wrap(err, "logr from context")
	}

	logger.Info("executing command", "cmd", cmd)

	var (
		stdoutBuf = &bytes.Buffer{}
		stderrBuf = &bytes.Buffer{}
	)

	cmd.Stdout = stdoutBuf
	cmd.Stderr = stderrBuf

	err = cmd.Run()

	// print

	if stdoutBuf.Len() > 0 {
		logger.V(1).Info("subprocess stdout")

		scanner := bufio.NewScanner(stdoutBuf)
		for scanner.Scan() {
			logger.V(1).Info(scanner.Text())
		}
	}

	if stderrBuf.Len() > 0 {
		logger.V(1).Info("subprocess stderr")

		scanner := bufio.NewScanner(stderrBuf)
		for scanner.Scan() {
			logger.V(1).Info(scanner.Text())
		}
	}

	if err != nil {
		return errors.Wrap(err, "cmd run")
	}

	return nil
}

func runRbfOpt(ctx context.Context, settings *Settings, rootDir, endpoint string) error {
	wrapper := &rbfOptWrapper{
		ctx:      ctx,
		settings: settings,
		rootDir:  rootDir,
		endpoint: endpoint,
	}

	if err := wrapper.run(); err != nil {
		return errors.Wrap(err, "run RbfOpt wrapper")
	}

	return nil
}
