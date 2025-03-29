import os
import re
import time
from dataclasses import asdict
from datetime import datetime, timedelta

import requests
import threading
from loguru import logger
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer
from utils.AppSettings import AppSettings

settings = AppSettings()

include_patterns = r".*\.(htm|html|csv|txt|md|odt|eml|doc|docx|pdf|xls|xlsx|ppt|pptx)$"


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

    def _find_matching_server_path(self, local_path: str) -> str:
        """Find the corresponding server path for a given local path"""
        if settings.WATCH_PATH:
            for path_config in settings.WATCH_PATH:
                source = path_config["source"]
                target = path_config["target"]
                if local_path.startswith(source):
                    return local_path.replace(source, target).replace("\\", "/")
        return local_path.replace("\\", "/")  # fallback, just normalize slashes

    def send_tattle(self, event: FileSystemEvent):
        try:
            if event.src_path:
                event.src_path = self._find_matching_server_path(event.src_path)
            if event.dest_path:
                event.dest_path = self._find_matching_server_path(event.dest_path)
            url = f"{settings.URL_TATTLE_SERVER}/file/tattle-event"
            rv = requests.post(url, json=asdict(event), timeout=(3, 10))
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
    def __init__(self, paths):
        self.paths = paths
        self.event_handler = TattleEventHandler()
        self.observers = []

    @logger.catch(reraise=True)
    def start(self):
        for path in self.paths:
            if os.path.isdir(path):
                observer = Observer()
                observer.schedule(self.event_handler, path, recursive=True)
                observer.start()
                self.observers.append(observer)
                logger.info(f"WatchFolder gestartet. Überwache Pfad: {path}")
            else:
                logger.warning(f"Pfad existiert nicht: {path}")

    def stop(self):
        for observer in self.observers:
            observer.stop()
            observer.join()
        self.observers.clear()
        logger.info("WatchFolder stopped gracefully.")
