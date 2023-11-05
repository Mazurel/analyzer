from dataclasses import dataclass
from typing import Optional

from nicegui import ui
from nicegui.elements.label import Label
from src.views import View


@dataclass
class SelectParser(View):
    """
    This view is responsible for selecting parser.
    """
    label: Optional[Label] = None
    parsers = ["Brain", "Drain"]
    parser_cap: str = parsers[0]

    def show(self):
        with ui.row() as r:
            self.label = ui.label()
            self.label.text = f"Select Parser: "
            self._parser_select = (
                ui.select(
                    options=self.parsers,
                    value=self.parsers[0]
                )
                .on(
                    "update:model-value",
                    lambda: self.state_changed.send(self),
                    throttle=1.0,
                    leading_events=False,
                )
                .bind_value_to(self, "parser_cap")
            )
        return r
