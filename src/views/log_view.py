from dataclasses import dataclass

from src.logs.drain import DrainManager
from src.heuristics import manager as heuristics
from src.views import View, HeuristicSetup, SelectFiles

from nicegui import ui
from nicegui.element import Element
from nicegui.tailwind_types.text_color import TextColor


@dataclass
class LogView(View):
    heuristic_setup: HeuristicSetup
    select_files: SelectFiles

    def update_log_visualization(self, container: Element):
        container.tailwind.padding("p-5").container().box_shadow(
            "inner"
        ).background_color("zinc-300").min_height("max")

        if self.select_files.state == SelectFiles.State.FILES_NOT_UPLOADED:
            self._show_logs_not_loaded(container)
            return

        assert (
            self.select_files.grand_truth is not None
            and self.select_files.checked is not None
        )

        # Apply drain
        # TODO: this will need to be abstracted away int the futuer
        drain = DrainManager()
        drain.learn(self.select_files.grand_truth)
        drain.learn(self.select_files.checked)
        drain.annotate(self.select_files.grand_truth)
        drain.annotate(self.select_files.checked)
        heuristics.apply_heuristics(
            self.select_files.grand_truth, self.select_files.checked
        )
        self._show_logs(container)

    def _show_logs_not_loaded(self, log_view: Element):
        ui.label("Please provide files above to see logs here !").tailwind.text_align(
            "center"
        ).width("full").font_size("lg")

    def _show_logs(self, log_view: Element):
        COLORS: list[TextColor] = [
            "neutral-500",
            "neutral-500",
            "green-500",
            "green-600",
        ]

        assert self.select_files.checked is not None

        for i, line in enumerate(self.select_files.checked.lines):
            val = 0
            for heuristic in line.list_heuristics():
                val = max(val, line.get_heuristic(heuristic))

            if val < self.heuristic_setup.heuristic_cap:
                continue

            color = COLORS[int(len(COLORS) * val)]

            lbl = ui.label(f"{i + 1}: {line.line}")
            lbl.tailwind.font_family("mono").user_select("none").text_overflow(
                "text-clip"
            ).text_color(color)
            lbl.classes(add="hover:font-bold")
            with lbl:
                tooltip_text = [
                    f"Template: {line.template.pattern}",
                ]
                tooltip_text += [
                    f"{heuristic}: {line.get_heuristic(heuristic)}"
                    for heuristic in line.list_heuristics()
                ]
                ui.tooltip("\n".join(tooltip_text)).tailwind.font_size(
                    "base"
                ).font_family("mono").whitespace("pre-line")

    def show(self, container: Element):
        self.parent = container
        self.heuristic_setup.state_changed.connect(self.update, weak=False)
        self.select_files.state_changed.connect(self.update, weak=False)
        self.update_log_visualization(container)

    def update(self, sender: object = None):
        self.parent.clear()
        with self.parent:
            self.update_log_visualization(self.parent)
