from src.views.view import View

from nicegui import ui


class Footer(View):
    def show(self):
        with ui.element("footer") as f:
            f.tailwind.margin("mt-10")
            ui.label("This tool is created for Research Project: ").tailwind.display(
                "inline"
            )
            ui.link(
                "Discovery and visualization of meaningful information in applications logs",
                "https://projektgrupowy.eti.pg.gda.pl/editions/18/projects/4881",
            ).tailwind.font_style("italic").display("inline")
        return f

    def update(self, sender: object = None):
        pass
