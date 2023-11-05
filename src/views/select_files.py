import os
from io import StringIO

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

from nicegui import ui

from src.logs.types import LogFile
from src.views import View
from src.widgets import LogFileUpload

from src.consts import LOG_WORKDIR

@dataclass
class SelectFiles(View):
    """
    This view is responsible for selecting grand truth and checked files.
    """

    class State(Enum):
        FILES_UPLOADED = auto()
        FILES_NOT_UPLOADED = auto()

    grand_truth: Optional[LogFile] = None
    checked: Optional[LogFile] = None
    grand_truth_name: Optional[str] = None
    checked_name: Optional[str] = None

    @property
    def state(self) -> State:
        return (
            self.State.FILES_UPLOADED
            if self.grand_truth is not None and self.checked is not None
            else self.State.FILES_NOT_UPLOADED
        )

    async def _handle_grand_truth(self, file: LogFile, buffer: StringIO):
        self.grand_truth = file
        # TODO 
        # currently temporary save of log file in order to simple use of another parsers
        self.grand_truth_name = "grand_truth.log"
        file.set_name(self.grand_truth_name)
        with open(os.path.join(LOG_WORKDIR, self.grand_truth_name), "w") as log_file:
            log_file.write(buffer.getvalue())
        await self._emit_state_changed()

    async def _handle_checked(self, file: LogFile, buffer: StringIO):
        self.checked = file
        # TODO 
        # currently temporary save of log file in order to simple use of another parsers
        self.checked_name = "checked.log"
        file.set_name(self.checked_name)
        with open(os.path.join(LOG_WORKDIR, self.checked_name), "w") as log_file:
            log_file.write(buffer.getvalue())
        await self._emit_state_changed()

    async def show(self):
        with ui.row() as r:
            LogFileUpload("Upload Grand Truth file", on_upload=self._handle_grand_truth)
            LogFileUpload("Upload Checked file", on_upload=self._handle_checked)
        return r

    async def update(self, sender: object = None):
        pass
