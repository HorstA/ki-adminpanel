import os
import re
import time
from dataclasses import asdict
from datetime import datetime, timedelta

import requests
import threading
from loguru import logger
from watchdog.events import FileSystemEvent
from watchdog.observers import Observer
from utils.AppSettings import AppSettings

settings = AppSettings()

include_patterns = r".*\.(htm|html|csv|txt|md|odt|eml|doc|docx|pdf|xls|xlsx|ppt|pptx)$"


from watchdog.events import (
    FileSystemEvent,
    FileSystemEvent,
    FileSystemEventHandler,
)
from watchdog.observers import Observer


def filter_events(func):
    def wrapper(*args, **kwargs):
        event: FileSystemEvent = args[1]
        if event.is_directory:
            return

        # Apply include_patterns for all relevant events
        if not re.search(include_patterns, event.src_path):
            # For "moved" events, also check the destination path
            if event.event_type == "moved" and not re.search(
                include_patterns, event.dest_path
            ):
                return
            elif event.event_type != "moved":  # For other event types
                return

        time.sleep(1)  # wait so changes can be done
        return func(*args, **kwargs)

    return wrapper


class TattleEventHandler(FileSystemEventHandler):
    def __init__(self):
        self.processed_files = {}
        self.lock = threading.Lock()
        self.delay = timedelta(seconds=1)  # Set the delay time here

    def send_tattle(self, event: FileSystemEvent):
        try:
            dict_representation = asdict(event)
            if dict_representation["src_path"]:
                dict_representation["src_path"] = (
                    dict_representation["src_path"]
                    .replace(settings.WATCH_PATH, settings.WATCH_PATH_SERVER)
                    .replace("\\", "/")
                )
            if dict_representation["dest_path"]:
                dict_representation["dest_path"] = (
                    dict_representation["dest_path"]
                    .replace(settings.WATCH_PATH, settings.WATCH_PATH_SERVER)
                    .replace("\\", "/")
                )
            url = f"{settings.URL_TATTLE_SERVER}/file/tattle-event"
            rv = requests.post(url, json=dict_representation, timeout=(3, 10))
            rv.raise_for_status()
            return rv
        except Exception as e:
            print(f"Error sending tattle: {e}")
            return {}

    ### events

    @logger.catch
    @filter_events
    def on_created(self, event: FileSystemEvent) -> None:
        current_time = datetime.now()
        with self.lock:
            last_processed = self.processed_files.get(event.src_path)
            if not last_processed or current_time - last_processed > self.delay:
                self.processed_files[event.src_path] = current_time

                logger.debug(f"_run_created: {event}")

                self.send_tattle(event)

    @logger.catch
    @filter_events
    def on_modified(self, event: FileSystemEvent) -> None:
        current_time = datetime.now()
        with self.lock:
            last_processed = self.processed_files.get(event.src_path)
            if not last_processed or current_time - last_processed > self.delay:
                self.processed_files[event.src_path] = current_time
                logger.debug(f"_run_modified: {event}")
                self.send_tattle(event)

    @logger.catch
    @filter_events
    def on_deleted(self, event: FileSystemEvent) -> None:
        logger.debug(f"Lösche Datei: {event.src_path}")
        # do not supress a deleted event:
        self.send_tattle(event)

    @logger.catch
    @filter_events
    def on_moved(self, event: FileSystemEvent) -> None:
        current_time = datetime.now()
        with self.lock:
            last_processed = self.processed_files.get(event.dest_path)
            if not last_processed or current_time - last_processed > self.delay:
                self.processed_files[event.dest_path] = current_time
                self.send_tattle(event)


class WatchTattle:
    def __init__(self, path):
        self.path = path
        self.event_handler = TattleEventHandler()
        self.observer = Observer()
        self.observer.schedule(self.event_handler, path, recursive=True)

    @logger.catch(reraise=True)
    def start(self):
        self.observer = Observer()
        self.observer.schedule(self.event_handler, self.path, recursive=True)
        self.observer.start()
        logger.info(f"WatchFolder gestartet. Überwache Pfad: {self.path}")

    def stop(self):
        self.observer.stop()
        self.observer.join()
        logger.info("WatchFolder stopped gracefully.")
