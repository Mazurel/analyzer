from pathlib import Path
from subprocess import Popen
import os
from dataclasses import dataclass
import traceback

import pandas

import evaluator

LOGHUB_PATH = Path(os.path.dirname(__file__)) / "data/loghub_2k"
BENCHMARK_BIN_PATH = Path(os.path.dirname(__file__)) / "build/libs/console-frontend-1.0.jar"


@dataclass
class Dataset:
    input_file: Path
    grand_truth: Path
    prediction_placeholder: Path

    def __post_init__(self):
        assert self.input_file.exists(), f"{self.input_file} should exist !"
        assert self.grand_truth.exists(), f"{self.grand_truth} should exist !"

def run_parser(log_file_path: Path, output_file_path: Path):
    args = [
        "java",
        "-jar",
        BENCHMARK_BIN_PATH,
        "--input_file",
        log_file_path.as_posix(),
        "--output_file",
        output_file_path.as_posix(),
    ]
    stdout, stderr = Popen(args, cwd=".").communicate()

def load_datasets(dataset_names: list[str]):
    resulting_datasets = {}
    for dataset_name in dataset_names:
        if not os.path.isdir(Path(LOGHUB_PATH) / dataset_name):
            continue
        yield dataset_name, Dataset(
            input_file=Path(LOGHUB_PATH) / dataset_name / f"{dataset_name}_2k.log",
            grand_truth=Path(LOGHUB_PATH) / dataset_name / f"{dataset_name}_2k.log_structured.csv",
            prediction_placeholder=Path(LOGHUB_PATH) / dataset_name / f"{dataset_name}_2k.predicted.csv",
        )
    return resulting_datasets

if __name__ == "__main__":
    import sys

    for dataset_name, dataset in load_datasets(sys.argv[0:]):
        print(f"Testing dataset: {dataset_name}", flush=True)
        run_parser(dataset.input_file, dataset.prediction_placeholder)
        try:
            res = evaluator.evaluate(dataset.grand_truth, dataset.prediction_placeholder)
        except pandas.errors.ParserError as err:
            traceback.print_exception(err)
            print(f"Skipping because: {err}", flush=True)
            continue
        except FileNotFoundError as err:
            traceback.print_exception(err)
            print(f"Skipping because: {err}", flush=True)
            continue

    # TODO: List all of datasets, run evaluator, handle error:
    # pandas.errors.ParserError: Error tokenizing data. C error: Expected 5 fields in line 4, saw 7
