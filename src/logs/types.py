from typing import Optional, TextIO

from dataclasses import dataclass


@dataclass
class Template:
    id: int
    pattern: str
    name: str | None = None


class LogLine:
    def __init__(self, line: str) -> None:
        self._line_content = line
        self._heuristics: dict[str, float] = {}
        self._template: Optional[Template] = None

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

    def add_heuristic(self, name: str, value: float):
        """
        Add heurtisitc value named `name` to the log line.

        When `value` is:
        - `1.0` -> This log line is really **important** according to heuristic
        - `0.0` -> This log line is really **unimportant** according to heuristic
        """
        assert 0.0 <= value <= 1.0, "Heuristic `value` must be in range"

        if name in self._heuristics:
            raise ValueError(f"Heuristic {name} already exists !")

        self._heuristics[name] = value

    def list_heuristics(self) -> set[str]:
        return set(self._heuristics.keys())

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
