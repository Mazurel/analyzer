from typing import Optional, List, Union
from datetime import datetime
from logging import getLogger
from dataclasses import dataclass

import dateparser

logger = getLogger("timestamps")


# The following are some of the templates automagically supported
# https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior
TIMESTAMP_TEMPLATES = [
    "%Y-%m-%d %H:%M:%S,%f",
    "%m-%d %H:%M:%S.%f",
    "%H:%M",
]


@dataclass
class Timestamp:
    representation: Optional[str] = None
    value: Union[None, datetime, float] = None

    def is_empty(self) -> bool:
        return self.value is None

    def get_numeric_value(self) -> float:
        if isinstance(self.value, float):
            return self.value

        if isinstance(self.value, datetime):
            return self.value.timestamp()

        raise ValueError("Timestamp has no value !")

    def get_relative_numeric_value(self, starting_time: "Timestamp") -> float:
        v1 = self.get_numeric_value()
        v2 = starting_time.get_numeric_value()
        return v1 - v2

    def get_date_value(self) -> Optional[datetime]:
        return self.value if isinstance(self.value, datetime) else None

    def __str__(self) -> str:
        if self.representation is not None:
            return self.representation

        if v := self.get_date_value():
            return v.strftime("%Y-%m-%d %H:%M:%S,%f")

        if v := self.get_numeric_value():
            return str(v)

        return ""


def _subdivide_str(s: str) -> List[str]:
    """
    Divide string into subdivisions in the following pattern:

    ```python
    'a b c' -> ['a b c', 'a b', 'a']
    ```
    """
    words = s.split()
    subdivisions = [" ".join(words[:i]) for i in range(len(words), 0, -1)]
    return subdivisions


def _try_interpret_str(s: str) -> Optional[Timestamp]:
    try:
        return Timestamp(representation=s.strip(), value=float(s))
    except ValueError:
        pass

    if (
        date := dateparser.parse(
            s, TIMESTAMP_TEMPLATES, settings={"STRICT_PARSING": True}
        )
    ) is not None:
        return Timestamp(representation=s.strip(), value=date)

    return None


def extract(line: str) -> Optional[tuple[str, Timestamp]]:
    """
    Based on line of text (line of log), try to extract timestamp from the message.
    This method tries a few common templates, based on log types of:

    - Hadoop
    - Apache
    - Android
    - Linux Kernel

    The returned data should be a UNIX timestamp, but it may not be in some cases.
    Timestamp is only guaranteed to be accurate when comparing two timestamps
    (i.e. They are in chronological order).

    When `None` is returned, then there are no common timestamps in this line.
    """
    # Check for date/timestamp pattern in [ ... ]
    if line[0] == "[":
        end_index: int = line.find("]", 1)
        if end_index != -1:
            potential_timestamp = line[1:end_index]
            if (timestamp := _try_interpret_str(potential_timestamp)) is not None:
                logger.debug(f"Found at: {potential_timestamp}")
                return line[end_index + 1 :].lstrip(), timestamp

    # Check for date pattern with date/timestamp in front
    subdivisions = iter(reversed(_subdivide_str(line)))

    last_parsing_succesfull = True
    working_subdivision = ""
    working_timestamp = Timestamp()
    while last_parsing_succesfull:
        try:
            subdivision = next(subdivisions)
        except StopIteration:
            break

        timestamp = _try_interpret_str(subdivision)
        last_parsing_succesfull = timestamp is not None
        if last_parsing_succesfull:
            working_subdivision = subdivision
            working_timestamp = timestamp

    if working_subdivision == "":
        return None

    assert working_timestamp is not None

    line_without_timestamp = line[len(working_subdivision) :].lstrip()
    return line_without_timestamp, working_timestamp
