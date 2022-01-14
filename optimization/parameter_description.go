package optimization

import (
	"regexp"

	"github.com/pkg/errors"
)

// ConfigModifier injects parameter value received from the optimizer into configuration instance
type ConfigModifier func(int)

// Bound describes reasonable bounds for parameter variation
type Bound struct {
	From int `json:"from"`
	To   int `json:"to"`
}

// ParameterDescription is something you want to optimization in your service configuration
type ParameterDescription struct {
	Bound          *Bound         `json:"bound"`
	ConfigModifier ConfigModifier `json:"-"`
	Name           string         `json:"name"`
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
		return errors.New("parameter ConfigModifier is empty")
	}

	return nil
}
