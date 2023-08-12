from dataclasses import dataclass

from blinker import Signal
from nicegui.element import Element


@dataclass
class View:
    '''
    `View` is a base building block of all UIs in this application.
    This objects are expected to have internal state.
    When the state changes, the `state_changed` signal should be emitted,
    which automatically should start `self.update()` method.
    This method should update the view based on state accordingly.

    `View` objects should use `nicegui.ui` object/namespace to dynamically
    create and update the DOM.

    NOTE:
    - Views may be depended on one another. In such case, `state_changed` event
      may also update parent view.
    - All views should be dataclasses !
    '''
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

