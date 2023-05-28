from io import StringIO

from src.logs.types import LogFile
from src.views.widgets import LogFileUpload
from src.logs.drain import DrainManager
from src.heuristics import manager as heuristics

from nicegui import ui, events, Tailwind
from nicegui.tailwind_types import font_family

class NiceGuiView():
    def __init__(self) -> None:
        self._checked = None
        self._grand_truth = None

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
 
        self._log_view.clear()
        with self._log_view:
            self._show_logs()
 
    def _show_logs(self):
        COLORS = [
            "neutral-500",
            "neutral-500",
            "green-500",
            "green-600",
        ]
        for line in self._checked.lines:
            val = 0
            for heuristic in line.list_heuristics():
                val = max(val, line.get_heuristic(heuristic))
            color = COLORS[int(len(COLORS) * val)]

            lbl = ui.label(line.line)
            lbl.tailwind.font_family("mono").user_select("none").text_overflow("text-clip").text_color(color)
            lbl.classes(add="hover:font-bold")
            with lbl:
                tooltip_text = [
                    f"Template: {line.template.pattern}",
                ]
                tooltip_text += [
                    f"{heuristic}: {line.get_heuristic(heuristic)}"
                    for heuristic in line.list_heuristics()
                ]
                ui.tooltip("\n".join(tooltip_text)).tailwind.font_size("base").font_family("mono").whitespace("pre-line")

    def start(self):
        ui.query("body").tailwind.background_color("zinc-200")
        ui.query(".nicegui-content").tailwind.align_items("center")
        ui.markdown("# Log analyzer")
        ui.markdown("Upload Grand truth and checked file to see analysis result")
        with ui.row() as row:
            LogFileUpload(
                "Upload Grand Truth file",
                on_upload=self._handle_grand_truth
            ) 

            LogFileUpload(
                "Upload Checked file",
                on_upload=self._handle_checked
            )

        self._log_view = ui.element("div")
        self._log_view.tailwind.padding("p-5").container().box_shadow("inner").background_color("zinc-300")

        ui.run()
