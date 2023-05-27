from typing import Protocol

from src.nicegui.view import NiceGuiView

class View(Protocol):
    def start():
        ...

def get_view() -> View:
    return NiceGuiView()
