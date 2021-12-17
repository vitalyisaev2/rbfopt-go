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
}

type rbfOpt struct {
	rootDir string
}

const rbfOptWrapper = "plecoptera.py"

func (r *rbfOpt) run(ctx context.Context, settings *Settings) error {
	path := filepath.Join(r.rootDir, "config.json")

	if err := r.dumpConfig(settings, path); err != nil {
		return errors.Wrap(err, "dump config")
	}

	cmd := exec.Command(rbfOptWrapper, path)
	if err := r.executeCommand(ctx, cmd); err != nil {
		return errors.Wrap(err, "execute command")
	}

	return nil
}

func (r *rbfOpt) dumpConfig(settings *Settings, path string) error {
	cfg := &rbfOptSettings{
		Parameters: settings.Parameters,
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

func (r *rbfOpt) executeCommand(ctx context.Context, cmd *exec.Cmd) error {
	logger, err := logr.FromContext(ctx)
	if err != nil {
		return errors.Wrap(err, "from context")
	}

	logger.Info("executing command", "cmd", cmd)

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
