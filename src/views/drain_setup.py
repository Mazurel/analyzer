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
from src.logs.drain import DrainManager, MaskingInstruction, DrainSettingsSchema
from src.consts import CONFIGS_LOCAL_PATH
from src.views.select_files import SelectFiles
from src.logs.finder import find_masking_instructions
from src.views.parser_setup import ParserSetup

LABEL_TEXT_1 = "Drain depth ({}): "
LABEL_TEXT_2 = "Drain Simmilarity threshold ({}): "

logger = logging.getLogger("drain_setup")


@dataclass
class MaskingInstructionSelection(View):
    ready: bool = False
    instruction_name: str = ""
    instruction_regex: str = ""

    async def show(self) -> Element:
        with ui.grid(rows=1, columns=2) as el:
            el.tailwind.width("full")
            self.l1 = ui.input(
                label="Masking instruction name",
                on_change=self._emit_state_change,
            ).bind_value_to(self, "instruction_name")
            self.l2 = ui.input(
                label="Masking instruction regex",
                on_change=self._emit_state_change,
            ).bind_value_to(self, "instruction_regex")

        self.container = el
        return el

    async def update(self, sender: object = None):
        self.l1.value = self.instruction_name
        self.l2.value = self.instruction_regex

        self.ready = len(self.instruction_name) > 0 and len(self.instruction_regex) > 0

    @property
    def instruction(self):
        return MaskingInstruction(self.instruction_regex, self.instruction_name)

    async def update_instruction(self, val: MaskingInstruction):
        self.instruction_regex = val.pattern
        self.instruction_name = val.mask_with
        await self._emit_state_change()

    async def clear(self):
        try:
            self.container.clear()
            del self.container
        except AttributeError:
            # There is no `container` yet defined
            pass


@dataclass
class DrainSetup(ParserSetup):
    """
    This view is responsible for configuring Drain.
    It supports saving/loading drain configs and tweaking individual options.
    """

    select_files: SelectFiles

    drain_depth: int = 10
    drain_sim_th: float = 0.4
    masking_instructions_amount: int = 0
    masking_instructions: list[MaskingInstructionSelection] = field(
        default_factory=lambda: []
    )

    async def show(self):
        with settings_frame() as outer:
            with ui.grid(columns=2):
                self.drain_depth_label = ui.label(LABEL_TEXT_1.format(self.drain_depth))
                self.drain_depth_slider = (
                    ui.slider(
                        min=2,
                        max=30,
                        step=1,
                        value=self.drain_depth,
                    )
                    .on(
                        "update:model-value",
                        self._emit_state_change,
                        throttle=1.0,
                        leading_events=False,
                    )
                    .bind_value_to(self, "drain_depth")
                )
                self.drain_depth_slider.tailwind.width("40")

                self.drain_similarity_label = ui.label(
                    LABEL_TEXT_2.format(self.drain_sim_th)
                )
                self.drain_similarity_slider = (
                    ui.slider(
                        min=0,
                        max=1,
                        step=0.01,
                        value=self.drain_sim_th,
                    )
                    .on(
                        "update:model-value",
                        self._emit_state_change,
                        throttle=1.0,
                        leading_events=False,
                    )
                    .bind_value_to(self, "drain_sim_th")
                )
                self.drain_similarity_slider.tailwind.width("40")

            self.masking_instructions_container = ui.element("div")
            self.masking_n = ui.number(
                "Masking instructions",
                value=self.masking_instructions_amount,
                on_change=self.update,
            ).bind_value_to(self, "masking_instructions_amount")

            with ui.row() as el:
                el.tailwind.margin("mt-2")
                el.tailwind.margin("mb-4")

                with ui.dialog() as dialog:

                    async def on_file(event: events.UploadEventArguments):
                        try:
                            buffer = StringIO(event.content.read().decode("utf-8"))
                            await self.load_config(buffer.read())
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

            ui.button(
                "Automatically find masking instructions",
                on_click=self.automatically_find_masking_instructions,
            )

        return outer

    async def update(self, sender: object = None):
        self.masking_instructions_amount = max(0, self.masking_instructions_amount)
        self.drain_depth_label.text = LABEL_TEXT_1.format(self.drain_depth)
        self.drain_depth_slider.value = self.drain_depth
        self.drain_similarity_label.text = LABEL_TEXT_2.format(self.drain_sim_th)
        self.drain_similarity_slider.value = self.drain_sim_th
        self.masking_n.value = self.masking_instructions_amount

        # Update masking instructions view
        with self.masking_instructions_container:
            while self.masking_instructions_amount < len(self.masking_instructions):
                await self.masking_instructions.pop().clear()

            while self.masking_instructions_amount > len(self.masking_instructions):
                masking_instruction = MaskingInstructionSelection()
                await masking_instruction.show()
                masking_instruction.on_state_changed(self._emit_state_change_anyargs)
                self.masking_instructions.append(masking_instruction)

    def build_parser_config(self) -> TemplateMinerConfig:
        config = TemplateMinerConfig()
        config.drain_sim_th = self.drain_sim_th
        config.drain_depth = self.drain_depth
        config.masking_instructions = [
            instruction.instruction
            for instruction in self.masking_instructions
            if instruction.ready
        ]
        return config

    def build_parser(self) -> DrainManager:
        return DrainManager(self.build_parser_config())

    def save_config(self):
        schema = DrainSettingsSchema()
        dump: dict = schema.dump(self.build_parser_config())
        config_path = join(CONFIGS_LOCAL_PATH, f"{uuid4()}.toml")
        with open(config_path, "w") as f:
            toml.dump(dump, f)

        ui.download(config_path)

    async def load_config(self, config: str):
        schema = DrainSettingsSchema()
        obj = toml.loads(config)
        parsed_config: dict[str, Any] = schema.load(obj)
        self.drain_depth = parsed_config.get("drain_depth")
        self.drain_sim_th = parsed_config.get("drain_sim_th")

        for i in self.masking_instructions:
            await i.clear()
        self.masking_instructions.clear()

        with self.masking_instructions_container:
            for instr in parsed_config.get("masking_instructions"):
                instruction = MaskingInstructionSelection()
                await instruction.show()
                await instruction.update_instruction(instr)
                instruction.on_state_changed(self._emit_state_change_anyargs)
                self.masking_instructions.append(instruction)
            self.masking_instructions_amount = len(self.masking_instructions)
        await self._emit_state_change()

    async def automatically_find_masking_instructions(self):
        if self.select_files.checked is None:
            ui.notify("No checked file loaded !", type="negative")
            return

        new_instructions = find_masking_instructions(self.select_files.checked)
        for new_instruction in new_instructions:
            valid = True
            for instruction in self.masking_instructions:
                if (
                    new_instruction.regex == instruction.instruction_regex
                    or new_instruction.name == instruction.instruction_name
                ):
                    valid = False
                    break

            if not valid:
                continue

            logger.info(f"Automatically adding {new_instruction} masking instruction")

            with self.masking_instructions_container:
                new_masking_instruction = MaskingInstructionSelection()
                await new_masking_instruction.show()
                await new_masking_instruction.update_instruction(
                    MaskingInstruction(new_instruction.regex, new_instruction.name)
                )

                self.masking_instructions.append(new_masking_instruction)
                self.masking_instructions_amount += 1
