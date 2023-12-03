from dataclasses import dataclass

from src.views.view import View
from src.logs.types import LogFile

@dataclass
class BaseLogView(View):
    left_log_file: LogFile
    right_log_file: LogFile

    async def focus_line(self, _: int):
        pass
