import logging

from src.logs.types import LogFile
from src.heuristics.types import Heuristic

logger = logging.getLogger("logging_heuristic")

class TimelineHeuristic(Heuristic):
    def __init__(self) -> None:
        self.grand_truth = None
        self.grand_truth_starting_time = None

    def load_grand_truth(self, grand_truth: LogFile):
        first_line = grand_truth.lines[0]

        if not first_line.has_timestamp():
            logger.error("First log line is missing timestamp")
            logger.info("Timeline heuristic will be disabled")
            return

        self.grand_truth = grand_truth
        self.grand_truth_starting_time = first_line.timestamp

    def calculate_heuristic(self, heuristic_name: str, checked: LogFile):
        if self.grand_truth is None:
            logger.warning("No grand truth file !")
            return

        checked_first_line = checked.lines[0]
        if not checked_first_line.has_timestamp():
            logger.error("First log line is missing timestamp")
            logger.info("Timeline heuristic will be disabled")
            return

        checked_starting_time = checked_first_line.timestamp

        
