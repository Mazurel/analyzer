from dataclasses import dataclass
from typing import Optional

from nicegui import ui
from nicegui.elements.label import Label
from src.views import View


@dataclass
class HeuristicSetup(View):
    """
    This view is responsible for configuring heuristics.
    Currently it only contains heuristic cap slider.
    """

    heuristic_cap: float = 0.5
    label: Optional[Label] = None

    async def show(self):
        with ui.row() as r:
            self.label = ui.label()
            self._heuristic_slider = (
                ui.slider(
                    min=0,
                    max=1,
                    step=0.01,
                    value=self.heuristic_cap,
                )
                .on(
                    "update:model-value",
                    self._emit_state_change,
                    throttle=1.0,
                    leading_events=False,
                )
                .bind_value_to(self, "heuristic_cap")
                .tailwind.width("40")
            )
            await self.update()
        return r

    async def update(self, sender: object = None):
        assert self.label is not None
        self.label.text = f"Importance threshold ({self.heuristic_cap}): "
