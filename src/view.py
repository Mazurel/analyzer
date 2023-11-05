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

from src.utils import get_parser_setup
from fastapi import FastAPI
from nicegui import ui, app, Client

logging.basicConfig(
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
    level=logging.INFO,
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


def start(fastapi_app: FastAPI):
    states: dict[uuid.UUID, State] = {}

    @ui.page("/")
    async def index(client: Client):
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

        await state.file_select.show()
        await state.parser_select.show()
        await state.parser_setup.show()
        await state.heuristic_setup.show()
        await state.log_view.show()
        await state.footer.show()
        logger.info("Succesfully initialized")

        await client.connected(timeout=30)
        logger.info("Client connected !")

    app.add_static_files("/configs", "configs/")
    ui.run_with(
        fastapi_app,
        storage_secret="123",
        reconnect_timeout=30.0,
        binding_refresh_interval=0.2,
    )
