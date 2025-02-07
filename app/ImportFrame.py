import os
import threading
import tkinter as tk

import customtkinter as ctk
import requests
from loguru import logger
from PIL import Image
from utils.AppSettings import AppSettings

settings = AppSettings()


class ImportFrame(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.columnconfigure(0, weight=1, uniform="a")
        self.rowconfigure((0, 1, 2, 3), weight=1, uniform="a")

        image_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "resources"
        )
        self.image_icon_image = ctk.CTkImage(
            Image.open(os.path.join(image_path, "publish_64dp_w.png")), size=(20, 20)
        )

        label = ctk.CTkLabel(
            self,
            text="Importiert die ausgewählte Datei in den Vektor-Store",
            justify=tk.LEFT,
            wraplength=485,
            anchor="w",
        )
        label.pack(padx=20, pady=(20, 0), fill="x", anchor="w")

        button_container = ctk.CTkFrame(self, fg_color="transparent")
        button_container.pack(fill="x")
        self.import_button = ctk.CTkButton(
            button_container,
            text="Datei auswählen",
            image=self.image_icon_image,
            compound="left",
            command=self.import_file,
        )
        self.import_button.pack(padx=20, pady=20, anchor="w")

        result_container = ctk.CTkFrame(self, fg_color="transparent")
        result_container.pack(fill="x")
        self.result_label = ctk.CTkLabel(
            result_container,
            text="",
            justify=tk.LEFT,
            anchor="w",
        )
        self.result_label.pack(padx=20, pady=(0, 20), fill="x", anchor="w")

    def import_file(self):

        file_path = ctk.filedialog.askopenfilename(
            title="Import",
        )
        if file_path:

            def task():
                try:
                    self.import_button.configure(state=tk.DISABLED, text="Import...")
                    self.result_label.configure(text="")

                    headers = {"accept": "application/json"}
                    params = {
                        "splitter_type": "recursive",
                        "collection_name": "rag",
                    }
                    files = {
                        "file_upload": (
                            os.path.basename(file_path),
                            open(file_path, "rb"),
                            "text/plain",
                        ),
                    }
                    url = f"{settings.URL_TATTLE_SERVER}/file/import"
                    rv = requests.post(url, headers=headers, files=files, params=params)
                    rv.raise_for_status()
                    text = (
                        f"Importierte Datei: {file_path}\nId: {rv.json()['import_id']}"
                    )
                    self.result_label.configure(text=text)
                    print(rv.json())
                except Exception as e:
                    logger.error(f"Error in import_file: {e}")
                    self.result_label.configure(text=f"Error: {e}")
                finally:
                    self.import_button.configure(
                        state=tk.NORMAL, text="Datei auswählen"
                    )

            threading.Thread(target=task).start()
