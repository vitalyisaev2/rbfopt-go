#!/usr/bin/env python

import json
import logging
import rbfopt
import numpy as np
import requests
import sys
from urllib.parse import urljoin
from dataclasses import dataclass
from typing import List
from http import HTTPStatus

Cost = float


@dataclass
class ParameterValue:
    name: str
    value: int


class Client():
    url_head: str
    session: requests.Session

    def __init__(self, endpoint: str):
        self.url_head = f'http://{endpoint}'
        self.session = requests.Session()

    def estimate_cost(self, parameter_values: List[ParameterValue]) -> Cost:
        print(f"request '{parameter_values}'")

        # TODO: how to handle custom serialization in a beautiful way?
        payload = dict(parameter_values=[])
        for pv in parameter_values:
            payload['parameter_values'].append(pv.__dict__)

        response = self.session.get(urljoin(self.url_head, 'estimate_cost'), json=payload)
        print(f"response code={response.status_code} cost={response.json()}")

        if response.status_code != HTTPStatus.OK:
            raise ValueError(f'invalid status code {response.status_code}')
        else:
            return response.json()["cost"]

    def register_report(self, optimum: List[ParameterValue]):
        print(f"request '{optimum}'")

        response = self.session.get(
            urljoin(self.url_head, 'register_report'),
            json={'optimum': optimum},
        )
        print(f"response code={response.status_code} cost={response.json()}")

        if response.status_code != HTTPStatus.OK:
            raise f'invalid status code {response.status_code}'


class Estimator:
    client: Client
    parameter_names: List[str]

    def __init__(self, client: Client, parameter_names: List[str]):
        self.client = client
        self.parameter_names = parameter_names

    def cost_function(self, raw_values: np.ndarray) -> Cost:
        parameter_values = []
        for i, raw_value in enumerate(raw_values):
            parameter_values.append(
                ParameterValue(name=self.parameter_names[i], value=int(raw_value)),
            )

        return self.client.estimate_cost(parameter_values)


def main():
    config_path = sys.argv[1]
    with open(config_path, 'r') as f:
        config = json.load(f)

    print(config)

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

    client = Client(config['endpoint'])
    estimator = Estimator(client, var_names)

    print("dimensions", dimensions)
    print("var_lower", var_lower)
    print("var_upper", var_upper)
    print("var_types", var_types)

    bb = rbfopt.RbfoptUserBlackBox(
        dimensions, var_lower, var_upper, var_types, estimator.cost_function)

    settings = rbfopt.RbfoptSettings(max_evaluations=10)
    alg = rbfopt.RbfoptAlgorithm(settings, bb)
    val, x, itercount, evalcount, fast_evalcount = alg.optimize()

    print(val, x, itercount, evalcount, fast_evalcount)


if __name__ == "__main__":
    main()
