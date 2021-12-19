from typing import List

import numpy as np

from plecoptera.aliases import Cost
from plecoptera.client import Client
from plecoptera.parameters import ParameterValue
from plecoptera.report import Report


class Evaluator:
    client: Client
    parameter_names: List[str]

    def __init__(self, client: Client, parameter_names: List[str]):
        self.client = client
        self.parameter_names = parameter_names

    def __np_array_to_parameter_values(self, raw_values: np.ndarray) -> List[ParameterValue]:
        parameter_values = []
        for i, raw_value in enumerate(raw_values):
            parameter_values.append(
                ParameterValue(name=self.parameter_names[i], value=int(raw_value)),
            )
        return parameter_values

    def estimate_cost(self, raw_values: np.ndarray) -> Cost:
        parameter_values = self.__np_array_to_parameter_values(raw_values)
        return self.client.estimate_cost(parameter_values)

    def register_report(
            self,
            cost: Cost,
            optimum: np.ndarray,
            iterations: int,
            evaluations: int,
            fast_evaluations: int,
    ):
        report = Report(
            cost=cost,
            optimum=self.__np_array_to_parameter_values(optimum),
            iterations=iterations,
            evaluations=evaluations,
            fast_evaluations=fast_evaluations,
        )
        self.client.register_report(report)