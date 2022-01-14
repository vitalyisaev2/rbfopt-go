from dataclasses import dataclass
from typing import List

from plecoptera.types import Cost, ParameterValue


@dataclass
class Report:
    cost: Cost
    optimum: List[ParameterValue]
    iterations: int
    evaluations: int
    fast_evaluations: int

    def optimum_argument(self, name: str) -> int:
        for pv in self.optimum:
            if pv.name == name:
                return pv.value

        raise ValueError(f"unexpected name {name}")