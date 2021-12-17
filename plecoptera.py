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
    logger: logging.Logger

    def __init__(self, logger: logging.Logger, endpoint: str):
        self.url_head = f'http://{endpoint}'
        self.session = requests.Session()
        self.logger = logger

    def estimate_cost(self, parameter_values: List[ParameterValue]) -> Cost:
        self.logger.info("estimate_cost request" % parameter_values)

        # TODO: how to handle custom serialization in a beautiful way
        payload = dict(parameter_values=[])
        for pv in parameter_values:
            payload['parameter_values'].append(pv.__dict__)

        response = self.session.get(urljoin(self.url_head, 'estimate_cost'), json=payload)

        if response.status_code != HTTPStatus.OK:
            self.logger.error("estimate_cost response %s" % response.status_code)
            raise ValueError(f'invalid status code {response.status_code}')
        else:
            self.logger.info("estimate_cost response", response.json())

    def register_report(self, optimum: List[ParameterValue]):
        self.logger.info("register_report request", optimum)

        response = self.session.get(
            urljoin(self.url_head, 'register_report'),
            json={'optimum': optimum},
        )

        if response.status_code != HTTPStatus.OK:
            self.logger.error("register_report response", response.status_code)
            raise f'invalid status code {response.status_code}'
        else:
            self.logger.info("register_report response", response.json())


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
                ParameterValue(name=self.parameter_names[0], value=raw_value),
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

    logger = logging.getLogger('plecoptera')
    client = Client(logger, config['endpoint'])
    estimator = Estimator(client, var_names)

    bb = rbfopt.RbfoptUserBlackBox(
        dimensions, var_lower, var_upper, var_types, estimator.cost_function)

    settings = rbfopt.RbfoptSettings(max_evaluations=10)
    alg = rbfopt.RbfoptAlgorithm(settings, bb)
    val, x, itercount, evalcount, fast_evalcount = alg.optimize()

    print(val, x, itercount, evalcount, fast_evalcount)


if __name__ == "__main__":
    main()
