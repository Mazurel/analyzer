import os
from pathlib import Path

from test import TestCase, TESTS_DIR

def clean_description(description: str) -> str:
    return " ".join([desc_line.strip() for desc_line in description.split("\n")])

if __name__ == "__main__":
    all_tests = os.listdir(TESTS_DIR)

    lines = []
    for test_name in all_tests:
        testcase = TestCase.from_testname(test_name)
        line = rf"\texttt{{{test_name}}} & {clean_description(testcase.description)}"
        lines.append(line)

    print(rf"""
\begin{{table}}[H]
\centering
\begin{{tabular}}{{||p{{4cm}}|p{{8cm}}||}}
\hline \hline
Nazwa testu & Opis (po angielsku) \\ \hline \hline
{"\\\\ \\hline \n".join(lines)} \\ \hline \hline
\end{{tabular}}
\caption{{Tabela zestawiająca sprefabrykowane testy}}
\label{{tab:prefab-test-table}}
\end{{table}}
    """)
