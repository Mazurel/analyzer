from dataclasses import dataclass, field

from nicegui import ui
from nicegui.element import Element

from drain3.template_miner_config import TemplateMinerConfig

from src.views import View
from src.logs.drain import DrainManager, MaskingInstruction

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
            ui.input(
                label="Masking instruction name",
                on_change=lambda: self.state_changed.send(self),
            ).bind_value_to(self, "instruction_name")
            ui.input(
                label="Masking instruction regex",
                on_change=lambda: self.state_changed.send(self),
            ).bind_value_to(self, "instruction_regex")

        return el

    def update(self, sender: object = None):
        self.ready = len(self.instruction_name) > 0 and len(self.instruction_regex) > 0

    def get_instruction(self):
        return MaskingInstruction(self.instruction_regex, self.instruction_name)


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
                ui.slider(
                    min=2,
                    max=30,
                    step=1,
                    value=self.drain_depth,
                ).on(
                    "update:model-value",
                    lambda: self.state_changed.send(self),
                    throttle=1.0,
                    leading_events=False,
                ).bind_value_to(self, "drain_depth").tailwind.width("40")

                self.dst_label = ui.label(LABEL_TEXT_2.format(self.drain_sim_th))
                ui.slider(
                    min=0,
                    max=1,
                    step=0.01,
                    value=self.drain_sim_th,
                ).on(
                    "update:model-value",
                    lambda: self.state_changed.send(self),
                    throttle=1.0,
                    leading_events=False,
                ).bind_value_to(self, "drain_sim_th").tailwind.width("40")

            self.masking_instructions_container = ui.element("div")
            ui.number(
                "Masking instructions",
                value=self.masking_instructions_amount,
                on_change=self.update,
            ).bind_value_to(self, "masking_instructions_amount")
        return outer

    def update(self, sender: object = None):
        self.dd_label.text = LABEL_TEXT_1.format(self.drain_depth)
        self.dst_label.text = LABEL_TEXT_2.format(self.drain_sim_th)

        with self.masking_instructions_container:
            while self.masking_instructions_amount > len(self.masking_instructions):
                masking_instruction = MaskingInstructionSelection()
                masking_instruction.show()
                masking_instruction.state_changed.connect(
                    lambda _: self.state_changed.send(self), weak=False
                )
                self.masking_instructions.append(masking_instruction)

    def build_drain(self) -> DrainManager:
        config = TemplateMinerConfig()
        config.drain_sim_th = self.drain_sim_th
        config.drain_depth = self.drain_depth

        config.masking_instructions.clear()
        for instruction in self.masking_instructions:
            if instruction.ready:
                config.masking_instructions.append(instruction.get_instruction())

        return DrainManager(config)
