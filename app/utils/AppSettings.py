import os
import tomllib

from dotenv import find_dotenv, load_dotenv, set_key


def get_poetry_data():
    try:
        with open("pyproject.toml", "rb") as f:
            data = tomllib.load(f)
        return data["tool"]["poetry"]
    except FileNotFoundError:
        return []


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
        if not find_dotenv():
            dotenv_path = os.path.join(
                os.path.dirname(os.path.realpath(__file__)), ".env"
            )
            with open(dotenv_path, "w") as f:
                f.write("")
        load_dotenv(find_dotenv())  # load enviroment variables once

        self.API_USER = os.getenv("API_USER")
        self.API_PWD = os.getenv("API_PWD")

        self.URL_TATTLE_SERVER = os.getenv("URL_TATTLE_SERVER", "http://127.0.0.1:8080")
        self.WATCH_PATH = os.getenv("WATCH_PATH", "")
        self.WATCH_PATH_SERVER = os.getenv("WATCH_PATH_SERVER", "/mnt/watch")

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
        set_key(dotenv_path=find_dotenv(), key_to_set=key, value_to_set=value)
        load_dotenv(find_dotenv())  # reload enviroment variables
