import random

from src.logs.types import LogFile
from src.heuristics.types import Heuristic

class RandomHeuristic(Heuristic):
    def load_grand_truth(self, grand_truth: LogFile):
        pass
    
    def calculate_heuristic(self, heuristic_name: str, checked: LogFile):
        for log_line in checked.lines:
            log_line.add_heuristic(heuristic_name, random.random())
