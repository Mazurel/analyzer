import re

from src.logs.types import LogFile, MaskingInstruction
from src.consts import COMMON_MASKING_INSTRUCTIONS

MIN_MASKING_INSTRUCTIONS = 5

def find_masking_instructions(file: LogFile) -> list[MaskingInstruction]:
    '''
    Find all known masking instructions inside `LogFile`, that match at least
    few lines inside the log file.
    '''
    return [
        instruction
        for instruction in COMMON_MASKING_INSTRUCTIONS
        if sum(
            re.search(instruction.regex, line.line) is not None
            for line in file.lines
        ) >= MIN_MASKING_INSTRUCTIONS
    ]
