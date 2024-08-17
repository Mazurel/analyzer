import difflib
from pathlib import Path
from subprocess import PIPE, Popen
import os
from dataclasses import dataclass
import traceback


TESTS_DIR = Path(os.path.dirname(__file__)) / "tests"
DIFFER_BIN_PATH = Path(os.path.dirname(__file__)) / "../differ/build/libs/differ-1.0.jar"


@dataclass
class TestCase:
    baseline_path: Path
    checked_path: Path
    expected_path: Path

    def __post_init__(self):
        assert self.baseline_path.exists(), f"{self.baseline_path} should exist !"
        assert self.checked_path.exists(), f"{self.checked_path} should exist !"
        assert self.expected_path.exists(), f"{self.expected_path} should exist !"

    @property
    def expected_result(self) -> str:
        return self.expected_path.read_text()

def run_differ(test_case: TestCase) -> str:
    args = [
        "java",
        "-jar",
        DIFFER_BIN_PATH.as_posix(),
        "-c",
        test_case.baseline_path.as_posix(),
        test_case.checked_path.as_posix(),
    ]
    print(" ".join(args), flush=True)
    stdout, stderr = Popen(args, cwd=".", stdout=PIPE, stderr=None).communicate()
    return stdout.decode()

def load_testcases(test_names: list[str]):
    for test_name in test_names:
        if not os.path.isdir(Path(TESTS_DIR) / test_name):
            continue
        yield test_name, TestCase(
            baseline_path=TESTS_DIR / test_name / "baseline.txt",
            checked_path=TESTS_DIR / test_name / "checked.txt",
            expected_path=TESTS_DIR / test_name / "expected.txt",
        )

if __name__ == "__main__":
    import sys

    for test_name, testcase in load_testcases(sys.argv[0:]):
        print(f"Testing: {test_name}", flush=True)
        differ_res = run_differ(testcase)
        expected_res = testcase.expected_result
        if differ_res != expected_res:
            print("FAILED", flush=True)
            print(f"==EXPECTED==\n{expected_res}", flush=True)
            print(f"==DIFFER==\n{differ_res}", flush=True)
            exit(1)
        else:
            print("PASS")
        # TODO: Use:
        # differences = difflib.SequenceMatcher(None, differ_res, expected_res)

    exit(0)
