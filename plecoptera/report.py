from dataclasses import dataclass
from typing import List

from plecoptera.aliases import Cost
from plecoptera.parameters import ParameterValue


@dataclass
class Report:
    cost: Cost
    optimum: List[ParameterValue]
    iterations: int
    evaluations: int
    fast_evaluations: int