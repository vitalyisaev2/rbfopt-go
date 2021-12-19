package optimization

import (
	"regexp"

	"github.com/pkg/errors"
)

type ConfigModifier func(int)

type Bound struct {
	From int `json:"from"`
	To   int `json:"to"`
}

// ParameterDescription is something you want to optimization in your service configuration
type ParameterDescription struct {
	Name           string         `json:"name"`  // Brief name of your parameter
	Bound          *Bound         `json:"bound"` // Some reasonable bounds for the parameters
	ConfigModifier ConfigModifier `json:"-"`
}

const namePattern = "[a-zA-Z0-9_]"

func (pd *ParameterDescription) validate() error {
	matched, err := regexp.MatchString(namePattern, pd.Name)
	if err != nil {
		return errors.Wrap(err, "regexp match string")
	}

	if !matched {
		return errors.Errorf("name '%s' does not match pattern '%s'", pd.Name, namePattern)
	}

	if pd.ConfigModifier == nil {
		return errors.New("ConfigModifier is empty")
	}

	return nil
}
