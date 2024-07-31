from pathlib import Path
from subprocess import Popen


def run_parser(log_file_path: Path, output_file_path: Path):
    assert log_file_path.exists(), f"File {log_file_path} does not exists"
    assert not output_file_path.exists(), f"File {output_file_path} exists (it should not !)"

    args = [
        "./gradlew",
        "benchmark:run",
        f"--args=\"if={log_file_path.as_posix()} of={output_file_path.as_posix()}\""
    ]
    stdout, stderr = Popen(args, executable="bash").communicate()


if __name__ == "__main__":
    run_parser(Path("../legacy-analyzer/sample-logs/log1.txt"), Path("../log_structured.txt"))

