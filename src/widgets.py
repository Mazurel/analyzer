from io import StringIO
from typing import Callable

from src.logs.types import LogFile

from nicegui import ui, events


class LogFileUpload(ui.upload):
    def _parse_file(self, event: events.UploadEventArguments):
        try:
            buffer = StringIO(event.content.read().decode("utf-8"))
            log_file = LogFile(buffer)
        except Exception as ex:
            ui.notify(f"Uploading log file failed with: {str(ex)}")
            return

        self._on_upload(log_file)

    def __init__(self, label: str, on_upload: Callable[[LogFile], None]):
        super().__init__(
            label=label,
            on_upload=self._parse_file,
            auto_upload=True,
            max_files=1,
        )

        self._on_upload = on_upload
