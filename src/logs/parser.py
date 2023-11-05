from abc import ABC
from src.logs.types import LogFile

class ParserManager(ABC):
    def __init__(self, config) -> None:
        raise NotImplementedError()
    
    def learn(self, file: LogFile):
        raise NotImplementedError()
    
    def annotate(self, file: LogFile):
        raise NotImplementedError()
