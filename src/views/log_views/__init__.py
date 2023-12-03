from dataclasses import dataclass
from typing import Optional, Tuple

from src.logs.types import LogFile

from src.views.view import View
from src.views.log_views.log_view import LogView
from src.views.log_views.multi_log_view import MultiLogView
from src.views.log_views.diff_log_view import DiffLogView
from src.views.log_views.base import BaseLogView

from nicegui import ui
from nicegui.element import Element

ALL_LOG_VIEWS: dict[str, type[BaseLogView]] = {
    "Basic log view": LogView,
    "Dual log view": MultiLogView,
    "Diff log view": DiffLogView,
}

ALL_LOG_VIEWS_ID_TO_NAME = { i: name for i, name in enumerate(ALL_LOG_VIEWS.keys()) }

@dataclass
class LogViewWrapper(View):
    left_log_file: LogFile
    right_log_file: LogFile

    current_log_view: Optional[Tuple[BaseLogView, Element]] = None
    parent: Optional[Element] = None
    focused_line: int = 0

    async def change_log_view(self, id: int):
        assert self.parent is not None

        log_name = ALL_LOG_VIEWS_ID_TO_NAME[id]
        if self.current_log_view is not None:
            v, el = self.current_log_view
            self.current_log_view = None
            el.clear()
            self.parent.remove(el)
            del el
            del v

        with self.parent:
            v = ALL_LOG_VIEWS[log_name](self.left_log_file, self.right_log_file)
            el = await v.show()
            el.tailwind.max_width("none").max_width("full").height("5/6")
            await v.focus_line(self.focused_line)

        self.current_log_view = (v, el)
        await self.state_changed.send_async()

    async def show(self) -> Element:
        with ui.element() as e:
            self.parent = e
            with ui.element() as wrap:
                async def on_toggle_change(a):
                    await self.change_log_view(a.value)
                wrap.tailwind.height("1/6").display("flex").align_items("center").justify_content("center")
                ui.toggle(ALL_LOG_VIEWS_ID_TO_NAME, value=0, on_change=on_toggle_change).tailwind.margin("my-3")
                await self.change_log_view(0)
            return e

    async def update(self, sender: object = None):
        if self.current_log_view is not None:
            await self.current_log_view[0].update(sender)

    async def focus_line(self, id: int):
        self.focused_line = id
        if self.current_log_view is not None:
            await self.current_log_view[0].focus_line(id)

__all__ = [
    "LogViewWrapper",
    "BaseLogView",
    "LogView",
    "MultiLogView",
    "ALL_LOG_VIEWS",
]

