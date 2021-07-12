#!/usr/bin/env python
"""A simple example of a Notepad-like text editor."""

import datetime
from asyncio import Future, ensure_future

from prompt_toolkit.application import Application
from prompt_toolkit.application.current import get_app
from prompt_toolkit.completion import Completer, PathCompleter
from prompt_toolkit.filters import Condition
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.key_processor import KeyPressEvent
from prompt_toolkit.layout import ScrollablePane
from prompt_toolkit.layout.containers import (
    ConditionalContainer,
    Float,
    HSplit,
    VSplit,
    Window,
    WindowAlign,
)
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.menus import CompletionsMenu
from prompt_toolkit.lexers import DynamicLexer, PygmentsLexer
from prompt_toolkit.search import start_search
from prompt_toolkit.shortcuts import set_title
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import (
    Button,
    Dialog,
    Frame,
    Label,
    MenuContainer,
    MenuItem,
    SearchToolbar,
    TextArea,
)


class ApplicationState:
    """
    Application state.

    For the simplicity, we store this as a global, but better would be to
    instantiate this as an object and pass at around.
    """

    show_status_bar = True
    current_path = None


# TODO make something like this that will pull up the side file menu
def get_statusbar_text() -> None:
    """Gets status bar opens menu"""
    return " Press Ctrl-K to open menu. "


def get_statusbar_right_text() -> None:
    """Get status bar for the right text?"""
    return " {}:{}  ".format(
        text_field.document.cursor_position_row + 1,
        text_field.document.cursor_position_col + 1,
    )


search_toolbar = SearchToolbar()
text_field = TextArea(
    lexer=DynamicLexer(
        lambda: PygmentsLexer.from_filename(
            ApplicationState.current_path or ".txt", sync_from_start=False
        )
    ),
    scrollbar=True,
    line_numbers=True,
    search_field=search_toolbar,
)


class PopUpDialog:
    """For type annotation of Dialog box classes"""

    pass


class TextInputDialog(PopUpDialog):
    """Text Input for the open dialog box"""

    def __init__(
        self, title: str = "", label_text: str = "", completer: Completer = None
    ):
        self.future = Future()

        # TODO: fix this type annotation
        def accept_text(buf: object) -> bool:
            """Accepts text"""
            get_app().layout.focus(ok_button)
            buf.complete_state = None
            return True

        def accept() -> None:
            """Accept"""
            self.future.set_result(self.text_area.text)

        def cancel() -> None:
            """Cancel"""
            self.future.set_result(None)

        self.text_area = TextArea(
            completer=completer,
            multiline=False,
            width=D(preferred=40),
            accept_handler=accept_text,
        )

        ok_button = Button(text="OK", handler=accept)
        cancel_button = Button(text="Cancel", handler=cancel)

        self.dialog = Dialog(
            title=title,
            body=HSplit([Label(text=label_text), self.text_area]),
            buttons=[ok_button, cancel_button],
            width=D(preferred=80),
            modal=True,
        )

    def __pt_container__(self):
        return self.dialog


# TODO this thing


class ScrollMenuDialog(PopUpDialog):
    """Scroll menu added to the info tab dialog box"""

    def __init__(self, title: str, text: str):
        self.future = Future()

        def set_done() -> None:
            """Future object when done return None"""
            self.future.set_result(None)

        ok_button = Button(text="OK", handler=(lambda: set_done()))

        self.dialog = Dialog(
            title=title,
            body=HSplit(
                [
                    Label("ScrollContainer Demo"),
                    Frame(
                        ScrollablePane(
                            HSplit(
                                [
                                    Frame(
                                        TextArea(
                                            text=f"label-{i}",
                                            # completer=animal_completer,
                                        )
                                    )
                                    for i in range(20)
                                ]
                            )
                        ),
                    ),
                ]
            ),
            buttons=[ok_button],
            width=D(preferred=80),
            modal=True,
        )

    def __pt_container__(self):
        return self.dialog


class MessageDialog(PopUpDialog):
    """About tab dialog box"""

    def __init__(self, title: str, text: str):
        self.future = Future()

        def set_done() -> None:
            """Future object when done return None"""
            self.future.set_result(None)

        ok_button = Button(text="OK", handler=(lambda: set_done()))

        self.dialog = Dialog(
            title=title,
            body=HSplit([Label(text=text)]),
            buttons=[ok_button],
            width=D(preferred=80),
            modal=True,
        )

    def __pt_container__(self):
        return self.dialog


