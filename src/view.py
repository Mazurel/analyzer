from src.views import Footer, SelectFiles, HeuristicSetup, LogView, show_in

from nicegui import ui


class NiceGuiView:
    def start(self):
        ui.query("body").tailwind.background_color("zinc-200")
        ui.query(".nicegui-content").tailwind.align_items("center")

        ui.markdown("# Log analyzer")
        ui.markdown("Upload Grand truth and checked file to see analysis result")

        self.file_select = SelectFiles()
        self.heuristic_setup = HeuristicSetup()
        self.log_view = LogView(self.heuristic_setup, self.file_select)
        self.footer = Footer()

        show_in(ui.row(), self.file_select)
        show_in(ui.row(), self.heuristic_setup)
        show_in(ui.element("div"), self.log_view)
        show_in(ui.element("footer"), self.footer)

        ui.run()
