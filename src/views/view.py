from typing import Protocol

from nicegui.element import Element

class View(Protocol):
    def show(self, container: Element):
        '''
        Show the view inside given `container`.
        If the view needs to access this element in the future,
        it should store it inside its state.
        '''
        ...

    def update(self, sender: object = None):
        '''
        This method is called when view should be updated.
        It is needed only when view has some dynamic data.
        It also has sender object parameter based on which user can check who has triggered the update.
        It is designed to work with `blinker`.
        '''
        ...

def show_in(container: Element, view: View):
    with container:
        view.show(container)