body = HSplit(
    [
        text_field,
        search_toolbar,
        ConditionalContainer(
            content=VSplit(
                [
                    Window(
                        FormattedTextControl(get_statusbar_text), style="class:status"
                    ),
                    Window(
                        FormattedTextControl(get_statusbar_right_text),
                        style="class:status.right",
                        width=9,
                        align=WindowAlign.RIGHT,
                    ),
                ],
                height=1,
            ),
            filter=Condition(lambda: ApplicationState.show_status_bar),
        ),
    ]
)

# Global key bindings.
bindings = KeyBindings()


@bindings.add("c-k")
def open_menu(event: KeyPressEvent) -> None:
    """Focus menu with Ctrl-K"""
    event.app.layout.focus(root_container.window)


@bindings.add("escape")
def close_menu(event: KeyPressEvent) -> None:
    """Focus text field."""
    event.app.layout.focus(text_field)


@bindings.add("c-n")
def create_new_file(event: KeyPressEvent) -> None:
    """Create new file with Ctrl-N"""
    do_new_file()


@bindings.add("c-s")
def save_file(event: KeyPressEvent) -> None:
    """Save file with Ctrl-S"""
    do_save_file()


@bindings.add("c-o")
def open_file(event: KeyPressEvent) -> None:
    """Save file with Ctrl-O"""
    do_open_file()


@bindings.add("c-q")
def exit_editor(event: KeyPressEvent) -> None:
    """Exit terminal with Ctrl-Q"""
    do_exit()


@bindings.add("c-a")
def select_all(event: KeyPressEvent) -> None:
    """Select all with Ctrl-A"""
    do_select_all()


@bindings.add("c-x")
def cut_text(event: KeyPressEvent) -> None:
    """Cut with Ctrl-X"""
    do_cut()


@bindings.add("c-c")
def copy_text(event: KeyPressEvent) -> None:
    """Copy with Ctrl-C"""
    do_copy()


@bindings.add("c-v")
def paste_text(event: KeyPressEvent) -> None:
    """Paste with Ctrl-V"""
    do_paste()


@bindings.add("c-z")
def undo_changes(event: KeyPressEvent) -> None:
    """Undo with Ctrl-Z"""
    do_undo()


#
# Handlers for menu items.
#


def do_open_file() -> None:
    """Open file from menu select"""

    async def coroutine() -> None:
        open_dialog = TextInputDialog(
            title="Open file",
            label_text="Enter the path of a file:",
            completer=PathCompleter(),
        )

        path = await show_dialog_as_float(open_dialog)
        ApplicationState.current_path = path

        if path is not None:
            try:
                with open(path, "r", encoding="utf8") as f:
                    text_field.text = f.read()
            except IOError as e:
                show_message("Error", "{}".format(e))
            else:
                set_title(f"Editor - {path}")

    ensure_future(coroutine())


def save_file_at_path(path: str, text: str) -> None:
    """Saves text (changes) to a file path"""
    try:
        with open(path, "w", encoding="utf8") as f:
            f.write(text)
    except IOError as e:
        show_message("Error", "{}".format(e))
    else:
        set_title(f"Editor - {path}")


def do_save_file() -> None:
    """Try to save. If no file is being edited, save as instead to create a new one."""
    if ApplicationState.current_path is not None:
        save_file_at_path(ApplicationState.current_path, text_field.text)
    else:
        do_save_as_file()


def do_save_as_file() -> None:
    """Try to Save As a file under a new name/path."""

    async def coroutine() -> None:
        open_dialog = TextInputDialog(
            title="Save As", label_text="Enter the path of the file:"
        )

        path = await show_dialog_as_float(open_dialog)
        ApplicationState.current_path = path
        if ApplicationState.current_path is not None:
            save_file_at_path(ApplicationState.current_path, text_field.text)

    ensure_future(coroutine())


def do_scroll_menu() -> None:
    """Open Scroll Menu"""
    show_scroll("Scroll", "buf")


def show_scroll(title: str, text: str) -> None:
    """Shows about message"""

    async def coroutine() -> None:
        dialog = ScrollMenuDialog(title, text)
        await show_dialog_as_float(dialog)

    ensure_future(coroutine())


def do_about() -> None:
    """About from menu select"""
    show_message("About", "Text editor.\nCreated by Adaptable Antelopes.")


def show_message(title: str, text: str) -> None:
    """Shows a MessageDialog with a certain title and text"""

    async def coroutine() -> None:
        dialog = MessageDialog(title, text)
        await show_dialog_as_float(dialog)

    ensure_future(coroutine())


