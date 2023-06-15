from dataclasses import dataclass

from nicegui import ui
from src.views import View
from src.logs.drain import DrainManager

LABEL_TEXT_1 = "Drain depth ({}): "
LABEL_TEXT_2 = "Drain Simmilarity threshold ({}): "


@dataclass
class DrainSetup(View):
    drain_depth: int = 10
    drain_sim_th: float = 0.4

    def show(self):
        with ui.grid(2, 2) as el:
            el.tailwind.border_color("indigo-300").border_width("2").padding(
                "p-4"
            ).border_radius("lg")
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
            ).bind_value_to(
                self, "drain_depth"
            ).tailwind.width(
                "40"
            )

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
            ).bind_value_to(
                self, "drain_sim_th"
            ).tailwind.width(
                "40"
            )
        return el

    def update(self, sender: object = None):
        self.dd_label.text = LABEL_TEXT_1.format(self.drain_depth)
        self.dst_label.text = LABEL_TEXT_2.format(self.drain_sim_th)

    def build_drain(self) -> DrainManager:
        drain = DrainManager()
        drain.config.drain_sim_th = self.drain_sim_th
        drain.config.drain_depth = self.drain_depth
        return drain
