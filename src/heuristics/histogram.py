from src.logs.types import LogFile
from src.heuristics.types import Heuristic

MAGIC_CONSTANT = 0.001

class HistogramHeuristic(Heuristic):
    def load_grand_truth(self, grand_truth: LogFile):
        self.clusters = {}

        for line in grand_truth.lines:
            t = line.template
            self.clusters[t.id] = self.clusters.get(t.id, 0) + 1

    def calculate_heuristic(self, heuristic_name: str, checked: LogFile):
        checked_clusters = {}
        for line in checked.lines:
            t = line.template
            checked_clusters[t.id] = checked_clusters.get(t.id, 0) + 1

        cluster_amount = (
            max(max(self.clusters.keys()), max(checked_clusters.keys())) + 1
        )

        clusters_difference = {
            cluster_id: abs(
                self.clusters.get(cluster_id, 0) - checked_clusters.get(cluster_id, 0)
            )
            / float(
                self.clusters.get(cluster_id, 0)
                + checked_clusters.get(cluster_id, 0)
                + 1
            )
            for cluster_id in range(cluster_amount)
        }

        max_pred = max(1, max(clusters_difference.values()) + MAGIC_CONSTANT)
        min_pred = max(0, min(clusters_difference.values()) - MAGIC_CONSTANT)

        clusters_difference = {
            i: (v - min_pred) / (max_pred - min_pred)
            for i, v in clusters_difference.items()
        }

        for log_line in checked.lines:
            log_line.add_heuristic(
                heuristic_name, clusters_difference[log_line.template.id]
            )
