from src.logs.types import LogFile
from src.heuristics.types import Heuristic
from src.heuristics.random import RandomHeuristic
from src.heuristics.histogram import HistogramHeuristic

HEURISTICS: list[tuple[str, Heuristic]]= [
    ("Histogram", HistogramHeuristic)
]

def apply_heuristics(grand_truth: LogFile, checked: LogFile):
    for name, heuristic_type in HEURISTICS:
        heuristic = heuristic_type()
        heuristic.load_grand_truth(grand_truth)
        heuristic.calculate_heuristic(name, checked)
