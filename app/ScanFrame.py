import os
import threading
import tkinter as tk

import customtkinter as ctk
import requests
from loguru import logger
from PIL import Image
from utils.AppSettings import AppSettings

settings = AppSettings()


class ScanFrame(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        image_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "resources"
        )
        image_icon_image = ctk.CTkImage(
            Image.open(os.path.join(image_path, "image_icon_light.png")), size=(20, 20)
        )

        label = ctk.CTkLabel(
            self,
            text=(
                f"Scant das Überwachungsverzeichnis erneut,\n"
                f"fügt neue Dateien hinzu und löscht nicht mehr vorhandene.\n\n"
                f"Maximale Importe: {settings.MAX_IMPORTS}\n"
                f"Maximale Löschungen: {settings.MAX_DELETES}\n"
                f"Fehlgeschlagene Dateien wiederholen: {settings.RETRY_ERROR_FILES}"
            ),
            justify=tk.LEFT,
            wraplength=485,
            anchor="w",
        )
        label.pack(padx=20, pady=(20, 0), fill="x", anchor="w")

        button_container = ctk.CTkFrame(self, fg_color="transparent")
        button_container.pack(fill="x")

        self.scan_button = ctk.CTkButton(
            button_container,
            text="Scan",
            image=image_icon_image,
            compound="left",
            command=self.scan_directory,
        )
        self.scan_button.pack(padx=20, pady=20, anchor="w")

        result_container = ctk.CTkFrame(self, fg_color="transparent")
        result_container.pack(fill="x")
        self.result_label = ctk.CTkLabel(
            result_container, text="", justify=tk.LEFT, anchor="w"
        )
        self.result_label.pack(padx=20, pady=(0, 20), fill="x", anchor="w")

    def scan_directory(self):
        def task():
            try:
                self.scan_button.configure(state=tk.DISABLED, text="Scanning...")
                self.result_label.configure(text="")

                params = {
                    "max_deletes": settings.MAX_DELETES,
                    "max_imports": settings.MAX_IMPORTS,
                    "retry_error_files": settings.RETRY_ERROR_FILES,
                }
                url = f"{settings.URL_TATTLE_SERVER}/file/scan-directory"
                rv = requests.post(
                    url, json=params, timeout=(3, settings.MAX_IMPORTS * 30)
                )
                rv.raise_for_status()

                text = f"Gelöschte Dateien: {len(rv.json()['deleted_files'])}\nImportierte Dateien: {len(rv.json()['imported_files'])}\n"
                self.result_label.configure(text=text)
                print(rv.json())
            except Exception as e:
                logger.error(f"Error in scan_directory: {e}")
                self.result_label.configure(text=f"Error: {e}")
            finally:
                self.scan_button.configure(state=tk.NORMAL, text="Scan")

        threading.Thread(target=task).start()
