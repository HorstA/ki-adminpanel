import json
import os
import tkinter as tk

import customtkinter as ctk
from loguru import logger
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
            size=(800, 420),
        )

        self.columnconfigure(0, weight=1, uniform="a")
        # self.rowconfigure((0, 1, 2), weight=1, uniform="a")

        self.large_image_label = ctk.CTkLabel(
            self, text="", image=self.large_test_image
        )
        self.large_image_label.grid(
            row=0, column=0, columnspan=2, padx=20, pady=(20, 10)
        )

        # Create a frame for the paths display
        self.paths_frame = ctk.CTkFrame(self)
        self.paths_frame.grid(
            row=1, column=0, columnspan=2, padx=20, pady=(10, 10), sticky="ew"
        )

        # Paths header
        self.paths_header = ctk.CTkLabel(
            self.paths_frame,
            text="Überwachte Verzeichnisse:",
            font=ctk.CTkFont(weight="bold"),
            anchor="w",
        )
        self.paths_header.pack(padx=15, pady=(10, 5), anchor="w")

        # Paths content
        self.paths_content = ctk.CTkFrame(self.paths_frame, fg_color="transparent")
        self.paths_content.pack(fill="x", padx=15, pady=(0, 10))

        # Display paths in separate lines
        if settings.WATCH_PATH:
            for item in settings.WATCH_PATH:
                path_label = ctk.CTkLabel(
                    self.paths_content,
                    text=f"• {item['source']} → {item['target']}",
                    anchor="w",
                )
                path_label.pack(anchor="w", pady=2)
        else:
            path_label = ctk.CTkLabel(
                self.paths_content,
                text="• Keine Verzeichnisse konfiguriert",
                anchor="w",
            )
            path_label.pack(anchor="w", pady=2)

        # Controls frame
        controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        controls_frame.grid(
            row=2, column=0, columnspan=2, padx=20, pady=(10, 20), sticky="ew"
        )

        # Check if all local paths exist
        paths_exist = settings.WATCH_PATH and all(
            os.path.isdir(item["source"]) for item in settings.WATCH_PATH
        )

        self.watch_mode = ctk.BooleanVar(value=False)
        sw = ctk.CTkSwitch(
            controls_frame,
            text="Verzeichnisse überwachen",
            command=self.toggle_tattle,
            variable=self.watch_mode,
            onvalue=True,
            offvalue=False,
            state=(tk.NORMAL if paths_exist else tk.DISABLED),
        )

        sw.pack(side="left", padx=(0, 20))
        self.watch_switch = sw

        self.change_watchpath_button = ctk.CTkButton(
            controls_frame,
            text="Verzeichnisse ändern",
            command=self.set_watchpath,
        )
        self.change_watchpath_button.pack(side="right")

        self.watchtattle = WatchTattle([item["source"] for item in settings.WATCH_PATH])

        # Startfunktion aufrufen
        if paths_exist and settings.WATCH_ON_START:
            self.after(100, self.watch_switch.toggle())
        else:
            logger.warning(
                "Nicht alle Watch-Verzeichnisse existieren, Watch bleibt deaktiviert."
            )

    def set_watchpath(self):
        paths = []
        i = 0
        while True:

            # Get initial directory for dialog
            initial_dir = None
            if settings.WATCH_PATH and len(settings.WATCH_PATH) > i:
                initial_dir = settings.WATCH_PATH[i]["source"]

            local_path = ctk.filedialog.askdirectory(
                initialdir=initial_dir,
                mustexist=False,
                title=f"Lokales Verzeichnis für /mnt/watch{i + 1 if i > 0 else ''} (Abbrechen zum Beenden)",
            )
            if not local_path or not os.path.isdir(local_path):
                break

            server_path = f"/mnt/watch" if i == 0 else f"/mnt/watch{i + 1}"
            paths.append({"source": local_path, "target": server_path})
            i += 1

        if paths:
            # Convert to JSON string for .env
            paths_json = json.dumps(paths)
            settings.setenv("WATCH_PATH", paths_json)

            # Update display with paths
            # Clear existing path labels
            for widget in self.paths_content.winfo_children():
                widget.destroy()

            # Add new path labels
            for item in paths:
                path_label = ctk.CTkLabel(
                    self.paths_content,
                    text=f"• {item['source']} → {item['target']}",
                    anchor="w",
                )
                path_label.pack(anchor="w", pady=2)

            # Always stop the current WatchTattle instance first
            if self.watchtattle:
                self.watchtattle.stop()

            # Create a new WatchTattle instance with the updated paths
            self.watchtattle = WatchTattle([item["source"] for item in paths])
            self.watch_switch.configure(state=tk.NORMAL)

            # Restart the watcher if it was active
            if self.watch_mode.get():
                self.watchtattle.start()

    def toggle_tattle(self):
        if self.watch_mode.get():
            self.watchtattle.start()
        else:
            self.watchtattle.stop()
