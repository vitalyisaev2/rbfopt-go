from http import HTTPStatus
from typing import List
from urllib.parse import urljoin

import jsons
import requests

from plecoptera.aliases import Cost
from plecoptera.parameters import ParameterValue
from plecoptera.report import Report


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