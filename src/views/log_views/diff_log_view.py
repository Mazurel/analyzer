from dataclasses import dataclass, field
from typing import Generator
import logging

from src.logs.types import LogLine
from src.heuristics.histogram_time import TimeHeuristicMetadata
from src.views.log_views.base import BaseLogView
from src.heuristics.manager import query_heuristic_name
from src.heuristics.histogram_time import TimeHeuristic

from nicegui import ui
from nicegui.element import Element

log = logging.getLogger("DiffLogView")

@dataclass
class DiffLogView(BaseLogView):
    """
    This view shows log file.
    It also alows focusing lines by ID.
    """

    lines: list[tuple[Element, list[Element]]] = field(default_factory=lambda: [])

    def build_log_buffers(self) -> Generator[tuple[LogLine, list[LogLine]], None, None]:
        for line in self.left_log_file.lines:
            try:
                meta = line.get_heuristic_metadata(
                    query_heuristic_name(TimeHeuristic), TimeHeuristicMetadata
                )
                if meta.connected_line is not None:
                    yield (line, [meta.connected_line])
                    continue
            except ValueError:
                pass
            yield (line, [])

    def show_heading(self, text: str):
        ui.label(text).tailwind.font_size("3xl").text_align(
            "center"
        ).height("fit")


    async def show(self) -> Element:
        self.lines = []

        with ui.grid(columns=2) as e:
            def update_scroll_percentage(e):
                p: float = e.vertical_percentage
                left_scroll_area.scroll_to(percent=p)
                right_scroll_area.scroll_to(percent=p)

            e.tailwind.gap("x-4")

            with ui.element("div"):
                self.show_heading("Checked")
                with ui.scroll_area(on_scroll=update_scroll_percentage) as left_scroll_area:
                    left_scroll_area.tailwind.space_between("y-1").height("full")
                    left_column = ui.element("div")
                    left_column.tailwind.width("max").height("max")

            with ui.element("div"):
                self.show_heading("Grand Truth")
                with ui.scroll_area(on_scroll=update_scroll_percentage) as right_scroll_area:
                    right_scroll_area.tailwind.space_between("y-1").height("full")
                    right_column = ui.element("div")
                    right_column.tailwind.width("max").height("max")

            for i, (line, lines) in enumerate(self.build_log_buffers()):
                def log_line(txt: str):
                    lbl = ui.label(f"{txt}")
                    lbl.tailwind.font_family("mono")
                    return lbl

                with left_column:
                    left_line = log_line(f"{line.line_number}: {line.line}")

                right_lines = []
                with right_column:
                    if len(lines) > 0:
                        for l in lines:
                            lbl = log_line(f"{l.line_number}: {l.line}")
                            right_lines.append(lbl)
                    else:
                        log_line(f" ---")

                self.lines.append((left_line, right_lines))

        return e

    async def focus_line(self, id: int):
        left_line, right_lines = self.lines[id]

        left_line.run_method(
            "scrollIntoView", {"behavior": "smooth", "block": "center"}
        )
        left_line.tailwind.font_weight("bold")

        for l in right_lines:
            l.run_method(
                "scrollIntoView", {"behavior": "smooth", "block": "center"}
            )
            l.tailwind.font_weight("bold")

