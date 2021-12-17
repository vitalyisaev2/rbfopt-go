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
    endpoint: str
    session: requests.Session
    logger: logging.Logger

    def __init__(self, logger: logging.Logger, endpoint: str):
        self.endpoint = endpoint
        self.session = requests.Session()
        self.logger = logger

    def estimate_cost(self, parameter_values: List[ParameterValue]) -> Cost:
        self.logger.info("estimate_cost request", parameter_values)

        response = self.session.get(
            urljoin(self.endpoint, 'estimate_cost'),
            json={'parameter_values': parameter_values},
        )

        if response.status_code != HTTPStatus.OK:
            self.logger.error("estimate_cost response", response.status_code)
            raise f'invalid status code {response.status_code}'
        else:
            self.logger.info("estimate_cost response", response.json())

    def register_report(self, optimum: List[ParameterValue]):
        self.logger.info("register_report request", optimum)

        response = self.session.get(
            urljoin(self.endpoint, 'register_report'),
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

    def __init__(self, client: Client):
        self.client = client

    def cost_function(self, raw_values: np.ndarray[float]) -> Cost:
        parameter_values = []
        for i, raw_value in enumerate(raw_values):
            parameter_values.append(
                ParameterValue(name=self.parameter_names[0], value=raw_value),
            )

        return self.client.estimate_cost(parameter_values)


def main():
    config_path = sys.argv[0]
    with open(config_path) as f:
        config = json.load(f)

    print(config)

    parameters = config['parameters']
    dimensions = len(parameters)

    var_lower = np.zeros(shape=(dimensions,))
    var_upper = np.zeros(shape=(dimensions,))
    var_types = np.zeros(shape=(dimensions,))
    for i, param in enumerate(parameters):
        var_lower[i] = param['bound']['from']
        var_upper[i] = param['bound']['to']
        var_types[i] = 'I'

    logger = logging.getLogger('plecoptera')
    client = Client(logger, config['endpoint'])
    estimator = Estimator(client)

    bb = rbfopt.RbfoptUserBlackBox(
        dimensions, var_lower, var_upper, var_types, estimator.cost_function)

    settings = rbfopt.RbfoptSettings(max_evaluations=10)
    alg = rbfopt.RbfoptAlgorithm(settings, bb)
    val, x, itercount, evalcount, fast_evalcount = alg.optimize()

    print(val, x, itercount, evalcount, fast_evalcount)


if __name__ == "__main__":
    main()
