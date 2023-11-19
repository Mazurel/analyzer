from dataclasses import dataclass
from functools import partial
import math

from src.heuristics import manager as heuristics
from src.views import (
    View,
    HeuristicSetup,
    SelectFiles,
    DrainSetup,
    MultiLogView,
)
from src.widgets import log_line

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

    async def update_log_visualization(self):
        self.parent.tailwind.padding("p-5").container().box_shadow(
            "inner"
        ).background_color("zinc-300").min_height("max")

        if self.select_files.state == SelectFiles.State.FILES_NOT_UPLOADED:
            self._show_logs_not_loaded()
            return

        if self._drain_needs_calculation:
            self._recalculate_drain()

        await self._show_logs()

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

    async def _show_logs(self):
        COLORS: list[TextColor] = [
            "neutral-500",
            "neutral-500",
            "green-500",
            "green-600",
        ]

        assert self.select_files.checked is not None
        assert self.select_files.grand_truth is not None

        log_view = MultiLogView(
            self.select_files.checked, self.select_files.grand_truth
        )
        with ui.dialog() as log_view_dialog:
            log_view_dialog.props(add="full-width")
            e = await log_view.show()
            e.tailwind.background_color("white").padding("p-2.5").width("max")

        def preview_log(line_id: int):
            log_view_dialog.open()
            log_view.focus_line(line_id)

        async def make_log_line(i: int, line: "LogLine"):
            val = 0
            for heuristic in line.list_heuristics():
                val = max(val, line.get_heuristic(heuristic))

            if val < self.heuristic_setup.heuristic_cap:
                return

            color = COLORS[math.floor(len(COLORS) * val - 1e-6)]
            lbl = log_line(line)
            lbl.on("click", partial(preview_log, i))

            lbl.tailwind.text_color(color)
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

        for i, line in enumerate(self.select_files.checked.lines):
            await make_log_line(i, line)

    async def show(self):
        self.parent = ui.element("div")
        self.heuristic_setup.on_state_changed(self.update)
        self.select_files.on_state_changed(self.update)
        self.drain_setup.on_state_changed(self.update)
        with self.parent:
            await self.update_log_visualization()

    async def update(self, sender: object = None):
        if isinstance(sender, (SelectFiles, DrainSetup)):
            self._drain_needs_calculation = True

        try:
            self.parent.clear()
        except KeyError:
            pass

        with self.parent:
            await self.update_log_visualization()
