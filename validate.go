package plecoptera

import (
	"reflect"

	"github.com/pkg/errors"
)

func validateSettings(settings *Settings, cfg interface{}) error {
	cfgType := reflect.TypeOf(cfg)

	for _, param := range settings.Parameters {
		err := validateParameterDescription(cfgType, param)
		if err != nil {
			return errors.Wrapf(err, "validate %v", param.ConfigModifier)
		}
	}

	return nil
}

func validateParameterDescription(cfgType reflect.Type, param *ParameterDescription) error {
	method, ok := cfgType.MethodByName(param.ConfigModifier)
	if !ok {
		return errors.New("method does not exist")
	}

	m := reflect.TypeOf(method)

	// setter may accept only one function with

	if m.NumIn() != 1 {
		return errors.Errorf(
			"unexpected number of arguments of method: expected: %v, actual: %v",
			1, m.NumIn(),
		)
	}

	arg := m.In(0)
	argKind := arg.Kind()
	if argKind != reflect.Int {
		return errors.Errorf(
			"unexpected type of argument: expected: %v, actual: %v",
			reflect.Int, argKind,
		)
	}
}
}
