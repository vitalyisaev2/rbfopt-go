from dataclasses import dataclass

Cost = float


@dataclass
class ParameterValue:
    name: str
    value: int