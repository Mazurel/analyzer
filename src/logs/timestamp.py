from typing import Optional, List
from logging import getLogger

from dateutil import parser as date_parser

logger = getLogger("timestamps")


class TimestampExtractor:
    def __init__(self) -> None:
        self.cached_positions = []

    def _subdivide_str(self, s: str) -> List[str]:
        """
        Divide string into subdivisions in the following pattern:

        ```python
        'a b c' -> ['a b c', 'a b', 'a']
        ```
        """
        words = s.split()
        subdivisions = [" ".join(words[:i]) for i in range(len(words), 0, -1)]
        return subdivisions

    def _try_interpret_str(self, s: str) -> Optional[float]:
        try:
            date = date_parser.parse(s)
            return date.timestamp()
        except date_parser.ParserError:
            pass

        try:
            return float(s)
        except ValueError:
            pass

        return None

    def extract(self, line: str) -> Optional[tuple[str, float]]:
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
                if (
                    timestamp := self._try_interpret_str(potential_timestamp)
                ) is not None:
                    logger.debug(f"Found at: {potential_timestamp}")
                    return line[end_index + 1 :].lstrip(), timestamp

        # Check for date pattern with date/timestamp in front
        subdivisions = self._subdivide_str(line)
        for cached_position in self.cached_positions:
            if cached_position >= len(subdivisions):
                continue

            subdivision = subdivisions[cached_position]
            timestamp = self._try_interpret_str(subdivision)
            if timestamp is None:
                continue

            line_without_timestamp = line[len(subdivision) :].lstrip()
            return line_without_timestamp, timestamp

        for i, subdivision in enumerate(subdivisions):
            timestamp = self._try_interpret_str(subdivision)
            if timestamp is None:
                continue

            self.cached_positions.append(i)
            self.cached_positions.sort(reverse=True)

            line_without_timestamp = line[len(subdivision) :].lstrip()
            return line_without_timestamp, timestamp

        return None
