import logging

from src.logs.types import LogFile
from src.heuristics.types import Heuristic
from src.heuristics.histogram import HistogramHeuristic
from src.heuristics.simple import SimpleHeuristic

HEURISTICS: list[tuple[str, Heuristic]] = [
    ("Simple", SimpleHeuristic()),
    ("Histogram", HistogramHeuristic())
]

logger = logging.getLogger("heuristics_manager")


def apply_heuristics(grand_truth: LogFile, checked: LogFile):
    grand_truth.clear_heuristics()
    checked.clear_heuristics()
    for name, heuristic in HEURISTICS:
        heuristic.load_grand_truth(grand_truth)
        heuristic.calculate_heuristic(name, checked)
        logger.info(f"Applying heuristic: {name}")
