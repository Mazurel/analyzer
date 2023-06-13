from typing import Protocol

from src.logs.types import LogFile


class Heuristic(Protocol):
    def load_grand_truth(self, grand_truth: LogFile):
        ...

    def calculate_heuristic(self, heuristic_name: str, checked: LogFile):
        ...
