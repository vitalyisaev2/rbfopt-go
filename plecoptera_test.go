package plecoptera_test

import (
	"context"
	"testing"

	"github.com/go-logr/logr"
	"github.com/go-logr/zapr"
	"github.com/stretchr/testify/require"
	"github.com/vitalyisaev2/plecoptera"
	"go.uber.org/zap"
	"go.uber.org/zap/zapcore"
)

func newLogger() logr.Logger {
	config := zap.NewDevelopmentConfig()
	config.EncoderConfig.EncodeLevel = zapcore.CapitalColorLevelEncoder
	zapLog, err := config.Build()
	if err != nil {
		panic(err)
	}

	return zapr.NewLogger(zapLog)
}

type serviceConfig struct {
	paramX int
	paramY int
}

func (cfg *serviceConfig) setParamX(value int) { cfg.paramX = value }
func (cfg *serviceConfig) setParamY(value int) { cfg.paramY = value }

func (cfg *serviceConfig) costFunction(_ context.Context) (plecoptera.Cost, error) {
	// simple function with minimum that can be easily discovered:
	// it matches the upper bound of every variable
	return plecoptera.Cost(-1 * cfg.paramX * cfg.paramY), nil
}

func TestPlecoptera(t *testing.T) {
	cfg := &serviceConfig{}

	settings := &plecoptera.Settings{
		Parameters: []*plecoptera.ParameterDescription{
			{
				Name:           "x",
				Bound:          &plecoptera.Bound{From: 0, To: 10},
				ConfigModifier: cfg.setParamX,
			},
			{
				Name:           "y",
				Bound:          &plecoptera.Bound{From: 0, To: 10},
				ConfigModifier: cfg.setParamY,
			},
		},
		CostFunction: cfg.costFunction,
	}

	logger := newLogger()
	ctx := logr.NewContext(context.Background(), logger)

	report, err := plecoptera.Optimize(ctx, settings)
	require.NoError(t, err)
	require.NotNil(t, report)

	expectedOptimumCfg := &serviceConfig{
		paramX: settings.Parameters[0].Bound.To,
		paramY: settings.Parameters[1].Bound.To,
	}

	expectedOptimumCost, err := expectedOptimumCfg.costFunction(context.Background())
	require.NoError(t, err)

	require.Equal(t, expectedOptimumCost, report.Cost)
	require.Len(t, report.Optimum, len(settings.Parameters))

	for i := 0; i < len(settings.Parameters); i++ {
		require.Equal(t, report.Optimum[i].Name, settings.Parameters[i].Name)
		require.Equal(t, report.Optimum[i].Value, settings.Parameters[i].Bound.To)
	}
}
