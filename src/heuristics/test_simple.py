from io import StringIO

from src.logs.types import LogFile
from src.heuristics.simple import SimpleHeuristic


def test_simple_heuristic():
    mocked_grand_truth = LogFile(
        StringIO(
            """
    1 : Warning test is a test
    2 : Thank you, next
    3 : Thank you, next
    """.strip()
        )
    )

    mocked_checked = LogFile(
        StringIO(
            """
    1 : Warning test is not a test
    2 : Error - What ?
    3 : Thank you, next
    """.strip()
        )
    )

    h = SimpleHeuristic()
    h.load_grand_truth(mocked_grand_truth)
    h.calculate_heuristic("test", mocked_checked)

    assert len(mocked_checked.lines) == 3
    assert not mocked_checked.lines[0].has_heuristic("test")
    assert mocked_checked.lines[1].has_heuristic("test")
