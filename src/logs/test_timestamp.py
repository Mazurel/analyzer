from src.logs.timestamp import _subdivide_str, extract


def test_timestamp_subdivisions():
    assert _subdivide_str("test a b c") == [
        "test a b c",
        "test a b",
        "test a",
        "test",
    ]


def test_extract_timestamp():
    assert extract("16 test 123 abc") is not None
    log_message = "Random 23.12.2023 log message"

    assert extract("Test1") is None

    def check_timestamp(stamp: str):
        line = stamp + " " + log_message
        result = extract(line)
        print(f"{line} -> {result}")
        assert result is not None, f"Timestamp '{stamp}' was not properly extracted"
        assert result[0] == log_message, "Timestamp should be extracted at proper place"

    hadoop_style_timestamp = "2015-10-17 15:37:56,547"
    hadoop_style_timestamp2 = "2015-10-17 18:09:30,830"
    apache_style_timestamp = "[Thu Jun 09 06:07:04 2005]"
    android_style_timestamp = "12-17 19:31:36.263"
    linux_style_timestamp = "[    0.000000]"

    check_timestamp(hadoop_style_timestamp)
    check_timestamp(hadoop_style_timestamp2)
    check_timestamp(apache_style_timestamp)
    # check_timestamp(android_style_timestamp) TODO: Support android style timestamps
    check_timestamp(linux_style_timestamp)


def test_specfific_log_lines_timestamps():
    r = extract(
        "2015-10-17 18:09:30,830 INFO [main] org.apache.hadoop.mapred.YarnChild: Executing with tokens:"
    )

    assert r is not None, "There is a timestamp in the log line"
    _, t = r
    assert t.representation == "2015-10-17 18:09:30,830"
