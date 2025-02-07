import os
import shutil
import sys
import tomllib

from loguru import logger
from utils.AppSettings import AppSettings


def init_app():
    try:
        # do not use logger until it is initialized
        logger_info = ""
        logger_error = ""
        app_dir = os.path.join(os.path.expanduser("~"), ".tattle")
        if not os.path.exists(app_dir):
            os.makedirs(app_dir)
            logger_info += f"Created directory at {app_dir}. "
            print(logger_info)
        dotenv_path = os.path.join(app_dir, ".env")
        if not os.path.exists(dotenv_path):
            logger_info += f"Creating .env file at {dotenv_path}. "
            print(logger_info)
            try:
                initial_env_path = _get_resource_path(
                    os.path.join("resources", "env.ini")
                )
                shutil.copy(initial_env_path, dotenv_path)
                logger_info += f"Copied initial .env file from {initial_env_path} to {dotenv_path}. "
                print(logger_info)
            except FileNotFoundError:
                logger_error = f"Initial env.ini file not found, creating an empty .env file at {dotenv_path}. "
                print(logger_error)
                with open(dotenv_path, "w") as f:
                    f.write("")

        settings = AppSettings()
        log_path = os.path.join(app_dir, "app.log")
        logger.add(
            log_path,
            colorize=False,
            enqueue=True,
            level=os.getenv("LOGLEVEL", default="DEBUG"),
            rotation="1 MB",
        )
        logger.success(f"Starting app with loglevel: {settings.LOG_LEVEL}")

        if logger_info:
            logger.info(logger_info)
        if logger_error:
            logger.error(logger_error)

        return True
    except Exception as e:
        print(f"Error: {e}")
        # sys.exit(1)


def _get_resource_path(relative_path):
    """Get absolute path to resource here in utils (!), works for dev and for PyInstaller"""
    base_path = getattr(
        sys,
        "_MEIPASS",
        os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."),
    )
    return os.path.join(base_path, relative_path)


def get_poetry_data():
    try:
        with open("pyproject.toml", "rb") as f:
            data = tomllib.load(f)
        return data["tool"]["poetry"]
    except FileNotFoundError:
        return []
