from src.logs.timestamp import extract_timestamp

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

    print()
    print("=== Timestamp test ===")
    check_timestamp(hadoop_style)
    check_timestamp(apache_style)
    check_timestamp(android_style)
    check_timestamp(linux_style)
    print("======")
