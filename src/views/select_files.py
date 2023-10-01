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

    state: State = State.FILES_NOT_UPLOADED
    grand_truth: Optional[LogFile] = None
    checked: Optional[LogFile] = None

    def _emit_state_changed(self):
        self.state = (
            self.State.FILES_UPLOADED
            if self.grand_truth is not None and self.checked is not None
            else self.State.FILES_NOT_UPLOADED
        )
        self.state_changed.send(self)

    def _handle_grand_truth(self, file: LogFile):
        self.grand_truth = file
        self._emit_state_changed()

    def _handle_checked(self, file: LogFile):
        self.checked = file
        self._emit_state_changed()

    def show(self):
        with ui.row() as r:
            LogFileUpload("Upload Grand Truth file", on_upload=self._handle_grand_truth)
            LogFileUpload("Upload Checked file", on_upload=self._handle_checked)
        return r

    def update(self, sender: object = None):
        pass
