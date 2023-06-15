from src.views.view import View

from nicegui.element import Element
from nicegui import ui


class Footer(View):
    def show(self, container: Element):
        container.tailwind.margin("mt-10")
        ui.label("This tool is created for Research Project: ").tailwind.display(
            "inline"
        )
        ui.link(
            "Discovery and visualization of meaningful information in applications logs",
            "https://projektgrupowy.eti.pg.gda.pl/editions/18/projects/4881",
        ).tailwind.font_style("italic").display("inline")

    def update(self, sender: object = None):
        pass
