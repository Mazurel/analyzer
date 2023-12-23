import logging
from typing_extensions import deprecated

from src.logs.types import LogFile
from src.heuristics.types import Heuristic
from src.heuristics.simple import SimpleHeuristic
from src.heuristics.histogram_time import TimeHeuristic
from src.heuristics.filler import FillerHeuristic

HEURISTICS: list[Heuristic] = [
    SimpleHeuristic(),
    TimeHeuristic(),
    FillerHeuristic(),  # This heuristic should be the last one !
]

logger = logging.getLogger("heuristics_manager")


def apply_heuristics(grand_truth: LogFile, checked: LogFile):
    grand_truth.clear_heuristics()
    checked.clear_heuristics()
    for heuristic in HEURISTICS:
        heuristic.load_grand_truth(grand_truth)
        heuristic.calculate_heuristic(checked)
        logger.info(f"Applied heuristic: {heuristic.get_heuristic_name()}")
    logger.info("All heuristics applied !")


@deprecated("You should use `<heuristic>.get_heuristic_name()` instead")
def query_heuristic_name(t: type):
    for instance in HEURISTICS:
        if type(instance) is t:
            return instance.get_heuristic_name()

    raise TypeError(f"Unknown heuristic type: {t}")
