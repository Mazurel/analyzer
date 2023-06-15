from src.views import Footer, SelectFiles, HeuristicSetup, LogView, DrainSetup

from nicegui import ui


class NiceGuiView:
    def start(self):
        ui.query("body").tailwind.background_color("zinc-200")
        ui.query(".nicegui-content").tailwind.align_items("center")

        ui.markdown("# Log analyzer")
        ui.markdown("Upload Grand truth and checked file to see analysis result")

        self.file_select = SelectFiles()
        self.drain_setup = DrainSetup()
        self.heuristic_setup = HeuristicSetup()
        self.log_view = LogView(
            drain_setup=self.drain_setup,
            heuristic_setup=self.heuristic_setup,
            select_files=self.file_select,
        )
        self.footer = Footer()

        self.file_select.show()
        self.drain_setup.show()
        self.heuristic_setup.show()
        self.log_view.show()
        self.footer.show()

        ui.run()
