from typing import Protocol

from src.logs.types import LogFile


class Heuristic(Protocol):
    """
    Heuristic is interface that defines how to calculate some heuristic for log line.

    Heuristics specify how important given line of log file is, based on another
    "grand truth" file (maybe in the future multiple files).

    It specifies two methods:
    - `load_grand_truth` - This method is called when grand truth file is loaded.
                           This is where heuristic should recalculate cache for new
                           grand truth file.
    - `calculate_heuristic` - This method is called when new check file is loaded.
                              It should call `add_heuristic` on log lines where heuristic
                              is calulated.

    Notes:
    - Refer to `src.heuristics.random` for example how to implement heuristic.
    """

    def load_grand_truth(self, grand_truth: LogFile):
        ...

    def calculate_heuristic(self, heuristic_name: str, checked: LogFile):
        ...
