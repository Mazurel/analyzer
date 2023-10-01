from typing import Optional

from dateutil import parser as date_parser


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


def extract_timestamp(line: str) -> Optional[float]:
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
            text = line[1:end_index]
            if (t := _try_interpret_str(text)) is not None:
                return t

    # Check for date pattern with date/timestamp in front
    substr = line
    while True:
        if (date := _try_interpret_str(substr)) is not None:
            return date

        new_end_index = substr.find(" ")
        if new_end_index == -1:
            break

        substr = substr[:new_end_index].strip()

    return None

