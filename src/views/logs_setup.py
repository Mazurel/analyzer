from dataclasses import dataclass

from nicegui import ui

from src.widgets import settings_frame
from src.views import View


@dataclass
class LogsSetup(View):
    """
    This view is responsible for configuring log files.
    """
    timestamp_regex: str = ""

    def show(self):
        with settings_frame() as el:
            ui.input("Timestamp Regexp", on_change=self.update).bind_value_to(self, "timestamp_regex")
        return el

    def update(self, sender: object = None):
        pass
