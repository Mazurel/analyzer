from dataclasses import dataclass
from functools import partial

from src.heuristics import manager as heuristics
from src.views import View, HeuristicSetup, SelectFiles, DrainSetup, LogView

from nicegui import ui
from nicegui.tailwind_types.text_color import TextColor


@dataclass
class SmartLogView(View):
    """
    This view is responsible for showing log files with their heurstics.
    It also allows interacting with log lines.
    """
    drain_setup: DrainSetup
    heuristic_setup: HeuristicSetup
    select_files: SelectFiles

    
    _drain_needs_calculation: bool = False

    def update_log_visualization(self):
        self.parent.tailwind.padding("p-5").container().box_shadow(
            "inner"
        ).background_color("zinc-300").min_height("max")

        if self.select_files.state == SelectFiles.State.FILES_NOT_UPLOADED:
            self._show_logs_not_loaded()
            return
        
        if self._drain_needs_calculation:
            self._recalculate_drain()

        self._show_logs()
    
    def _recalculate_drain(self):
        assert (
            self.select_files.grand_truth is not None
            and self.select_files.checked is not None
        )

        drain = self.drain_setup.build_drain()
        drain.learn(self.select_files.grand_truth)
        drain.learn(self.select_files.checked)
        drain.annotate(self.select_files.grand_truth)
        drain.annotate(self.select_files.checked)
        heuristics.apply_heuristics(
            self.select_files.grand_truth, self.select_files.checked
        )
        self._drain_needs_calculation = False

    def _show_logs_not_loaded(self):
        ui.label("Please provide files above to see logs here !").tailwind.text_align(
            "center"
        ).width("full").font_size("lg")

    def _show_logs(self):
        COLORS: list[TextColor] = [
            "neutral-500",
            "neutral-500",
            "green-500",
            "green-600",
        ]

        assert self.select_files.checked is not None

        log_view = LogView(self.select_files.checked)
        with ui.dialog() as log_view_dialog:
            log_view_dialog.props(add="full-width")
            log_view.show().tailwind.background_color("white").padding("p-2.5").width("max")

        def preview_log(line_id: int):
            log_view_dialog.open()
            log_view.focus_line(line_id)

        for i, line in enumerate(self.select_files.checked.lines):
            val = 0
            for heuristic in line.list_heuristics():
                val = max(val, line.get_heuristic(heuristic))

            if val < self.heuristic_setup.heuristic_cap:
                continue

            color = COLORS[int(len(COLORS) * val)]

            lbl = ui.label(f"{i + 1}: {line.line}")
            lbl.on("click", partial(preview_log, i))

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

    def show(self):
        self.parent = ui.element("div")
        self.heuristic_setup.state_changed.connect(self.update, weak=False)
        self.select_files.state_changed.connect(self.update, weak=False)
        self.drain_setup.state_changed.connect(self.update, weak=False)
        with self.parent:
            self.update_log_visualization()

    def update(self, sender: object = None):
        if isinstance(sender, (SelectFiles, DrainSetup)):
            self._drain_needs_calculation = True

        self.parent.clear()
        with self.parent:
            self.update_log_visualization()
