from dataclasses import dataclass, field

from nicegui.element import Element

from src.logs.types import LogFile

from .view import View
from nicegui import ui


@dataclass
class LogView(View):
    """
    This view shows log file.
    It also alows focusing lines by ID.
    """

    log_file: LogFile
    lines: list[Element] = field(default_factory=lambda: [])

    def show(self) -> Element:
        with ui.element("div") as e:
            e.tailwind.space_between("y-1.5").max_width("2xl")
            for i, line in enumerate(self.log_file.lines):
                lbl = ui.label(f"{i + 1}: {line.line}")
                self.lines.append(lbl)
                lbl.tailwind.font_family("mono")
        return e

    def focus_line(self, id: int):
        for line in self.lines:
            line.classes(remove="font-bold")

        self.lines[id].run_method(
            "scrollIntoView", {"behavior": "smooth", "block": "center"}
        )
        self.lines[id].tailwind.font_weight("bold")

    def update(self, sender: object = None):
        pass
