from src.logs.types import extract_timestamp

def test_extract_timestamp():
    assert extract_timestamp("16 test 123 abc") is not None
    log_message = "Random 23.12.2023 log message"

    assert extract_timestamp("Test1") is None

    def check_timestamp(stamp: str):
        line = stamp + " " + log_message
        result = extract_timestamp(line)
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

