package optimization_test

import (
	"context"
	"testing"

	"github.com/go-logr/logr"
	"github.com/go-logr/zapr"
	"github.com/stretchr/testify/require"
	"github.com/vitalyisaev2/plecoptera/optimization"
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
	paramZ int
}

func (cfg *serviceConfig) setParamX(value int) { cfg.paramX = value }
func (cfg *serviceConfig) setParamY(value int) { cfg.paramY = value }
func (cfg *serviceConfig) setParamZ(value int) { cfg.paramZ = value }

func (cfg *serviceConfig) costFunction(_ context.Context) (optimization.Cost, error) {
	// using quite a simple polinomial function with minimum that can be easily discovered:
	// it corresponds to the upper bound of every variable
	x, y, z := cfg.paramX, cfg.paramY, cfg.paramZ
	return optimization.Cost(-1 * (x*y + z)), nil
}

func TestPlecoptera(t *testing.T) {
	t.Run("positive", func(t *testing.T) {
		cfg := &serviceConfig{}

		// set bounds to parameters
		settings := &optimization.Settings{
			Parameters: []*optimization.ParameterDescription{
				{
					Name:           "x",
					Bound:          &optimization.Bound{From: 0, To: 10},
					ConfigModifier: cfg.setParamX,
				},
				{
					Name:           "y",
					Bound:          &optimization.Bound{From: 0, To: 10},
					ConfigModifier: cfg.setParamY,
				},
				{
					Name:           "z",
					Bound:          &optimization.Bound{From: 0, To: 10},
					ConfigModifier: cfg.setParamZ,
				},
			},
			CostFunction:                    cfg.costFunction,
			MaxEvaluations:                  25,
			MaxIterations:                   25,
			InvalidParameterCombinationCost: 10,
		}

		logger := newLogger()
		ctx := logr.NewContext(context.Background(), logger)

		// perform optimization
		report, err := optimization.Optimize(ctx, settings)
		require.NoError(t, err)
		require.NotNil(t, report)

		// validate that the optimum was reached
		expectedOptimumCfg := &serviceConfig{
			paramX: settings.Parameters[0].Bound.To,
			paramY: settings.Parameters[1].Bound.To,
			paramZ: settings.Parameters[2].Bound.To,
		}

		expectedOptimumCost, err := expectedOptimumCfg.costFunction(context.Background())
		require.NoError(t, err)

		require.Equal(t, expectedOptimumCost, report.Cost)
		require.Len(t, report.Optimum, len(settings.Parameters))

		for i := 0; i < len(settings.Parameters); i++ {
			require.Equal(t, report.Optimum[i].Name, settings.Parameters[i].Name)
			require.Equal(t, report.Optimum[i].Value, settings.Parameters[i].Bound.To)
		}
	})

	t.Run("invalid parameters combination", func(t *testing.T) {
		cfg := &serviceConfig{}

		settings := &optimization.Settings{
			Parameters: []*optimization.ParameterDescription{
				{
					Name:           "x",
					Bound:          &optimization.Bound{From: 0, To: 10},
					ConfigModifier: cfg.setParamX,
				},
				{
					Name:           "y",
					Bound:          &optimization.Bound{From: 0, To: 10},
					ConfigModifier: cfg.setParamY,
				},
				{
					Name:           "z",
					Bound:          &optimization.Bound{From: 0, To: 10},
					ConfigModifier: cfg.setParamZ,
				},
			},
			// the cost function is almost the same as in previous test case, but now we impose some conditions on variables
			CostFunction: func(ctx context.Context) (optimization.Cost, error) {
				// explicitly validate parameters, throw errors if they're invalid
				if cfg.paramX < cfg.paramY {
					return 0, optimization.ErrInvalidParameterCombination
				}

				return cfg.costFunction(ctx)
			},
			MaxEvaluations:                  25,
			MaxIterations:                   25,
			InvalidParameterCombinationCost: 10,
		}

		logger := newLogger()
		ctx := logr.NewContext(context.Background(), logger)

		report, err := optimization.Optimize(ctx, settings)
		require.NoError(t, err)
		require.NotNil(t, report)

		expectedOptimumCfg := &serviceConfig{
			paramX: settings.Parameters[0].Bound.To,
			paramY: settings.Parameters[1].Bound.To,
			paramZ: settings.Parameters[2].Bound.To,
		}

		expectedOptimumCost, err := expectedOptimumCfg.costFunction(context.Background())
		require.NoError(t, err)

		require.Equal(t, expectedOptimumCost, report.Cost)
		require.Len(t, report.Optimum, len(settings.Parameters))

		for i := 0; i < len(settings.Parameters); i++ {
			require.Equal(t, report.Optimum[i].Name, settings.Parameters[i].Name)
			require.Equal(t, report.Optimum[i].Value, settings.Parameters[i].Bound.To)
		}
	})
}
