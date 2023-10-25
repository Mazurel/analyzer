from typing import Generator, Optional, TextIO, NamedTuple
from dataclasses import dataclass
from uuid import uuid4, UUID

from src.logs.timestamp import TimestampExtractor


@dataclass
class Template:
    id: int
    pattern: str
    name: Optional[str] = None


class NoTemplateException(ValueError):
    pass


class NoTimestampException(ValueError):
    pass


class LogLine:
    def __init__(self, line: str) -> None:
        self._line_content = line

        self._line_content_no_timestamp = None
        self._timestamp = None
        self._heuristics: dict[str, float] = {}
        self._template: Optional[Template] = None
        self._id: Optional[UUID] = None

    @property
    def line(self) -> str:
        return self._line_content

    @property
    def line_without_timestamp(self) -> str:
        return (
            self._line_content_no_timestamp
            if self._line_content_no_timestamp is not None
            else self._line_content
        )

    @property
    def template(self) -> Template:
        if self._template is None:
            raise NoTemplateException("Template was not set")
        return self._template

    @template.setter
    def template(self, template: Template):
        assert template is not None
        self._template = template

    def extract_timestamp(self, extractor: TimestampExtractor):
        if timestamp_extraction_res := extractor.extract(self.line):
            self._line_content_no_timestamp, self._timestamp = timestamp_extraction_res

    @property
    def timestamp(self) -> float:
        if self._timestamp is None:
            raise NoTimestampException("Timestamp was not set")
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

    def get_unique_id(self) -> UUID:
        if self._id is not None:
            return self._id

        self._id = uuid4()
        return self._id

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
        timestamp_extractor = TimestampExtractor()
        self._lines = [LogLine(line) for line in file.readlines()]
        for line in self._lines:
            line.extract_timestamp(timestamp_extractor)

    @property
    def lines(self) -> list[LogLine]:
        return self._lines

    def clear_heuristics(self):
        for line in self.lines:
            line.clear_heuristics()

    def get_all_template_ids(self) -> Generator[int, None, None]:
        covered_id = set()
        for line in self.lines:
            if line.template.id in covered_id:
                continue

            yield line.template.id
            covered_id.add(line.template.id)


class MaskingInstruction(NamedTuple):
    name: str
    regex: str
