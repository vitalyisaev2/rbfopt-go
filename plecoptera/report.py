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

    def optimum_value(self, name: str) -> int:
        for pv in self.optimum:
            if pv.name == name:
                return pv.value

        raise ValueError(f"unexpected name {name}")