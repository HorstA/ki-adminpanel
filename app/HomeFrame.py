import os
import time
import tkinter as tk

import customtkinter as ctk
from PIL import Image

from utils.AppSettings import AppSettings
from utils.WatchTattle import WatchTattle

settings = AppSettings()


class HomeFrame(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        image_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "resources"
        )
        self.large_test_image = ctk.CTkImage(
            Image.open(os.path.join(image_path, "office.png")),
            size=(582, 326),
        )

        self.columnconfigure(0, weight=1, uniform="a")
        # self.rowconfigure((0, 1, 2), weight=1, uniform="a")

        self.large_image_label = ctk.CTkLabel(
            self, text="", image=self.large_test_image
        )
        self.large_image_label.grid(row=0, column=0, columnspan=2)

        self.label_value = tk.StringVar(value=f"Verzeichnis: {settings.WATCH_PATH}")
        self.label = ctk.CTkLabel(
            self,
            textvariable=self.label_value,
        )
        self.label.grid(row=1, column=0, columnspan=2, padx=20, pady=10)

        self.watch_mode = ctk.BooleanVar(value=False)
        sw = ctk.CTkSwitch(
            self,
            text="Verzeichnis überwachen",
            command=self.toggle_tattle,
            variable=self.watch_mode,
            onvalue=True,
            offvalue=False,
            state=(tk.NORMAL if os.path.isdir(settings.WATCH_PATH) else tk.DISABLED),
        )

        sw.grid(row=2, column=0, padx=20, pady=10, sticky="w")
        self.watch_switch = sw

        self.change_watchpath_button = ctk.CTkButton(
            self,
            text="Verzeichnis ändern",
            command=self.set_watchpath,
        )
        self.change_watchpath_button.grid(row=2, column=1, padx=20, pady=10, sticky="e")

        self.watchtattle = WatchTattle(settings.WATCH_PATH)

        # Startfunktion aufrufen

        if os.path.isdir(settings.WATCH_PATH) and settings.WATCH_ON_START:
            self.after(100, self.watch_switch.toggle())

    def set_watchpath(self):
        value = ctk.filedialog.askdirectory(
            initialdir=settings.WATCH_PATH,
            mustexist=False,
            title="Überwachungsverzeichnis",
        )
        if value and os.path.isdir(value):
            settings.setenv("WATCH_PATH", value)
            self.label_value.set(f"Verzeichnis: {value}")

            self.watchtattle.path = value
            self.watch_switch.configure(state=tk.NORMAL)
            if self.watch_mode.get():
                self.watchtattle.stop()
                time.sleep(1)
                self.watchtattle.start()

    def toggle_tattle(self):
        if self.watch_mode.get():
            self.watchtattle.start()
        else:
            self.watchtattle.stop()
