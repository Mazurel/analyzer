from io import StringIO

from src.logs.types import LogFile, LogLine, extract_timestamp

import pytest

def test_logfile():
    sample_file = StringIO(
    '''
    Line1
    Line2
    Line3
    '''.strip())

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

def test_extract_timestamp():
    assert extract_timestamp("16 test 123 abc") is not None
    def check_timestamp(stamp: str):
        result = extract_timestamp(stamp)
        print(f"{stamp} -> {result}")
        assert result is not None, f"Timestamp '{stamp}' was not properly extracted"

    hadoop_style = "2015-10-17 15:37:56,547"
    apache_style = "[Thu Jun 09 06:07:04 2005]"
    android_style = "12-17 19:31:36.263"
    linux_style = "[    0.000000]"

    check_timestamp(hadoop_style)
    check_timestamp(apache_style)
    check_timestamp(android_style)
    check_timestamp(linux_style)

def test_timestamp():
    line_with_timestamp = LogLine("21 - test")
    line_without_timestamp = LogLine("test")

    assert line_with_timestamp.timestamp, "Timestamp should be set"

    with pytest.raises(ValueError):
        line_without_timestamp.timestamp