async def show_dialog_as_float(dialog: PopUpDialog) -> None:
    """Coroutine what does it return idk? the messageDialogs future result which is None?"""
    float_ = Float(content=dialog)
    root_container.floats.insert(0, float_)

    app = get_app()

    focused_before = app.layout.current_window
    app.layout.focus(dialog)
    result = await dialog.future
    app.layout.focus(focused_before)

    if float_ in root_container.floats:
        root_container.floats.remove(float_)

    return result


# All the do_ is a menu item


def do_new_file() -> None:
    """Makes a new file"""
    text_field.text = ""
    ApplicationState.current_path = None
    set_title("Editor - Untitled")


def do_exit() -> None:
    """Exit"""
    get_app().exit()


def do_time_date() -> None:
    """Inserts current datetime into text_field from menu"""
    text = datetime.datetime.now().isoformat()
    text_field.buffer.insert_text(text)


def do_go_to() -> None:
    """Go to line"""

    async def coroutine() -> None:
        dialog = TextInputDialog(title="Go to line", label_text="Line number:")

        line_number = await show_dialog_as_float(dialog)

        try:
            line_number = int(line_number)
        except ValueError:
            show_message("Invalid line number")
        else:
            text_field.buffer.cursor_position = (
                text_field.buffer.document.translate_row_col_to_index(
                    line_number - 1, 0
                )
            )

    ensure_future(coroutine())


def do_undo() -> None:
    """Undo"""
    text_field.buffer.undo()


def do_cut() -> None:
    """Cut"""
    data = text_field.buffer.cut_selection()
    get_app().clipboard.set_data(data)


def do_copy() -> None:
    """Copy"""
    data = text_field.buffer.copy_selection()
    get_app().clipboard.set_data(data)


def do_delete() -> None:
    """Delete"""
    text_field.buffer.cut_selection()


def do_find() -> None:
    """Find"""
    start_search(text_field.control)


def do_find_next() -> None:
    """Fine next"""
    search_state = get_app().current_search_state

    cursor_position = text_field.buffer.get_search_position(
        search_state, include_current_position=False
    )
    text_field.buffer.cursor_position = cursor_position


def do_paste() -> None:
    """Paste"""
    text_field.buffer.paste_clipboard_data(get_app().clipboard.get_data())


def do_select_all() -> None:
    """Select all"""
    text_field.buffer.cursor_position = 0
    text_field.buffer.start_selection()
    text_field.buffer.cursor_position = len(text_field.buffer.text)


def do_status_bar() -> None:
    """Opens ar closes status bar"""
    ApplicationState.show_status_bar = not ApplicationState.show_status_bar


#
# The menu container.
#


root_container = MenuContainer(
    body=body,
    menu_items=[
        MenuItem(
            "File",
            children=[
                MenuItem("New...", handler=do_new_file),
                MenuItem("Open...", handler=do_open_file),
                MenuItem("Save", handler=do_save_file),
                MenuItem("Save as...", handler=do_save_as_file),
                MenuItem("-", disabled=True),
                MenuItem("Exit", handler=do_exit),
            ],
        ),
        MenuItem(
            "Edit",
            children=[
                MenuItem("Undo", handler=do_undo),
                MenuItem("Cut", handler=do_cut),
                MenuItem("Copy", handler=do_copy),
                MenuItem("Paste", handler=do_paste),
                MenuItem("Delete", handler=do_delete),
                MenuItem("-", disabled=True),
                MenuItem("Find", handler=do_find),
                MenuItem("Find next", handler=do_find_next),
                # TODO no replace function we can just delete it or try to implement do_replace
                MenuItem("Replace"),
                MenuItem("Go To", handler=do_go_to),
                MenuItem("Select All", handler=do_select_all),
                MenuItem("Time/Date", handler=do_time_date),
            ],
        ),
        MenuItem(
            "View",
            children=[MenuItem("Status Bar", handler=do_status_bar)],
        ),
        MenuItem(
            "Info",
            children=[
                MenuItem("About", handler=do_about),
                MenuItem("Scroll", handler=do_scroll_menu),
            ],
        ),
    ],
    floats=[
        Float(
            xcursor=True,
            ycursor=True,
            content=CompletionsMenu(max_height=16, scroll_offset=1),
        ),
    ],
    key_bindings=bindings,
)

# style of menu can def play around here
style = Style.from_dict(
    {
        "status": "reverse",
        "shadow": "bg:#440044",
    }
)

layout = Layout(root_container, focused_element=text_field)

application = Application(
    layout=layout,
    enable_page_navigation_bindings=True,
    style=style,
    mouse_support=True,
    full_screen=True,
)


def run() -> None:
    """Run the application"""
    application.run()


if __name__ == "__main__":
    run()