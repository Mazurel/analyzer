from dataclasses import dataclass, field

from src.logs.types import LogFile
from src.views.log_views.base import BaseLogView

from nicegui import ui
from nicegui.element import Element


@dataclass
class LogView(BaseLogView):
    """
    This view shows log file.
    It also alows focusing lines by ID.
    """

    lines: list[Element] = field(default_factory=lambda: [])

    async def show(self) -> Element:
        with ui.scroll_area() as e:
            e.tailwind.space_between("y-10").max_width("2xl")
            for i, line in enumerate(self.right_log_file.lines):
                lbl = ui.label(f"{i + 1}: {line.line}")
                self.lines.append(lbl)
                lbl.tailwind.font_family("mono")
        return e

    async def focus_line(self, id: int):
        for line in self.lines:
            line.classes(remove="font-bold")

        self.lines[id].run_method(
            "scrollIntoView", {"behavior": "smooth", "block": "center"}
        )
        self.lines[id].tailwind.font_weight("bold")

