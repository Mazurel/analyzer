from dataclasses import dataclass

from blinker import Signal
from nicegui.element import Element


@dataclass
class View:
    def __post_init__(self):
        self.state_changed = Signal()
        self.state_changed.connect(self.update)

    def show(self) -> Element:
        '''
        Show the view inside into view-initialized container.
        This method should return root of such object.
        '''
        raise NotImplementedError()

    def update(self, sender: object = None):
        '''
        This method is called when view should be updated.
        It is needed only when view has some dynamic data.
        It also has sender object parameter based on which user can check who has triggered the update.
        It is designed to work with `blinker`.
        '''
        pass

