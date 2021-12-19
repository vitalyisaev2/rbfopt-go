from typing import List

import numpy as np
import pandas as pd

from plecoptera.aliases import Cost
from plecoptera.client import Client
from plecoptera.parameters import ParameterValue
from plecoptera.report import Report


class Evaluator:
    __client: Client
    __parameter_names: List[str]
    __evaluations: []

    def __init__(self, client: Client, parameter_names: List[str]):
        self.__client = client
        self.__parameter_names = parameter_names
        self.__evaluations = []

    def __np_array_to_parameter_values(self, raw_values: np.ndarray) -> List[ParameterValue]:
        parameter_values = []
        for i, raw_value in enumerate(raw_values):
            parameter_values.append(
                ParameterValue(name=self.__parameter_names[i], value=int(raw_value)),
            )
        return parameter_values

    def estimate_cost(self, raw_values: np.ndarray) -> Cost:
        parameter_values = self.__np_array_to_parameter_values(raw_values)
        cost = self.__client.estimate_cost(parameter_values)

        # store evaluation result for the future use
        entry = {name: value for (name, value) in zip(self.__parameter_names, raw_values)}
        entry["cost"] = cost

        self.__evaluations.append(entry)

        return cost

    @property
    def evaluations(self) -> pd.DataFrame:
        return pd.DataFrame(self.__evaluations)

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
        self.__client.register_report(report)