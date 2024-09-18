from pathlib import Path
from subprocess import PIPE, Popen
import os
from dataclasses import dataclass
import traceback
from enum import Enum, IntEnum
import textwrap
import json
import math

import pandas

import evaluator

LOGHUB_PATH = Path(os.path.dirname(__file__)) / "data/loghub_2k"
BENCHMARK_BIN_PATH = Path(os.path.dirname(__file__)) / "build/libs/console-frontend-1.0.jar"


class ParserType(Enum):
    DICT = "DICT"
    DRAIN = "DRAIN"


class ParserExitCode(IntEnum):
  TIMESTAMP_FOUND = 0
  TIMESTAMP_NOT_FOUND = 1
  INTERNAL_ERROR = 2

  @staticmethod
  def from_exit_code(exit_code: int) -> "ParserExitCode":
      for name, associated_exit_code in ParserExitCode.__members__.items():
        if associated_exit_code == exit_code:
            return associated_exit_code
      raise RuntimeError(f"Unknown exit code: {exit_code}")

@dataclass
class Dataset:
    input_file: Path
    grand_truth: Path
    dict_prediction_placeholder: Path
    drain_prediction_placeholder: Path

    def __post_init__(self):
        assert self.input_file.exists(), f"{self.input_file} should exist !"
        assert self.grand_truth.exists(), f"{self.grand_truth} should exist !"

def run_parser(log_file_path: Path, output_file_path: Path, parser: ParserType) -> ParserExitCode:
    args = [
        "java",
        "-jar",
        BENCHMARK_BIN_PATH,
        log_file_path.as_posix(),
        output_file_path.as_posix(),
        parser.value
    ]
    parser_process = Popen(args, cwd=".", stdout=PIPE, stderr=PIPE)
    stdout, stderr = parser_process.communicate()
    output = textwrap.dedent(f"""
        PARSER LOGS
        {stdout.decode()}{stderr.decode()}
        END PARSER LOGS
    """)
    print(output, file=sys.stderr, flush=True, end="")
    return ParserExitCode.from_exit_code(parser_process.returncode)

def load_datasets(dataset_names: list[str]):
    resulting_datasets = {}
    for dataset_name in dataset_names:
        if not os.path.isdir(Path(LOGHUB_PATH) / dataset_name):
            continue
        yield dataset_name, Dataset(
            input_file=Path(LOGHUB_PATH) / dataset_name / f"{dataset_name}_2k.log",
            grand_truth=Path(LOGHUB_PATH) / dataset_name / f"{dataset_name}_2k.log_structured.csv",
            dict_prediction_placeholder=Path(LOGHUB_PATH) / dataset_name / f"{dataset_name}_2k.predicted.dict.csv",
            drain_prediction_placeholder=Path(LOGHUB_PATH) / dataset_name / f"{dataset_name}_2k.predicted.drain.csv",
        )
    return resulting_datasets

def report_result(parser_type: ParserType, was_timestamp_extracted: bool, dataset_name: str, grand_truth: Path, prediction_path: Path):
    def clean_float(num: object) -> str:
        assert isinstance(num, float), "Float from evaluation is not correct"
        return str(round(float(num), 4))

    precission, recall, f_score, accuracy = evaluator.evaluate(grand_truth, prediction_path)
    print(json.dumps({
        "parser": parser_type.value,
        "dataset": dataset_name,
        "precission": clean_float(precission),
        "recall": clean_float(recall),
        "f_score": clean_float(f_score),
        "accuracy": clean_float(accuracy),
        "timestamp_extracted": was_timestamp_extracted
    }), flush=True)

if __name__ == "__main__":
    import sys

    for dataset_name, dataset in load_datasets(sys.argv[0:]):
        dict_exit_code = run_parser(dataset.input_file, dataset.dict_prediction_placeholder, ParserType.DICT)
        drain_exit_code = run_parser(dataset.input_file, dataset.drain_prediction_placeholder, ParserType.DRAIN)
        report_result(
            ParserType.DICT,
            dict_exit_code == ParserExitCode.TIMESTAMP_FOUND,
            dataset_name,
            dataset.grand_truth,
            dataset.dict_prediction_placeholder
        )
        report_result(
            ParserType.DRAIN,
            drain_exit_code == ParserExitCode.TIMESTAMP_FOUND,
            dataset_name,
            dataset.grand_truth,
            dataset.drain_prediction_placeholder
        )
