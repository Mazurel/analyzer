from dataclasses import dataclass, field
from io import StringIO
from typing import Any
from uuid import uuid4
import toml
from os.path import join

from nicegui import ui, app, events
from nicegui.element import Element

from drain3.template_miner_config import TemplateMinerConfig

from src.views import View
from src.logs.drain import DrainManager, MaskingInstruction, DrainSettingsSchema
from src.consts import CONFIGS_FOLDER

LABEL_TEXT_1 = "Drain depth ({}): "
LABEL_TEXT_2 = "Drain Simmilarity threshold ({}): "


@dataclass
class MaskingInstructionSelection(View):
    ready: bool = False
    instruction_name: str = ""
    instruction_regex: str = ""

    def show(self) -> Element:
        with ui.grid(1, 2) as el:
            el.tailwind.width("full")
            self.l1 = ui.input(
                label="Masking instruction name",
                on_change=lambda: self.state_changed.send(self),
            ).bind_value_to(self, "instruction_name")
            self.l2 = ui.input(
                label="Masking instruction regex",
                on_change=lambda: self.state_changed.send(self),
            ).bind_value_to(self, "instruction_regex")

        self.container = el
        return el

    def update(self, sender: object = None):
        self.l1.value = self.instruction_name
        self.l2.value = self.instruction_regex

        self.ready = len(self.instruction_name) > 0 and len(self.instruction_regex) > 0

    @property
    def instruction(self):
        return MaskingInstruction(self.instruction_regex, self.instruction_name)

    @instruction.setter
    def instruction(self, val: MaskingInstruction):
        self.instruction_regex = val.pattern
        self.instruction_name = val.mask_with
        self.state_changed.send(self)
    
    def clear(self):
        self.container.clear()
        del self.container


@dataclass
class DrainSetup(View):
    drain_depth: int = 10
    drain_sim_th: float = 0.4
    masking_instructions_amount: int = 0
    masking_instructions: list[MaskingInstructionSelection] = field(
        default_factory=lambda: []
    )

    def show(self):
        with ui.element("div") as outer:
            outer.tailwind.border_color("indigo-300").border_width("2").padding(
                "p-4"
            ).border_radius("lg")
            with ui.grid(columns=2):
                self.dd_label = ui.label(LABEL_TEXT_1.format(self.drain_depth))
                self.dd_slider = ui.slider(
                    min=2,
                    max=30,
                    step=1,
                    value=self.drain_depth,
                ).on(
                    "update:model-value",
                    lambda: self.state_changed.send(self),
                    throttle=1.0,
                    leading_events=False,
                ).bind_value_to(self, "drain_depth")
                self.dd_slider.tailwind.width("40")

                self.dst_label = ui.label(LABEL_TEXT_2.format(self.drain_sim_th))
                self.dst_slider = ui.slider(
                    min=0,
                    max=1,
                    step=0.01,
                    value=self.drain_sim_th,
                ).on(
                    "update:model-value",
                    lambda: self.state_changed.send(self),
                    throttle=1.0,
                    leading_events=False,
                ).bind_value_to(self, "drain_sim_th")
                self.dst_slider.tailwind.width("40")

            self.masking_instructions_container = ui.element("div")
            self.masking_n = ui.number(
                "Masking instructions",
                value=self.masking_instructions_amount,
                on_change=self.update,
            ).bind_value_to(self, "masking_instructions_amount")

            with ui.row() as el:
                el.tailwind.margin("mt-2")

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
                ui.button("Save", on_click=lambda: self.saveconfig())

        return outer

    def update(self, sender: object = None):
        self.masking_instructions_amount = max(0, self.masking_instructions_amount)
        self.dd_label.text = LABEL_TEXT_1.format(self.drain_depth)
        self.dd_slider.value = self.drain_depth
        self.dst_label.text = LABEL_TEXT_2.format(self.drain_sim_th)
        self.dst_slider.value = self.drain_sim_th
        self.masking_n.value = self.masking_instructions_amount

        with self.masking_instructions_container:
            while self.masking_instructions_amount < len(self.masking_instructions):
                self.masking_instructions.pop().clear()

            while self.masking_instructions_amount > len(self.masking_instructions):
                masking_instruction = MaskingInstructionSelection()
                masking_instruction.show()
                masking_instruction.state_changed.connect(
                    lambda _: self.state_changed.send(self), weak=False
                )
                self.masking_instructions.append(masking_instruction)

    def build_drain_config(self) -> TemplateMinerConfig:
        config = TemplateMinerConfig()
        config.drain_sim_th = self.drain_sim_th
        config.drain_depth = self.drain_depth
        config.masking_instructions = [
            instruction.instruction
            for instruction in self.masking_instructions
            if instruction.ready
        ]
        return config

    def build_drain(self) -> DrainManager:
        return DrainManager(self.build_drain_config())

    def saveconfig(self):
        schema = DrainSettingsSchema()
        dump: dict = schema.dump(self.build_drain_config())
        config_path = join(CONFIGS_FOLDER, f"{uuid4()}.toml")
        with open(config_path, "w") as f:
            toml.dump(dump, f)

        ui.download(config_path)

    def load_config(self, config: str):
        schema = DrainSettingsSchema()
        obj = toml.loads(config)
        parsed_config: dict[str, Any] = schema.load(obj)
        self.drain_depth = parsed_config.get("drain_depth")
        self.drain_sim_th = parsed_config.get("drain_sim_th")

        for i in self.masking_instructions:
            i.clear()
        self.masking_instructions.clear()

        with self.masking_instructions_container:
            for instr in parsed_config.get("masking_instructions"):
                instruction = MaskingInstructionSelection()
                instruction.show()
                instruction.instruction = instr
                instruction.state_changed.connect(
                    lambda _: self.state_changed.send(self), weak=False
                )
                self.masking_instructions.append(instruction)
            self.masking_instructions_amount = len(self.masking_instructions)
        self.state_changed.send(self)
