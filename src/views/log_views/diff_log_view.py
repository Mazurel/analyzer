from dataclasses import dataclass, field
from typing import Generator
import logging
import math

from nicegui.elements.scroll_area import ScrollArea

from src.logs.types import LogLine
from src.heuristics.histogram_time import TimeHeuristicMetadata
from src.views.log_views.base import BaseLogView
from src.heuristics.manager import query_heuristic_name
from src.heuristics.histogram_time import TimeHeuristic

from nicegui import ui
from nicegui.element import Element
from nicegui.elements.scroll_area import ScrollEventArguments
from nicegui.tailwind_types.background_color import BackgroundColor

log = logging.getLogger("DiffLogView")


def are_the_same(f1: float, f2: float) -> bool:
    return abs(f1 - f2) < 1


@dataclass
class DiffLogView(BaseLogView):
    """
    This view shows log file.
    It also alows focusing lines by ID.
    """

    lines: list[tuple[Element, list[Element]]] = field(default_factory=lambda: [])
    scroll_areas: list[ScrollArea] = field(default_factory=lambda: [])
    scroll_offset: float = 0.0

    def build_log_buffers(self) -> list[tuple[LogLine, list[LogLine]]]:
        used_line_numbers: set[int] = set()
        result: list[tuple[LogLine, list[LogLine]]] = []

        for line in self.left_log_file.lines:
            arr = []
            result.append((line, arr))
            try:
                meta = line.get_heuristic_metadata(
                    query_heuristic_name(TimeHeuristic), TimeHeuristicMetadata
                )
                if meta.connected_line is not None:
                    used_line_numbers.add(meta.connected_line.line_number)
                    arr.append(meta.connected_line)
            except ValueError:
                pass

        for line_left in filter(lambda l: l.line_number not in used_line_numbers, self.right_log_file.lines):
            l = self.left_log_file.find_closest_line_by_relative_timestamp(line_left.timestamp.get_relative_numeric_value(self.right_log_file.starting_time))
            result[l.line_number - 1][1].append(line_left)

        for _, line_list in result:
            line_list.sort(key=lambda l: l.line_number)

        return result

    def show_heading(self, text: str):
        ui.label(text).tailwind.font_size("3xl").text_align(
            "center"
        ).height("fit")

    async def sync_scroll_areas(self, e: ScrollEventArguments):
        dest_scroll_offset: float = math.floor(e.vertical_position)

        if not are_the_same(dest_scroll_offset, self.scroll_offset):
            self.scroll_offset = dest_scroll_offset
            await self._emit_state_change()

    async def show(self) -> Element:
        self.lines = []

        with ui.grid(columns=2) as e:
            e.tailwind.gap("x-4")

            with ui.element("div"):
                self.show_heading("Checked")
                with ui.scroll_area(on_scroll=self.sync_scroll_areas) as left_scroll_area:
                    left_scroll_area.tailwind.space_between("y-1").height("full")
                    left_column = ui.element("div")
                    left_column.tailwind.width("max").height("max")
                    self.scroll_areas.append(left_scroll_area)

            with ui.element("div"):
                self.show_heading("Grand Truth")
                with ui.scroll_area(on_scroll=self.sync_scroll_areas) as right_scroll_area:
                    right_scroll_area.tailwind.space_between("y-1").height("full")
                    right_column = ui.element("div")
                    right_column.tailwind.width("max").height("max")
                    self.scroll_areas.append(right_scroll_area)

            for group_id, (line, lines) in enumerate(self.build_log_buffers()):
                COLORS: list[BackgroundColor] = [
                    "cyan-50",
                    "cyan-100"
                ]

                def log_line(txt: str):
                    lbl = ui.label(f"{txt}")
                    lbl.tailwind.font_family("mono").background_color(COLORS[group_id % 2]).width("full")
                    return lbl

                with left_column:
                    left_line = log_line(f"{line.line_number}: {line.line}")
                    for _ in range(len(lines) - 1):
                        log_line("+++")

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

        left_line.tailwind.font_weight("bold")
        left_line.run_method(
            "scrollIntoView", {"block": "center"}
        )

        for line in right_lines:
            line.tailwind.font_weight("bold")

    async def update(self, _: object = None):
        for scroll_area in self.scroll_areas:
            off: float = (await scroll_area.run_method("getScrollPosition"))["top"]
            if not are_the_same(off, self.scroll_offset):
                scroll_area.scroll_to(pixels=self.scroll_offset)

