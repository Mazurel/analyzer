from typing import TYPE_CHECKING

from src.logs.types import LogFile
from src.views.widgets import LogFileUpload
from src.logs.drain import DrainManager
from src.heuristics import manager as heuristics

from nicegui import ui

if TYPE_CHECKING:
    from nicegui.tailwind_types.text_color import TextColor

HEURISTIC_LABEL_TEXT = "Heuristic Cap ({}): "


class NiceGuiView:
    def __init__(self) -> None:
        self._checked = None
        self._grand_truth = None
        self._heuristic_cap = 0.5

    def _handle_heuristic_cap_change(self):
        self._heuristic_label.text = HEURISTIC_LABEL_TEXT.format(self._heuristic_cap)
        self._show_logs()

    def _handle_grand_truth(self, file: LogFile):
        self._grand_truth = file
        self._update_log_visualization()

    def _handle_checked(self, file: LogFile):
        self._checked = file
        self._update_log_visualization()

    def _update_log_visualization(self):
        if self._checked is None or self._grand_truth is None:
            return

        drain = DrainManager()
        drain.learn(self._grand_truth)
        drain.learn(self._checked)
        drain.annotate(self._grand_truth)
        drain.annotate(self._checked)

        heuristics.apply_heuristics(self._grand_truth, self._checked)
        self._show_logs()

    def _show_logs(self):
        COLORS: list[TextColor] = [
            "neutral-500",
            "neutral-500",
            "green-500",
            "green-600",
        ]

        if self._checked is None or self._grand_truth is None:
            self._show_logs_not_loaded()
            return

        self._log_view.clear()
        with self._log_view:
            for i, line in enumerate(self._checked.lines):
                val = 0
                for heuristic in line.list_heuristics():
                    val = max(val, line.get_heuristic(heuristic))

                if val < self._heuristic_cap:
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

    def _show_logs_not_loaded(self):
        if not hasattr(self, "_log_view"):
            return

        self._log_view.clear()
        with self._log_view:
            ui.label(
                "Please provide files above to see logs here !"
            ).tailwind.text_align("center").width("full").font_size("lg")

    def start(self):
        ui.query("body").tailwind.background_color("zinc-200")
        ui.query(".nicegui-content").tailwind.align_items("center")
        ui.markdown("# Log analyzer")
        ui.markdown("Upload Grand truth and checked file to see analysis result")
        with ui.row() as row:
            LogFileUpload("Upload Grand Truth file", on_upload=self._handle_grand_truth)

            LogFileUpload("Upload Checked file", on_upload=self._handle_checked)

        with ui.row():
            self._heuristic_label = ui.label()
            self._heuristic_slider = (
                ui.slider(
                    min=0,
                    max=1,
                    step=0.01,
                    value=self._heuristic_cap,
                    on_change=self._handle_heuristic_cap_change,
                )
                .bind_value_to(self, "_heuristic_cap")
                .tailwind.width("40")
            )
            self._handle_heuristic_cap_change()

        self._log_view = ui.element("div")
        self._log_view.tailwind.padding("p-5").container().box_shadow(
            "inner"
        ).background_color("zinc-300").min_height("max")
        self._show_logs_not_loaded()

        with ui.element("footer") as el:
            el.tailwind.margin("mt-10")
            ui.label("This tool is created for Research Project: ").tailwind.display(
                "inline"
            )
            ui.link(
                "Discovery and visualization of meaningful information in applications logs",
                "https://projektgrupowy.eti.pg.gda.pl/editions/18/projects/4881",
            ).tailwind.font_style("italic").display("inline")

        ui.run()
