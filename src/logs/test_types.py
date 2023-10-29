from io import StringIO

from src.logs.timestamp import TimestampExtractor
from src.logs.types import LogFile, LogLine

import pytest


def test_logfile():
    sample_file = StringIO(
        """
    Line1
    Line2
    Line3
    """.strip()
    )

    log_file = LogFile(sample_file)
    assert len(log_file.lines) == 3, "There are 3 lines"

    first_line = log_file.lines[0]
    assert first_line.line == "Line1\n"


def test_logline_heuristic():
    line = LogLine("test")

    assert line.line == "test", "String is saved properly"

    line.add_heuristic("Sample", 0.5)
    assert line.get_heuristic("Sample") == 0.5, "It is possible to add heuristic"
    line.clear_heuristics()

    # There should be no heurisric now
    with pytest.raises(ValueError):
        line.get_heuristic("Sample")

    # There should be no template initially
    with pytest.raises(ValueError):
        line.template


def test_timestamp():
    line_with_timestamp = LogLine("21 - test")
    line_without_timestamp = LogLine("test")

    line_with_timestamp.extract_timestamp(TimestampExtractor())

    assert line_with_timestamp.timestamp, "Timestamp should be set"

    with pytest.raises(ValueError):
        line_without_timestamp.timestamp
