from typing import Optional, TextIO, NamedTuple
from dataclasses import dataclass


from src.logs.timestamp import extract_timestamp


@dataclass
class Template:
    id: int
    pattern: str
    name: Optional[str] = None


class LogLine:
    def __init__(self, line: str) -> None:
        self._line_content = line
        self._heuristics: dict[str, float] = {}
        self._template: Optional[Template] = None
        self._timestamp: Optional[float] = extract_timestamp(line)

    @property
    def line(self) -> str:
        return self._line_content

    @property
    def template(self) -> Template:
        if self._template is None:
            raise ValueError("Template was not set")
        return self._template

    @template.setter
    def template(self, template: Template):
        assert template is not None
        self._template = template

    @property
    def timestamp(self) -> float:
        if self._timestamp is None:
            raise ValueError("Timestamp was not set")
        return self._timestamp

    def add_heuristic(self, name: str, value: float):
        """
        Add heurtisitc value named `name` to the log line.

        When `value` is:
        - `1.0` -> This log line is really **important** according to heuristic
        - `0.0` -> This log line is really **unimportant** according to heuristic
        """
        assert 0.0 <= value <= 1.0, "Heuristic `value` must be in range"
        self._heuristics[name] = value

    def list_heuristics(self) -> set[str]:
        return set(self._heuristics.keys())

    def clear_heuristics(self):
        self._heuristics.clear()

    def has_heuristic(self, name: str) -> bool:
        return name in self._heuristics.keys()

    def get_heuristic(self, name: str) -> float:
        if name not in self._heuristics:
            raise ValueError(f"Heuristic {name} does not exists !")

        return self._heuristics[name]


class LogFile:
    def __init__(self, file: TextIO) -> None:
        self._lines = [LogLine(line) for line in file.readlines()]

    @property
    def lines(self) -> list[LogLine]:
        return self._lines

    def clear_heuristics(self):
        for line in self.lines:
            line.clear_heuristics()


class MaskingInstruction(NamedTuple):
    name: str
    regex: str
