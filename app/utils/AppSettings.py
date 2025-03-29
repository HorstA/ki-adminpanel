import os
import json
from dotenv import find_dotenv, load_dotenv, set_key


class AppSettings:
    true_values = [
        "true",
        "1",
        "t",
        "y",
        "yes",
        "ja",
        "ok",
    ]

    def __init__(self):
        app_dir = os.path.join(os.path.expanduser("~"), ".tattle")
        self.dotenv_path = os.path.join(app_dir, ".env")
        print(f"Dotenv path: {self.dotenv_path}")
        try:
            load_dotenv(self.dotenv_path)  # load enviroment variables once
        except Exception as e:
            print(f"Error: {e}")

        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")

        self.API_USER = os.getenv("API_USER")
        self.API_PWD = os.getenv("API_PWD")

        self.URL_TATTLE_SERVER = os.getenv("URL_TATTLE_SERVER", "http://127.0.0.1:8080")

        watch_path_env = os.getenv("WATCH_PATH")
        self.WATCH_PATH = json.loads(watch_path_env) if watch_path_env else None

        self.MAX_IMPORTS = int(os.getenv("MAX_IMPORTS", 10))
        self.MAX_DELETES = int(os.getenv("MAX_DELETES", -1))
        self.RETRY_ERROR_FILES = (
            os.getenv("RETRY_ERROR_FILES", "False").lower() in self.true_values
        )

        self.WATCH_ON_START = (
            os.getenv("WATCH_ON_START", "False").lower() in self.true_values
        )

    def getenv(self, key: str, default=None):
        return os.getenv(key, default)

    def setenv(self, key: str, value=None):
        set_key(dotenv_path=self.dotenv_path, key_to_set=key, value_to_set=value)
        load_dotenv(find_dotenv())  # reload enviroment variables
