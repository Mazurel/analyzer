from typing import Dict, List, Tuple, Optional
import logging
from dataclasses import dataclass

from src.logs.types import LogFile, LogLine, NoTimestampException
from src.heuristics.types import Heuristic

import numpy as np
from numpy import typing as npt
from scipy import optimize


log = logging.getLogger("TimeHeuristic")
NUMERICAL_STABILITY_CONSTANT = 1e-4
DT_PERC = 0.5


@dataclass
class TimeHeuristicMetadata:
    connected_line: Optional[LogLine] = None


class TimeHeuristic(Heuristic):
    def load_grand_truth(self, grand_truth: LogFile):
        self.grand_truth_template_per_line: Dict[int, List[LogLine]] = {}
        self.grand_truth_starting_time: Optional[float] = None
        try:
            t = grand_truth.lines[0].timestamp.get_numeric_value()
            self.grand_truth_starting_time = t
        except NoTimestampException:
            return

        for line in grand_truth.lines:
            a = self.grand_truth_template_per_line.get(line.template.id, [])
            a.append(line)
            self.grand_truth_template_per_line[line.template.id] = a

        self.grand_truth = grand_truth

    def calculate_dt(self, checked: LogLine, truth: LogLine) -> float:
        assert self.checked_starting_time is not None
        assert self.grand_truth_starting_time is not None

        t1 = checked.timestamp.get_numeric_value() - self.checked_starting_time
        t2 = truth.timestamp.get_numeric_value() - self.grand_truth_starting_time
        v = abs(t1 - t2)
        return v

    def collect_template_associations(
        self, all_template_ids: set[int], grand_truth: LogFile, checked: LogFile
    ) -> Dict[int, Tuple[List[LogLine], List[LogLine]]]:
        """
        For both grand truth and checked files, create dictionary that
        for each template ID, stores tuple of two lists:
        - list of lines with that template ID inside checked file
        - list of lines with that template ID inside grand truth file
        """
        res = {i: ([], []) for i in all_template_ids}

        for checked_l in checked.lines:
            checked_lines, _ = res[checked_l.template.id]
            checked_lines.append(checked_l)

        for truth_l in grand_truth.lines:
            _, truth_lines = res[truth_l.template.id]
            truth_lines.append(truth_l)

        return res

    def calculate_heuristic(self, heuristic_name: str, checked: LogFile):
        if self.grand_truth_starting_time is None:
            return

        try:
            self.checked_starting_time = checked.lines[0].timestamp.get_numeric_value()
            self.checked_ending_time = checked.lines[-1].timestamp.get_numeric_value()
            self.max_dt = self.checked_ending_time - self.checked_starting_time
        except NoTimestampException:
            return

        all_template_ids = set(checked.get_all_template_ids()) | set(
            self.grand_truth_template_per_line.keys()
        )
        template_assocs = self.collect_template_associations(
            all_template_ids, self.grand_truth, checked
        )

        for template_id in all_template_ids:
            try:
                checked_lines, truth_lines = template_assocs[template_id]
                n = len(checked_lines)
                m = len(truth_lines)
                log_dispropotion = abs(n - m) / abs(n + m + 1)

                if n == 0:
                    continue
                elif m == 0:
                    for l in checked_lines:
                        l.add_heuristic(heuristic_name, log_dispropotion)

                dts = np.zeros((max(n, m), max(n, m)))
                for i in range(n):
                    for j in range(m):
                        dt = self.calculate_dt(checked_lines[i], truth_lines[j])
                        dts[i, j] = dt

                alg_input = dts / (DT_PERC * self.max_dt + NUMERICAL_STABILITY_CONSTANT)
                res: Tuple[
                    npt.NDArray[np.int_], npt.NDArray[np.int_]
                ] = optimize.linear_sum_assignment(alg_input)

                if (i, j) in zip(iter(res[0]), iter(res[1])):
                    if i >= n or j >= m:
                        checked_lines[i].add_heuristic(
                            heuristic_name, log_dispropotion, TimeHeuristicMetadata()
                        )
                    else:
                        checked_lines[i].add_heuristic(
                            heuristic_name,
                            max(0, min(1, alg_input[i, j])),
                            TimeHeuristicMetadata(truth_lines[j]),
                        )
            except NoTimestampException:
                log.info("Skipping ...")
                continue
