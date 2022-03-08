from http import HTTPStatus
from typing import List
from urllib.parse import urljoin

import jsons
import requests

from wrapper.types import Cost, ParameterValue
from wrapper.report import Report
import wrapper.names as names


class Client:
    url_head: str
    session: requests.Session

    def __init__(self, endpoint: str):
        self.url_head = f'http://{endpoint}'
        self.session = requests.Session()

    def estimate_cost(self, parameter_values: List[ParameterValue]) -> (Cost, bool):
        print(f"request '{parameter_values}'")

        payload = dict(parameter_values=parameter_values)
        response = self.session.get(
            urljoin(self.url_head, 'estimate_cost'),
            json=jsons.dump(payload),
        )

        print(f"response code={response.status_code} body={response.json()}")

        if response.status_code != HTTPStatus.OK:
            raise ValueError(f'invalid status code {response.status_code}')
        else:
            return response.json()[names.Cost], response.json()[names.InvalidParameterCombination]

    def register_report(self, report: Report):
        print(f"request '{report}'")

        payload = dict(report=report)
        response = self.session.post(
            urljoin(self.url_head, 'register_report'),
            json=jsons.dump(payload),
        )

        print(f"response code={response.status_code} response={response}")

        if response.status_code != HTTPStatus.OK:
            raise ValueError(f'invalid status code {response.status_code}')