from io import StringIO

from src.logs.types import LogFile
from src.heuristics.simple import SimpleHeuristic

def test_simple_heuristic():
    mocked_grand_truth = LogFile(StringIO("""
    Warning test is a test
    """.strip()))

    mocked_checked = LogFile(StringIO("""
    Warning test is not a test
    Error - What ?
    """.strip()))

    h = SimpleHeuristic()
    h.load_grand_truth(mocked_grand_truth)
    h.calculate_heuristic("test", mocked_checked)

    assert len(mocked_checked.lines) == 2
    assert not mocked_checked.lines[0].has_heuristic("test")
    assert mocked_checked.lines[1].has_heuristic("test")

