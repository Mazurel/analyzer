from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional

from nicegui.element import Element
from blinker import Signal

from src.logs.types import LogFile
from src.views import View
from src.widgets import LogFileUpload


@dataclass
class SelectFiles(View):
    class State(Enum):
        FILES_UPLOADED = auto()
        FILES_NOT_UPLOADED = auto()

    state_changed: Signal = field(default_factory=lambda: Signal())
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

    def show(self, container: Element):
        LogFileUpload("Upload Grand Truth file", on_upload=self._handle_grand_truth)
        LogFileUpload("Upload Checked file", on_upload=self._handle_checked)

    def update(self, sender: object = None):
        pass
