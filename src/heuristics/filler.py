import logging
from dataclasses import dataclass

from src.logs.types import LogFile, LogLine
from src.heuristics.types import Heuristic
from src.heuristics.histogram_time import TimeHeuristicMetadata, TimeHeuristic

logger = logging.getLogger("filler_heuristic")

BIG_DIFF_N = 11


@dataclass
class FillerMetadata:
    connected_lines: list[LogLine]


class FillerHeuristic(Heuristic):
    def get_heuristic_name(self) -> str:
        return "Filler Heuristic"

    def load_grand_truth(self, grand_truth: LogFile):
        self.grand_truth = grand_truth

    def calculate_heuristic(self, checked: LogFile):
        if self.grand_truth is None:
            logger.warning("No grand truth file !")
            return

        heuristic_name = self.get_heuristic_name()
        time_heuristic_name = TimeHeuristic().get_heuristic_name()

        busy_lines = set()  # Lines which are connected by time histogram heuristic
        free_lines = {line: [] for line in checked.lines}

        for line in checked.lines:
            if line.has_heuristic(time_heuristic_name):
                try:
                    meta = line.get_heuristic_metadata(
                        time_heuristic_name, TimeHeuristicMetadata
                    )
                    if meta.connected_line is not None:
                        busy_lines.add(meta.connected_line.line_number)
                        continue
                except TypeError:
                    continue

        for line in self.grand_truth.lines:
            if line.line_number in busy_lines:
                continue

            closest_line = checked.find_closest_line_by_relative_timestamp(
                line.timestamp.get_relative_numeric_value(
                    self.grand_truth.starting_time
                )
            )
            free_lines[closest_line].append(line)

        for line in checked.lines:
            closest_lines = free_lines[line]
            h = min(1.0, (len(closest_lines) / BIG_DIFF_N))
            line.add_heuristic(heuristic_name, h, FillerMetadata(closest_lines))
