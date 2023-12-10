import uuid
import logging
import sys

from src.views import (
    Footer,
    SelectFiles,
    SelectParser,
    HeuristicSetup,
    SmartLogView,
    DrainSetup,
    BrainSetup,
    LogsSetup,
)

from nicegui import ui, app
from src.utils import get_parser_setup

logging.basicConfig(
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
    level=logging.DEBUG,
)


class State:
    def __init__(self) -> None:
        self.file_select = SelectFiles()
        self.parser_select = SelectParser()
        self.parser_setup = get_parser_setup(self.parser_select, self.file_select)
        self.heuristic_setup = HeuristicSetup()
        self.log_view = SmartLogView(
            parser_setup=self.parser_setup,
            heuristic_setup=self.heuristic_setup,
            select_files=self.file_select,
            select_parser=self.parser_select
        )
        self.footer = Footer()


states: dict[uuid.UUID, State] = {}


@ui.page("/")
def index():
    logger = logging.getLogger("index")
    try:
        user_id = uuid.UUID(app.storage.browser.get("id"))
        if not isinstance(user_id, uuid.UUID):
            raise KeyError()
    except KeyError:
        user_id = uuid.uuid4()
        app.storage.browser["id"] = str(user_id)

    if user_id in states.keys():
        state = states[user_id]
    else:
        state = State()
        states[user_id] = state
        logger.info(f"New state for user {user_id} !")

    ui.query("body").tailwind.background_color("zinc-200")
    ui.query(".nicegui-content").tailwind.align_items("center")

    ui.markdown("# Log analyzer")
    ui.markdown("Upload Grand truth and checked file to see analysis result")

    state.file_select.show()
    state.parser_select.show()
    parser_setup_div = ui.element("div")
    with parser_setup_div:
        state.parser_setup.show()
    # state.parser_setup.clear()
    state.heuristic_setup.show()
    state.log_view.show(parser_setup_div)
    state.footer.show()

    logger.info("Succesfully initialized")


def start():
    app.add_static_files("/configs", "configs/")
    # TODO: Use better secret
    ui.run(storage_secret="123")
