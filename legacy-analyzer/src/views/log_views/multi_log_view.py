from dataclasses import dataclass, field

from src.logs.types import LogLine
from src.heuristics.histogram_time import TimeHeuristicMetadata
from src.views.log_views.base import BaseLogView
from src.heuristics.manager import query_heuristic_name
from src.heuristics.histogram_time import TimeHeuristic

from nicegui import ui
from nicegui.element import Element


@dataclass
class MultiLogView(BaseLogView):
    """
    This view shows log file.
    It also alows focusing lines by ID.
    """

    lines_left: list[tuple[LogLine, Element]] = field(default_factory=lambda: [])
    lines_right: list[tuple[LogLine, Element]] = field(default_factory=lambda: [])

    async def show(self) -> Element:
        with ui.grid(columns=2) as e:
            e.tailwind.gap("x-4")

            with ui.element("div"):
                ui.label("Analyzed").tailwind.font_size("3xl").text_align(
                    "center"
                ).height("fit")
                with ui.scroll_area() as scroll_area:
                    scroll_area.tailwind.space_between("y-1").height("full")
                    with ui.element("div") as wrapper:
                        wrapper.tailwind.width("max").height("max")
                        for i, line in enumerate(self.left_log_file.lines):
                            lbl = ui.label(f"{i + 1}: {line.line}")
                            lbl.tailwind.font_family("mono")
                            self.lines_left.append((line, lbl))

            with ui.element("div"):
                ui.label("Baseline").tailwind.font_size("3xl").text_align(
                    "center"
                ).height("fit")
                with ui.scroll_area() as scroll_area:
                    scroll_area.tailwind.space_between("y-1").height("full")
                    with ui.element("div") as wrapper:
                        wrapper.tailwind.width("max").height("max")
                        for i, line in enumerate(self.right_log_file.lines):
                            lbl = ui.label(f"{i + 1}: {line.line}")
                            lbl.tailwind.font_family("mono")

                            self.lines_right.append((line, lbl))

        return e

    async def focus_line(self, id: int):
        for _, left_line in self.lines_left:
            left_line.classes(remove="font-bold")

        for _, left_line in self.lines_right:
            left_line.classes(remove="font-bold")

        left_line, left_line_element = self.lines_left[id]
        left_line_element.run_method(
            "scrollIntoView", {"behavior": "smooth", "block": "center"}
        )
        left_line_element.tailwind.font_weight("bold")

        right_line_element = None
        try:
            meta = left_line.get_heuristic_metadata(
                query_heuristic_name(TimeHeuristic), TimeHeuristicMetadata
            )
            if meta.connected_line is not None:
                _, right_line_element = self.lines_right[
                    meta.connected_line.line_number - 1
                ]
        except ValueError:
            pass
        except TypeError:
            pass

        if right_line_element is None:
            right_line = self.right_log_file.find_closest_line_by_relative_timestamp(
                left_line.timestamp.get_relative_numeric_value(
                    self.left_log_file.starting_time
                )
            )
            _, right_line_element = self.lines_right[right_line.line_number - 1]

        right_line_element.run_method(
            "scrollIntoView", {"behavior": "smooth", "block": "center"}
        )
        right_line_element.tailwind.font_weight("bold")
