from dataclasses import dataclass, field
from io import StringIO
from typing import Any
from uuid import uuid4
import toml
from os.path import join
import logging

from nicegui import ui, events
from nicegui.element import Element

from drain3.template_miner_config import TemplateMinerConfig

from src.views import View
from src.widgets import settings_frame
from src.logs.parser import ParserManager, ParserSettingsSchema
from src.consts import CONFIGS_LOCAL_PATH
from src.views.select_files import SelectFiles

LABEL_TEXT_1 = "Parser depth ({}): "
LABEL_TEXT_2 = "Parser Simmilarity threshold ({}): "

logger = logging.getLogger("drain_setup")

@dataclass
class ParserSetup(View):
    """
    This view is responsible for configuring Parser.
    It supports saving/loading drain configs and tweaking individual options.
    """
    select_files: SelectFiles

    parser_depth: int = 10
    parser_sim_th: float = 0.4

    def show(self):
        with settings_frame() as outer:
            with ui.grid(columns=2):
                self.parser_depth_label = ui.label(LABEL_TEXT_1.format(self.parser_depth))
                self.parser_depth_slider = ui.slider(
                    min=2,
                    max=30,
                    step=1,
                    value=self.parser_depth,
                ).on(
                    "update:model-value",
                    lambda: self.state_changed.send(self),
                    throttle=1.0,
                    leading_events=False,
                ).bind_value_to(self, "drain_depth")
                self.parser_depth_slider.tailwind.width("40")

                self.parser_similarity_label = ui.label(LABEL_TEXT_2.format(self.parser_sim_th))
                self.parser_similarity_slider = ui.slider(
                    min=0,
                    max=1,
                    step=0.01,
                    value=self.parser_sim_th,
                ).on(
                    "update:model-value",
                    lambda: self.state_changed.send(self),
                    throttle=1.0,
                    leading_events=False,
                ).bind_value_to(self, "drain_sim_th")
                self.parser_similarity_slider.tailwind.width("40")

            with ui.row() as el:
                el.tailwind.margin("mt-2")
                el.tailwind.margin("mb-4")

                with ui.dialog() as dialog:
                    def on_file(event: events.UploadEventArguments):
                        try:
                            buffer = StringIO(event.content.read().decode("utf-8"))
                            self.load_config(buffer.read())
                            dialog.close()
                        except Exception as ex:
                            ui.notify(f"Uploading config file failed with: {str(ex)}")
                            return

                    dialog.tailwind.padding("p-40")
                    ui.upload(
                        label="Upload file here",
                        on_upload=on_file,
                        auto_upload=True,
                        max_files=1,
                    )

                ui.button("Load", on_click=dialog.open)
                ui.button("Save", on_click=lambda: self.save_config())


        return outer

    def update(self, sender: object = None):
        # self.masking_instructions_amount = max(0, self.masking_instructions_amount)
        self.parser_depth_label.text = LABEL_TEXT_1.format(self.parser_depth)
        self.parser_depth_slider.value = self.parser_depth
        self.parser_similarity_label.text = LABEL_TEXT_2.format(self.parser_sim_th)
        self.parser_similarity_slider.value = self.parser_sim_th
        # self.masking_n.value = self.masking_instructions_amount

        # Update masking instructions view
        # with self.masking_instructions_container:
        #     while self.masking_instructions_amount < len(self.masking_instructions):
        #         self.masking_instructions.pop().clear()

        #     while self.masking_instructions_amount > len(self.masking_instructions):
        #         masking_instruction = MaskingInstructionSelection()
        #         masking_instruction.show()
        #         masking_instruction.state_changed.connect(
        #             lambda _: self.state_changed.send(self), weak=False
        #         )
        #         self.masking_instructions.append(masking_instruction)

    def build_drain_config(self) -> TemplateMinerConfig:
        config = TemplateMinerConfig()
        config.parser_sim_th = self.parser_sim_th
        config.parser_depth = self.parser_depth
        return config

    def build_parser(self) -> ParserManager:
        return ParserManager(self.build_drain_config())

    def save_config(self):
        schema = ParserSettingsSchema()
        dump: dict = schema.dump(self.build_drain_config())
        config_path = join(CONFIGS_LOCAL_PATH, f"{uuid4()}.toml")
        with open(config_path, "w") as f:
            toml.dump(dump, f)

        ui.download(config_path)

    def load_config(self, config: str):
        schema = ParserSettingsSchema()
        obj = toml.loads(config)
        parsed_config: dict[str, Any] = schema.load(obj)
        self.parser_depth = parsed_config.get("drain_depth")
        self.parser_sim_th = parsed_config.get("drain_sim_th")

        # for i in self.masking_instructions:
        #     i.clear()
        # self.masking_instructions.clear()

        # with self.masking_instructions_container:
        #     for instr in parsed_config.get("masking_instructions"):
        #         instruction = MaskingInstructionSelection()
        #         instruction.show()
        #         instruction.instruction = instr
        #         instruction.state_changed.connect(
        #             lambda _: self.state_changed.send(self), weak=False
        #         )
        #         self.masking_instructions.append(instruction)
        #     self.masking_instructions_amount = len(self.masking_instructions)
        self.state_changed.send(self)
