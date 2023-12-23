import random

from src.logs.types import LogFile
from src.heuristics.types import Heuristic


class RandomHeuristic(Heuristic):
    def get_heuristic_name(self) -> str:
        return "Random"

    def load_grand_truth(self, grand_truth: LogFile):
        pass

    def calculate_heuristic(self, checked: LogFile):
        heuristic_name = self.get_heuristic_name()
        for log_line in checked.lines:
            log_line.add_heuristic(heuristic_name, random.random())
