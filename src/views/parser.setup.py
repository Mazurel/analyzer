from dataclasses import dataclass

from src.views import View
from src.views.select_files import SelectFiles

@dataclass
class ParserSetup(View):
    select_files: SelectFiles

    def build_parser_config(self) -> ParserConfig:
        raise NotImplementedError()

    def build_drain(self) -> ParserManager:
        return ParserManager(self.build_parser_config())

    def save_config(self):
        raise NotImplementedError()

    def load_config(self, config: str):
        raise NotImplementedError()
