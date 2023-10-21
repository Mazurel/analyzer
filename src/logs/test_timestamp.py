from src.logs.timestamp import TimestampExtractor

def test_timestamp_subdivisions():
    e = TimestampExtractor()
    assert e._subdivide_str("test a b c") == [
        "test a b c",
        "test a b",
        "test a",
        "test",
    ]

def test_extract_timestamp():
    e = TimestampExtractor()
    assert e.extract("16 test 123 abc") is not None
    log_message = "Random 23.12.2023 log message"

    assert e.extract("Test1") is None

    def check_timestamp(stamp: str):
        line = stamp + " " + log_message
        result = e.extract(line)
        print(f"{line} -> {result}")
        assert result is not None, f"Timestamp '{stamp}' was not properly extracted"
        assert result[0] == log_message, "Timestamp should be extracted at proper place"

    hadoop_style_timestamp = "2015-10-17 15:37:56,547"
    apache_style_timestamp = "[Thu Jun 09 06:07:04 2005]"
    android_style_timestamp = "12-17 19:31:36.263"
    linux_style_timestamp = "[    0.000000]"

    check_timestamp(hadoop_style_timestamp)
    check_timestamp(apache_style_timestamp)
    check_timestamp(android_style_timestamp)
    check_timestamp(linux_style_timestamp)

