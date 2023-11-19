import bisect
import logging
import multiprocessing
from typing import Generator, Optional, TextIO, NamedTuple, cast, TypeVar
from dataclasses import dataclass
from uuid import uuid4, UUID
from multiprocessing import Pool

from src.logs.timestamp import extract, Timestamp
from src.itertools import contains_at_least_n, find_left


T = TypeVar("T")

logger = logging.getLogger("LogFile")


@dataclass
class HeuristicData:
    value: float
    metadata: Optional[object] = None  # Custom heuristic metadata


@dataclass
class Template:
    id: int
    pattern: str
    name: Optional[str] = None


class NoTemplateException(ValueError):
    pass


class NoTimestampException(ValueError):
    pass


class InvalidLogFile(ValueError):
    pass


class LogLine:
    def __init__(self, line: str, line_number: int = 0) -> None:
        self._line_content = line
        self._line_number = line_number

        self._line_content_no_timestamp = None
        self._timestamp = None
        self._heuristics: dict[str, HeuristicData] = {}
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

    @property
    def line_number(self) -> int:
        return self._line_number

    @property
    def timestamp(self) -> Timestamp:
        if self._timestamp is None:
            raise NoTimestampException("Timestamp was not set")
        return self._timestamp

    def set_timestamp(self, extraction_result: tuple[str, Timestamp]):
        self._timestamp = extraction_result[1]
        self._line_content_no_timestamp = extraction_result[0]

    def get_timestamp_as_extraction_result(self) -> tuple[str, Timestamp]:
        if self._line_content_no_timestamp is None:
            raise RuntimeError("Timestamp is not set !")

        if self._timestamp is None:
            raise RuntimeError("Timestamp is not set !")

        return (self._line_content_no_timestamp, self._timestamp)

    @property
    def has_timestamp(self) -> bool:
        return self._timestamp is not None

    def add_heuristic(self, name: str, value: float, metadata: object | None = None):
        """
        Add heurtisitc value named `name` to the log line.

        When `value` is:
        - `1.0` -> This log line is really **important** according to heuristic
        - `0.0` -> This log line is really **unimportant** according to heuristic
        """
        if metadata is not None:
            self._heuristics[name] = HeuristicData(value, metadata)
        else:
            assert 0.0 <= value <= 1.0, "Heuristic `value` must be in range"
            self._heuristics[name] = HeuristicData(value)

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

        return self._heuristics[name].value

    def get_heuristic_metadata(self, name: str, t: type[T]) -> T:
        if name not in self._heuristics:
            raise ValueError(f"Heuristic {name} does not exists !")

        if not isinstance(self._heuristics[name].metadata, t):
            raise TypeError("Invalid type `t` provided")

        return cast(t, self._heuristics[name].metadata)

    def __repr__(self) -> str:
        fields = [
            (self._line_number, "Line Number"),
            (self._line_content.strip(), "Content"),
            (self._template, "Template"),
            (self._timestamp, "Timestamp"),
        ]
        fields_stred = ", ".join([f"{n}={v}" for v, n in fields if v is not None])
        return f"LogLine({fields_stred})"


class LogFile:
    @staticmethod
    def extract_timestamp(line: str):
        return extract(line)

    def __init__(self, file: TextIO) -> None:
        # TODO: Add check if timestamps are "sorted"
        #       , if not, sort the file
        self._lines = [
            LogLine(line, line_number=i + 1) for i, line in enumerate(file.readlines())
        ]

        if len(self._lines) <= 2:
            raise InvalidLogFile("Log file is too short")

        with Pool(processes=multiprocessing.cpu_count() // 2) as p:
            for i, r in enumerate(
                p.map(
                    self.extract_timestamp,
                    [line.line for line in self._lines],
                    chunksize=32,
                )
            ):
                if r is None:
                    continue

                self._lines[i].set_timestamp(r)

        self.fill_in_timestamps()

        logger.info("Log file initialized")

        self._starting_time = None

    def fill_in_timestamps(self):
        if not contains_at_least_n(self._lines, 2, lambda line: line.has_timestamp):
            raise InvalidLogFile("Log file needs at least 2 timestamps")

        left = 0
        while True:
            l1 = find_left(self._lines, lambda l: l.has_timestamp, left)
            if l1 == -1:
                break

            l2 = find_left(self._lines, lambda l: l.has_timestamp, l1 + 1)
            if l2 == -1:
                break

            left = l2

            if l2 - l1 == 1:
                # Nothing to fill
                continue

            logger.info(f"Fill timestamps in range: {l1} - {l2}")
            # Fill in the timestamps !
            for i in range(l1 + 1, l2, 1):
                self._lines[i].set_timestamp(
                    ("", self._lines[l1].get_timestamp_as_extraction_result()[1])
                )

    @property
    def lines(self) -> list[LogLine]:
        return self._lines

    @property
    def starting_time(self) -> Timestamp:
        if self._starting_time is not None:
            return self._starting_time

        try:
            self._starting_time = next(
                line.timestamp for line in self.lines if line.has_timestamp
            )
        except StopIteration:
            raise ValueError("None of the lines have timestamp")

        return self._starting_time

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

    def find_closest_line_by_relative_timestamp(self, time: float) -> LogLine:
        index = bisect.bisect(
            self.lines,
            time,
            key=lambda line: line.timestamp.get_relative_numeric_value(
                self.starting_time
            ),
        )
        return self.lines[min(index, len(self.lines) - 1)]


class MaskingInstruction(NamedTuple):
    name: str
    regex: str
