import logging

from src.logs.types import LogFile
from src.heuristics.types import Heuristic

logger = logging.getLogger("simple_heuristic")

# Keywords that describe how important log line may be
KEYWORDS = {
    "warning": 0.8,
    "warn": 0.8,
    "error": 1.0,
    "exception": 0.9,
    "traceback": 0.9,
}


class SimpleHeuristic(Heuristic):
    def load_grand_truth(self, grand_truth: LogFile):
        self.grand_truth = grand_truth

    def grand_truth_contains(self, keyword: str) -> bool:
        return any(keyword in line.line.lower() for line in self.grand_truth.lines)

    def calculate_heuristic(self, heuristic_name: str, checked: LogFile):
        if self.grand_truth is None:
            logger.warning("No grand truth file !")
            return

        for keyword, heuristic in KEYWORDS.items():
            if self.grand_truth_contains(keyword):
                continue

            for line in checked.lines:
                if keyword not in line.line.lower():
                    continue
                if (
                    line.has_heuristic(heuristic_name)
                    and line.get_heuristic(heuristic_name) > heuristic
                ):
                    continue
                line.add_heuristic(heuristic_name, heuristic)
