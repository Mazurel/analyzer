from io import StringIO
from math import floor

from src.logs.types import LogFile, LogLine
from src.logs.timestamp import extract

import pytest


def test_logfile():
    sample_file = StringIO(
        """
    12:01 Line1
    12:02 Line2
    12:03 Line3
    """.strip()
    )

    log_file = LogFile(sample_file)
    assert len(log_file.lines) == 3, "There are 3 lines"

    first_line = log_file.lines[0]
    assert first_line.line == "12:01 Line1\n"
    assert first_line.line_without_timestamp == "Line1\n"
    assert first_line.line_number == 1

    assert log_file.lines[2].line_number == 3


def test_logline_heuristic():
    line = LogLine("test")

    line.add_heuristic("Sample", 0.5)
    assert line.get_heuristic("Sample") == 0.5, "It is possible to add heuristic"
    line.clear_heuristics()

    # There should be no heurisric now
    with pytest.raises(ValueError):
        line.get_heuristic("Sample")

    # Test line metadata
    line.add_heuristic("Sample", 0.5, {"x": 1})
    assert line.get_heuristic("Sample") == 0.5, "It is possible to add heuristic"

    # There should be no template initially
    with pytest.raises(TypeError):
        line.get_heuristic_metadata("Sample", int)


def test_logline_misc():
    line = LogLine("test")

    assert line.line == "test", "String is saved properly"

    # There should be no template initially
    with pytest.raises(ValueError):
        line.template


def test_timestamp():
    line_with_timestamp = LogLine("21 : test")
    line_without_timestamp = LogLine("test")

    extraction_result = extract(line_with_timestamp.line)
    assert extraction_result is not None, "Simple timestamp should be found"

    line_with_timestamp.set_timestamp(extraction_result)

    assert line_with_timestamp.timestamp, "Timestamp should be set"
    assert (
        floor(line_with_timestamp.timestamp.get_numeric_value()) == 21
    ), "Timestamp should be set"
    assert (
        line_with_timestamp.timestamp.get_date_value() is None
    ), "There should be no date"

    with pytest.raises(ValueError):
        line_without_timestamp.timestamp


def test_timestamp_normalization():
    file = LogFile(
        StringIO(
            """
    1 : a
    5 : b
    10 : c
    20 : d
    """.strip()
        )
    )

    second_line = file.lines[1]

    assert (
        floor(second_line.timestamp.get_relative_numeric_value(file.starting_time)) == 4
    )

    for l1, l2 in zip(file.lines[:-2], file.lines[1:]):
        assert l1.timestamp.get_relative_numeric_value(
            file.starting_time
        ) <= l2.timestamp.get_relative_numeric_value(file.starting_time)


def test_time_lookup():
    f1 = LogFile(
        StringIO(
            """
    1 : a
    5 : b
    10 : c
    20 : d
    """.strip()
        )
    )

    f2 = LogFile(
        StringIO(
            """
    23 : e
    30 : f
    31 : g
    40 : i
    """.strip()
        )
    )

    assert (
        f1.find_closest_line_by_relative_timestamp(
            f2.lines[1].timestamp.get_relative_numeric_value(f2.starting_time)
        )
        is f1.lines[2]
    )
