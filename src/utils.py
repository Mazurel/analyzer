from src.views import SelectParser, BrainSetup, DrainSetup, SelectFiles

def get_parser_setup(select_parser: SelectParser, select_files: SelectFiles):
    parser_name = select_parser.parser_cap
    if parser_name == "Drain":
        return DrainSetup(select_files=select_files)
    elif parser_name == "Brain":
        return BrainSetup(select_files=select_files)
    else:
        # Should never happen
        assert(True)