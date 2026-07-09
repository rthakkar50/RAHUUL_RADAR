from dataclasses import dataclass
from enum import Enum
from typing import Any, List

class FilterOperator(Enum):
    GREATER_THAN = ">"
    LESS_THAN = "<"
    EQUAL = "=="
    GREATER_EQUAL = ">="
    LESS_EQUAL = "<="
    CROSS_ABOVE = "CROSS_ABOVE"
    CROSS_BELOW = "CROSS_BELOW"
    CONTAINS = "CONTAINS"

@dataclass
class FilterCondition:
    field: str
    operator: FilterOperator
    value: Any

@dataclass
class ScannerProfile:
    name: str
    description: str
    conditions: List[FilterCondition]
