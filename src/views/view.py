from dataclasses import dataclass
from typing import Callable, Coroutine, Any

from blinker import Signal
from nicegui.element import Element


@dataclass
class View:
    """
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
    """

    def __post_init__(self):
        self.state_changed = Signal()
        self.state_changed.connect(self.update)

    async def show(self) -> Element:
        """
        Show the view inside into view-initialized container.
        This method should return root of such object.

        NOTE:
        - This method should be overrided
        """
        raise NotImplementedError()

    async def update(self, sender: object = None):
        """
        This method is called when view should be updated.
        It is needed only when view has some dynamic data.
        It also has sender object parameter based on which user can check who has triggered the update.
        It is designed to work with `blinker`.

        NOTE:
        - This method can be overrided
        """
        pass

    async def _emit_state_change(self):
        """Emit state change event. Calls all connected callbacks."""
        await self.state_changed.send_async(self)

    async def _emit_state_change_anyargs(self, *args, **kwargs):
        """Like, `_emit_state_change`, but takes any inputs."""
        await self._emit_state_change()

    def on_state_changed(self, callback: Callable[[object], Coroutine[Any, Any, None]]):
        self.state_changed.connect(callback, weak=False)
