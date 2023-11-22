import logging

from src.logs.types import LogFile
from src.heuristics.types import Heuristic
from src.heuristics.simple import SimpleHeuristic
from src.heuristics.histogram_time import TimeHeuristic

HEURISTICS: list[tuple[str, Heuristic]] = [
    ("Simple", SimpleHeuristic()),
    ("Time Histogram", TimeHeuristic()),
]

logger = logging.getLogger("heuristics_manager")


def apply_heuristics(grand_truth: LogFile, checked: LogFile):
    grand_truth.clear_heuristics()
    checked.clear_heuristics()
    for name, heuristic in HEURISTICS:
        heuristic.load_grand_truth(grand_truth)
        heuristic.calculate_heuristic(name, checked)
        logger.info(f"Applied heuristic: {name}")
    logger.info("All heuristics applied !")
