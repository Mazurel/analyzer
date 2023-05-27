from ..view import View

from nicegui import ui

class NiceGuiView(View):
    def start():
        ui.label('Hello NiceGUI!')
        ui.run()
