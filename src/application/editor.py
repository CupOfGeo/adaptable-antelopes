import os

from prompt_toolkit.application import Application
from prompt_toolkit.filters import Condition
from prompt_toolkit.layout.containers import (
    ConditionalContainer,
    HSplit,
    VSplit,
    Window,
    WindowAlign,
)
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import SearchToolbar, TextArea
from pygments.lexers.markup import MarkdownLexer

from application.state import ApplicationState
from constants import NOTES_DIR
from navigation.menu_bar import MenuNav


class ThoughtBox(MenuNav):
    """Thought Box - The minimalist note-taking app"""

    def __init__(self):
        self.application_state = ApplicationState()
        self.search_toolbar = SearchToolbar()
        self.text_field = TextArea(
            lexer=PygmentsLexer(MarkdownLexer),
            scrollbar=True,
            search_field=self.search_toolbar,
        )
        # style of menu can def play around here
        self.style = Style.from_dict(
            {
                "status": "reverse",
                "shadow": "bg:#440044",
            }
        )
        self.body = HSplit(
            [
                self.text_field,
                self.search_toolbar,
                ConditionalContainer(
                    content=VSplit(
                        [
                            # No longer need the bottom title bar
                            # Window(
                            #     FormattedTextControl(get_status_bar_left_text),
                            #     style="class:status",
                            #     align=WindowAlign.LEFT,
                            # ),
                            Window(
                                FormattedTextControl(self.get_statusbar_middle_text),
                                style="class:status",
                            ),
                            Window(
                                FormattedTextControl(self.get_statusbar_right_text),
                                style="class:status.right",
                                width=9,
                                align=WindowAlign.RIGHT,
                            ),
                        ],
                        height=1,
                    ),
                    filter=Condition(lambda: self.application_state.show_status_bar),
                ),
            ]
        )
        # Initialize super class to get self.root_container
        super().__init__()

        self.layout = Layout(self.root_container, focused_element=self.text_field)

        self.application = Application(
            layout=self.layout,
            enable_page_navigation_bindings=True,
            style=self.style,
            mouse_support=True,
            full_screen=True,
        )

    def get_statusbar_middle_text(self) -> None:
        """Gets status bar opens menu"""
        return " Press Ctrl-K to open menu. "

    def get_statusbar_right_text(self) -> None:
        """Get status bar for the right text?"""
        return " {}:{}  ".format(
            self.text_field.document.cursor_position_row + 1,
            self.text_field.document.cursor_position_col + 1,
        )

    def run(self) -> None:
        """Run the application"""
        # Create notes directory
        os.makedirs(NOTES_DIR, exist_ok=True)
        self.application.run()