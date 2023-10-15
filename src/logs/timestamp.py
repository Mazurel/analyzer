from typing import Optional
from logging import getLogger

from dateutil import parser as date_parser

logger = getLogger("timestamps")

def _try_interpret_str(s: str) -> Optional[float]:
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


def extract_timestamp(line: str) -> Optional[tuple[str, float]]:
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
                return line[end_index+1:].lstrip(), timestamp

    # Check for date pattern with date/timestamp in front
    substr = line
    while True:
        new_end_index = substr.rfind(" ")
        substr = substr[:new_end_index].strip()

        if new_end_index == -1:
            break

        if (timestamp := _try_interpret_str(substr)) is not None:
            logger.debug(f"Found at: {substr}")
            return line[new_end_index:].lstrip(), timestamp

    return None

