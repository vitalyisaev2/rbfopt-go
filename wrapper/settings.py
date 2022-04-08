import json
import pathlib
from dataclasses import dataclass
from typing import List

import numpy as np

@dataclass
class Settings:
    dimensions: int
    var_names: List[str]
    var_lower: np.array
    var_upper: np.array
    var_types: np.chararray
    endpoint: str
    max_iterations: int
    max_evaluations: int
    skip_invalid_parameter_combination_on_plots: bool
    init_strategy: str

    @classmethod
    def from_file(cls, root_dir: pathlib.Path) -> 'Settings':
        settings_path = root_dir.joinpath("settings.json")

        with open(settings_path, 'r') as f:
            ss = json.load(f)

        parameters = ss['parameters']
        dimensions = len(parameters)

        var_names = []
        var_lower = np.zeros(shape=(dimensions,))
        var_upper = np.zeros(shape=(dimensions,))
        var_types = np.chararray(shape=(dimensions,))
        for i, param in enumerate(parameters):
            var_names.append(param['name'])
            var_lower[i] = param['bound']['from']
            var_upper[i] = param['bound']['to']
            var_types[i] = 'I'

        print("dimensions", dimensions)
        print("var_lower", var_lower)
        print("var_upper", var_upper)
        print("var_types", var_types)

        return cls(
            dimensions=dimensions,
            var_names=var_names,
            var_lower=var_lower,
            var_upper=var_upper,
            var_types=var_types,
            endpoint=ss['endpoint'],
            max_evaluations=ss['max_evaluations'],
            max_iterations=ss['max_iterations'],
            skip_invalid_parameter_combination_on_plots=ss['skip_invalid_parameter_combination_on_plots'],
            init_strategy=ss['init_strategy'],
        )