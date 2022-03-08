import json
import pathlib
from typing import List

import jsons
import numpy as np
import pandas as pd

from wrapper.types import Cost, ParameterValue
from wrapper.client import Client
from wrapper.report import Report
import wrapper.names as names


class Evaluator:
    __client: Client
    __parameter_names: List[str]
    __evaluations: []
    __root_dir: pathlib.Path
    __report: Report

    def __init__(self, client: Client, parameter_names: List[str], root_dir: pathlib.Path):
        self.__client = client
        self.__parameter_names = parameter_names
        self.__evaluations = []
        self.__root_dir = root_dir

    def __np_array_to_parameter_values(self, raw_values: np.ndarray) -> List[ParameterValue]:
        parameter_values = []
        for i, raw_value in enumerate(raw_values):
            parameter_values.append(
                ParameterValue(name=self.__parameter_names[i], value=int(raw_value)),
            )
        return parameter_values

    def estimate_cost(self, raw_values: np.ndarray) -> Cost:
        parameter_values = self.__np_array_to_parameter_values(raw_values)
        cost, invalid_parameter_combination = self.__client.estimate_cost(parameter_values)

        # store evaluation result for the future use
        entry = {name: value for (name, value) in zip(self.__parameter_names, raw_values)}
        entry[names.Cost] = cost
        entry[names.InvalidParameterCombination] = invalid_parameter_combination

        self.__evaluations.append(entry)

        return cost

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
        self.__report = report

    def dump(self) -> (pd.DataFrame, Report):
        # dump history of evaluations for future usage
        evaluations = pd.DataFrame(self.__evaluations)
        file_path = self.__root_dir.joinpath("evaluations.csv")
        evaluations.to_csv(file_path, header=True)

        # dump report for future usage
        file_path = self.__root_dir.joinpath("report.json")
        self.__report.save_to_file(file_path)

        return evaluations, self.__report
