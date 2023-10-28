from views.drain_setup import DrainSetup
from views.brain_setup import BrainSetup
from src.views.select_files import SelectFiles

class ParserSetupFacade():
    def __init__(self, parser_name: str, select_files: SelectFiles) -> None:
        if parser_name == "Drain":
            self.parser_setup = DrainSetup(select_files=select_files)
        elif parser_name == "Brain":
            self.parser_setup = BrainSetup(select_files=select_files)
        else:
            # Should never happen
            assert(True)

        return self.parser_setup