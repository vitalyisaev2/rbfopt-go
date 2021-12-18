#!/usr/bin/env python

import json
import jsons
import rbfopt
import numpy as np
import requests
import sys
from urllib.parse import urljoin
from dataclasses import dataclass
from typing import List
from http import HTTPStatus


@dataclass
class Settings:
    dimensions: int
    var_names: List[str]
    var_lower: np.array
    var_upper: np.array
    var_types: np.chararray
    endpoint: str

    @classmethod
    def from_config(cls, config_path: str) -> 'Settings':
        with open(config_path, 'r') as f:
            config = json.load(f)

        parameters = config['parameters']
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
            endpoint=config['endpoint'],
        )


Cost = float


@dataclass
class ParameterValue:
    name: str
    value: int


@dataclass
class Report:
    cost: Cost
    optimum: List[ParameterValue]
    iterations: int
    evaluations: int
    fast_evaluations: int


class Client():
    url_head: str
    session: requests.Session

    def __init__(self, endpoint: str):
        self.url_head = f'http://{endpoint}'
        self.session = requests.Session()

    def estimate_cost(self, parameter_values: List[ParameterValue]) -> Cost:
        print(f"request '{parameter_values}'")

        payload = dict(parameter_values=parameter_values)
        response = self.session.get(
            urljoin(self.url_head, 'estimate_cost'),
            json=jsons.dump(payload),
        )

        print(f"response code={response.status_code} cost={response.json()}")

        if response.status_code != HTTPStatus.OK:
            raise ValueError(f'invalid status code {response.status_code}')
        else:
            return response.json()["cost"]

    def register_report(self, report: Report):
        print(f"request '{report}'")

        payload = dict(report=report)
        response = self.session.post(
            urljoin(self.url_head, 'register_report'),
            json=jsons.dump(payload),
        )

        print(f"response code={response.status_code} cost={response}")

        if response.status_code != HTTPStatus.OK:
            raise ValueError(f'invalid status code {response.status_code}')


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


def main():
    # prepare infrastructure
    settings = Settings.from_config(sys.argv[1])

    client = Client(settings.endpoint)
    evaluator = Evaluator(client, settings.var_names)

    bb = rbfopt.RbfoptUserBlackBox(
        settings.dimensions,
        settings.var_lower,
        settings.var_upper,
        settings.var_types,
        evaluator.estimate_cost,
    )

    # perform optimization and post report to server
    settings = rbfopt.RbfoptSettings(max_evaluations=10)
    alg = rbfopt.RbfoptAlgorithm(settings, bb)
    evaluator.register_report(*alg.optimize())


if __name__ == "__main__":
    main()
