import textwrap
import os
from typing import Any
from pathlib import Path
import json

PARSER_NAMES = ["DICT", "DRAIN"]

def load_benchmark_results(path: Path):
    all_lines = path.read_text().splitlines()
    all_json_documents = [json.loads(line) for line in all_lines]

    results_per_parser: dict[str, list[dict]] = {
        parser_name: []
        for parser_name in PARSER_NAMES
    }

    for json_document in all_json_documents:
        parser_name = str(json_document["parser"])

        results_per_parser[parser_name].append({
            key: json_document[key]
            for key in json_document.keys()
            if key != "parser"
        })

    all_dataset_names: list[str] = [
        subresult["dataset"]
        for subresult in results_per_parser[PARSER_NAMES[0]]
    ]
    actual_results = {
        dataset_name: {}
        for dataset_name in all_dataset_names
    }

    for parser_name in PARSER_NAMES:
        for subresult in results_per_parser[parser_name]:
            dataset_name = subresult["dataset"]
            subresult_copy = { **subresult }
            del subresult_copy["dataset"]
            actual_results[dataset_name][parser_name] = subresult_copy

    return actual_results

def get_dataset_names(results) -> list[str]:
    return list(results.keys())

def into_table(dataset_name: str, results: dict[str, dict[str, Any]]) -> str:
    def format_field(obj: object):
        return f"\\texttt{{{str(obj)}}}"

    heading_fields = ["parser"] + list(results[PARSER_NAMES[0]].keys())
    tabular_env_setting = " c " * len(heading_fields)
    tex_heading = " & ".join([field.replace("_", "\\_") for field in heading_fields])

    table_content = ""
    for parser_name in PARSER_NAMES:
        table_content += f"\\textbf{{{parser_name}}} & "
        parser_results = results[parser_name]
        table_content += " & ".join([format_field(parser_results[field_name]) for field_name in heading_fields if field_name != "parser"])
        table_content += "\\\\\n\\hline\n"

    return textwrap.dedent(f"""
\\begin{{table}}[H]
\\begin{{center}}
\\begin{{tabular}}{{|{tabular_env_setting}|}}
\\hline
{tex_heading} \\\\ [0.5ex]
\\hline\\hline
{table_content.strip()}
\\end{{tabular}}
\\caption{{Wyniki jakościowe dla zbioru danych {dataset_name}}}
\\end{{center}}
\\end{{table}}
    """)

if __name__ == "__main__":
    dir_path = Path(os.path.dirname(__file__)).absolute()

    all_benchmark_results = load_benchmark_results(Path(
        dir_path / "benchmark_result.txt"
    ))
    all_dataset_names = get_dataset_names(all_benchmark_results)

    with open(dir_path / "tables.tex", "w") as f:
        for dataset_name in all_dataset_names:
            print(into_table(dataset_name, all_benchmark_results[dataset_name]), file=f)
