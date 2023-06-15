from dataclasses import dataclass, field
from typing import Optional

from blinker import Signal
from nicegui import ui
from nicegui.element import Element
from nicegui.elements.label import Label
from src.views import View


@dataclass
class HeuristicSetup(View):
    state_changed: Signal = field(default_factory=lambda: Signal())
    heuristic_cap: float = 0.5
    label: Optional[Label] = None

    def show(self, _: Element):
        self.label = ui.label()
        self._heuristic_slider = (
            ui.slider(
                min=0,
                max=1,
                step=0.01,
                value=self.heuristic_cap,
                on_change=lambda: self.state_changed.send(self),
            )
            .bind_value_to(self, "heuristic_cap")
            .tailwind.width("40")
        )
        self.state_changed.connect(self.update)

    def update(self, sender: object = None):
        assert self.label is not None
        self.label.text = f"Heuristic Cap ({self.heuristic_cap}): "        
