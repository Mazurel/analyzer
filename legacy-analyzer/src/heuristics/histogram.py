from typing import Dict

from src.logs.types import LogFile
from src.heuristics.types import Heuristic

MAGIC_CONSTANT = 0.001


class HistogramHeuristic(Heuristic):
    def get_heuristic_name(self) -> str:
        return "Histogram"

    def load_grand_truth(self, grand_truth: LogFile):
        self.grand_truth_templates_count: Dict[int, int] = {}

        for line in grand_truth.lines:
            t = line.template
            self.grand_truth_templates_count[t.id] = (
                self.grand_truth_templates_count.get(t.id, 0) + 1
            )

    def calculate_heuristic(self, checked: LogFile):
        heuristic_name = self.get_heuristic_name()

        templates_count: Dict[int, int] = {}
        for line in checked.lines:
            t = line.template
            templates_count[t.id] = templates_count.get(t.id, 0) + 1

        templates_amount: int = (
            max(
                max(self.grand_truth_templates_count.keys()),
                max(templates_count.keys()),
            )
            + 1
        )

        templates_difference = {
            template_id: abs(
                self.grand_truth_templates_count.get(template_id, 0)
                - templates_count.get(template_id, 0)
            )
            / float(
                self.grand_truth_templates_count.get(template_id, 0)
                + templates_count.get(template_id, 0)
                + 1
            )
            for template_id in range(templates_amount)
        }

        max_pred = max(1, max(templates_difference.values()) + MAGIC_CONSTANT)
        min_pred = max(0, min(templates_difference.values()) - MAGIC_CONSTANT)

        heuristic_per_template = {
            i: (v - min_pred) / (max_pred - min_pred)
            for i, v in templates_difference.items()
        }

        for log_line in checked.lines:
            log_line.add_heuristic(
                heuristic_name, heuristic_per_template[log_line.template.id]
            )
