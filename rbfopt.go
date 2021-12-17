package plecoptera

import (
	"bufio"
	"context"
	"encoding/json"
	"io/ioutil"
	"os/exec"
	"path/filepath"
	"sync"

	"github.com/go-logr/logr"
	"github.com/pkg/errors"
)

type rbfOptSettings struct {
	Parameters []*ParameterDescription `json:"parameters"`
	Endpoint   string                  `json:"endpoint"`
}

type rbfOptWrapper struct {
	rootDir  string
	endpoint string
	settings *Settings
	ctx      context.Context
}

const rbfOptExecutable = "/home/isaev/go/src/github.com/vitalyisaev2/plecoptera/plecoptera.py"

func (r *rbfOptWrapper) run() error {
	path := filepath.Join(r.rootDir, "config.json")

	if err := r.dumpConfig(path); err != nil {
		return errors.Wrap(err, "dump config")
	}

	cmd := exec.Command(rbfOptExecutable, path)
	if err := r.executeCommand(r.ctx, cmd); err != nil {
		return errors.Wrap(err, "execute command")
	}

	return nil
}

func (r *rbfOptWrapper) dumpConfig(path string) error {
	cfg := &rbfOptSettings{
		Parameters: r.settings.Parameters,
		Endpoint:   r.endpoint,
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
		return errors.Wrap(err, "from context")
	}

	logger.V(1).Info("executing command", "cmd", cmd)

	stdoutReader, err := cmd.StdoutPipe()
	if err != nil {
		return errors.Wrap(err, "cmd stdout reader")
	}

	stderrReader, err := cmd.StderrPipe()
	if err != nil {
		return errors.Wrap(err, "cmd stderr reader")
	}

	stdoutScanner := bufio.NewScanner(stdoutReader)
	stderrScanner := bufio.NewScanner(stderrReader)

	wg := &sync.WaitGroup{}
	wg.Add(2)

	go func() {
		defer wg.Done()

		for stdoutScanner.Scan() {
			logger.V(1).Info(stdoutScanner.Text())
		}
	}()

	go func() {
		defer wg.Done()

		for stderrScanner.Scan() {
			logger.V(1).Info(stderrScanner.Text())
		}
	}()

	if err := cmd.Start(); err != nil {
		return errors.Wrap(err, "cmd Start")
	}

	wg.Wait()

	if err := cmd.Wait(); err != nil {
		return errors.Wrap(err, "cmd wait")
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
