from io import StringIO
from typing import Callable

from src.logs.types import LogFile

from nicegui import ui, events
from nicegui.element import Element


class LogFileUpload(ui.upload):
    def _parse_file(self, event: events.UploadEventArguments):
        try:
            buffer = StringIO(event.content.read().decode("utf-8"))
            log_file = LogFile(buffer)
        except Exception as ex:
            ui.notify(f"Uploading log file failed with: {str(ex)}")
            return

        self._on_upload(log_file, buffer)

    def __init__(self, label: str, on_upload: Callable[[LogFile], None]):
        super().__init__(
            label=label,
            on_upload=self._parse_file,
            auto_upload=True,
            max_files=1,
        )

        self._on_upload = on_upload


def settings_frame() -> Element:
    el = ui.element("div")
    el.tailwind.border_color("indigo-300")
    el.tailwind.border_width("2")
    el.tailwind.padding("p-4")
    el.tailwind.border_radius("lg")
    return el
