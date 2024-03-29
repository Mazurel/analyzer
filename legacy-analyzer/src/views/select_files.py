from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

from nicegui import ui

from src.logs.types import LogFile
from src.views import View
from src.widgets import LogFileUpload


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

    @property
    def state(self) -> State:
        return (
            self.State.FILES_UPLOADED
            if self.grand_truth is not None and self.checked is not None
            else self.State.FILES_NOT_UPLOADED
        )

    async def _handle_grand_truth(self, file: LogFile):
        self.grand_truth = file
        await self._emit_state_change()

    async def _handle_checked(self, file: LogFile):
        self.checked = file
        await self._emit_state_change()

    async def show(self):
        with ui.row() as r:
            LogFileUpload("Upload Baseline file", on_upload=self._handle_grand_truth)
            LogFileUpload("Upload Analyzed file", on_upload=self._handle_checked)
        return r

    async def update(self, sender: object = None):
        pass
