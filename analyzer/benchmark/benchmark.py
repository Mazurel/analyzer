from pathlib import Path
from subprocess import Popen

import evaluator

def run_parser(log_file_path: Path, output_file_path: Path):
    args = [
        "bash",
        "-c",
        f"./gradlew benchmark:run --args=\"--input_file {log_file_path.as_posix()} --output_file {output_file_path.as_posix()}\"",
    ]
    stdout, stderr = Popen(args, cwd=".").communicate()

if __name__ == "__main__":
    # TODO: List all of datasets, run evaluator, handle error:
    # pandas.errors.ParserError: Error tokenizing data. C error: Expected 5 fields in line 4, saw 7
    input_file = Path("benchmark/data/loghub_2k_corrected/Android/Android_2k.log").resolve().absolute()
    grand_truth_file = Path("benchmark/data/loghub_2k_corrected/Android/Android_2k.log_structured.csv").resolve().absolute()
    predicted_file = Path("benchmark/data/loghub_2k_corrected/Android/Android_2k.predicted.csv").resolve().absolute()
    input_file = Path("benchmark/data/loghub_2k/Apache/Apache_2k.log").resolve().absolute()
    grand_truth_file = Path("benchmark/data/loghub_2k/Apache/Apache_2k.log_structured.csv").resolve().absolute()
    predicted_file = Path("benchmark/data/loghub_2k/Apache/Apache_2k.predicted.csv").resolve().absolute()
    input_file = Path("benchmark/data/loghub_2k/Hadoop/Hadoop_2k.log").resolve().absolute()
    grand_truth_file = Path("benchmark/data/loghub_2k/Hadoop/Hadoop_2k.log_structured.csv").resolve().absolute()
    predicted_file = Path("benchmark/data/loghub_2k/Hadoop/Hadoop_2k.predicted.csv").resolve().absolute()
    run_parser(Path(input_file), Path(predicted_file))
    res = evaluator.evaluate(grand_truth_file, predicted_file)
    print(f"Result -> {res}")
