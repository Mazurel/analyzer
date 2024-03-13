import sys
import pytest
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", dest="prints", action="store_true", help="Enable prints in all tests")
    args = parser.parse_args()

    pytest_args = [
        "--pyargs", "src"
    ]
    if args.prints:
        pytest_args.append("-s")

    sys.exit(pytest.main(pytest_args))
