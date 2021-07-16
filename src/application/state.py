import json
import os

from constants import NOTES_DIR, WELCOME_PAGE


class ApplicationState:
    """Holds things like settings and current path in an object"""

    def __init__(self):
        try:
            with open(os.path.join(NOTES_DIR, ".user_setting.json"), "r") as f:
                self.user_settings = json.load(f)
        except FileNotFoundError:
            # Use default settings when the file got accidentally deleted.
            self.user_settings = {"last_path": None, "style": ""}
            with open(os.path.join(NOTES_DIR, ".user_setting.json"), "w") as f:
                json.dump(self.user_settings, f)

        self.show_status_bar = True
        if self.user_settings.get("last_path"):
            self.current_path = self.user_settings["last_path"]
        else:
            # Open the welcome page
            self.current_path = NOTES_DIR + "/" + WELCOME_PAGE

    @property
    def current_dir(self) -> str:
        """
        Returns the directory of the current path.

        If there is no current path, return NOTES_DIR
        """
        if self.current_path:
            return os.path.dirname(self.current_path)
        return NOTES_DIR
