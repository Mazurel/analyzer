from src.logs.types import LogFile
from src.heuristics.types import Heuristic
from src.heuristics.histogram import HistogramHeuristic

HEURISTICS: list[tuple[str, Heuristic]] = [("Histogram", HistogramHeuristic())]


def apply_heuristics(grand_truth: LogFile, checked: LogFile):
    grand_truth.clear_heuristics()
    checked.clear_heuristics()
    for name, heuristic in HEURISTICS:
        heuristic.load_grand_truth(grand_truth)
        heuristic.calculate_heuristic(name, checked)
