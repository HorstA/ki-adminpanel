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
            Image.open(os.path.join(image_path, "document_scanner_64dp_w.png")),
            size=(24, 24),
        )

        # Header with icon
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(30, 0))
        
        header_label = ctk.CTkLabel(
            header_frame,
            text=" Verzeichnis-Scan",
            font=ctk.CTkFont(size=20, weight="bold"),
            image=image_icon_image,
            compound="left",
        )
        header_label.pack(anchor="w")
        
        # Description frame with improved styling
        description_frame = ctk.CTkFrame(self)
        description_frame.pack(fill="x", padx=30, pady=(20, 0))
        
        description_text = (
            f"Scant alle Überwachungsverzeichnisse erneut,\n"
            f"fügt neue Dateien hinzu und löscht nicht mehr vorhandene."
        )
        
        description_label = ctk.CTkLabel(
            description_frame,
            text=description_text,
            justify=tk.LEFT,
            wraplength=700,
            anchor="w",
        )
        description_label.pack(padx=20, pady=15, fill="x", anchor="w")

        # Settings frame
        settings_frame = ctk.CTkFrame(self)
        settings_frame.pack(fill="x", padx=30, pady=(20, 0))
        
        settings_label = ctk.CTkLabel(
            settings_frame,
            text="Scan-Einstellungen",
            font=ctk.CTkFont(weight="bold"),
            anchor="w",
        )
        settings_label.pack(padx=20, pady=(15, 10), anchor="w")
        
        # Settings grid
        settings_grid = ctk.CTkFrame(settings_frame, fg_color="transparent")
        settings_grid.pack(fill="x", padx=20, pady=(0, 15))
        
        # Max imports
        max_imports_label = ctk.CTkLabel(
            settings_grid,
            text="Maximale Importe:",
            anchor="w",
        )
        max_imports_label.grid(row=0, column=0, sticky="w", pady=5)
        
        max_imports_value = ctk.CTkLabel(
            settings_grid,
            text=str(settings.MAX_IMPORTS),
            anchor="w",
            font=ctk.CTkFont(weight="bold"),
        )
        max_imports_value.grid(row=0, column=1, sticky="w", padx=(10, 0), pady=5)
        
        # Max deletes
        max_deletes_label = ctk.CTkLabel(
            settings_grid,
            text="Maximale Löschungen:",
            anchor="w",
        )
        max_deletes_label.grid(row=1, column=0, sticky="w", pady=5)
        
        max_deletes_value = ctk.CTkLabel(
            settings_grid,
            text=str(settings.MAX_DELETES),
            anchor="w",
            font=ctk.CTkFont(weight="bold"),
        )
        max_deletes_value.grid(row=1, column=1, sticky="w", padx=(10, 0), pady=5)
        
        # Retry error files
        retry_label = ctk.CTkLabel(
            settings_grid,
            text="Fehlgeschlagene Dateien wiederholen:",
            anchor="w",
        )
        retry_label.grid(row=2, column=0, sticky="w", pady=5)
        
        retry_value = ctk.CTkLabel(
            settings_grid,
            text="Ja" if settings.RETRY_ERROR_FILES else "Nein",
            anchor="w",
            font=ctk.CTkFont(weight="bold"),
        )
        retry_value.grid(row=2, column=1, sticky="w", padx=(10, 0), pady=5)

        # Button container with improved styling
        button_container = ctk.CTkFrame(self, fg_color="transparent")
        button_container.pack(fill="x", padx=30, pady=(20, 0))

        self.scan_button = ctk.CTkButton(
            button_container,
            text="Scan starten",
            image=image_icon_image,
            compound="left",
            command=self.scan_directory,
            height=40,
            font=ctk.CTkFont(weight="bold"),
        )
        self.scan_button.pack(padx=0, pady=0, anchor="w")

        # Result container with improved styling
        result_container = ctk.CTkFrame(self)
        result_container.pack(fill="x", padx=30, pady=(20, 30))
        
        result_header = ctk.CTkLabel(
            result_container,
            text="Scan-Ergebnisse",
            font=ctk.CTkFont(weight="bold"),
            anchor="w",
        )
        result_header.pack(padx=20, pady=(15, 10), anchor="w")
        
        self.result_label = ctk.CTkLabel(
            result_container, 
            text="Noch kein Scan durchgeführt", 
            justify=tk.LEFT, 
            anchor="w"
        )
        self.result_label.pack(padx=20, pady=(0, 15), fill="x", anchor="w")

    def scan_directory(self):
        def task():
            try:
                self.scan_button.configure(state=tk.DISABLED, text="Scanning...")
                self.result_label.configure(text="Scan läuft...")

                params = {
                    "max_deletes": settings.MAX_DELETES,
                    "max_imports": settings.MAX_IMPORTS,
                    "retry_error_files": settings.RETRY_ERROR_FILES,
                    # "paths": settings.WATCH_PATH,  # Send all paths to scan
                }
                url = f"{settings.URL_TATTLE_SERVER}/file/scan-directory"
                rv = requests.post(
                    url, json=params, timeout=(3, settings.MAX_IMPORTS * 30)
                )
                rv.raise_for_status()

                text = f"Gelöschte Dateien: {len(rv.json()['deleted_files'])}\nImportierte Dateien: {len(rv.json()['imported_files'])}\n"
                # TODO: API entsprechend ändern
                # if 'errors' in rv.json():
                #     text += f"\nFehler: {len(rv.json()['errors'])} Dateien"
                self.result_label.configure(text=text)
                print(rv.json())
            except Exception as e:
                logger.error(f"Error in scan_directory: {e}")
                self.result_label.configure(text=f"Fehler: {e}")
            finally:
                self.scan_button.configure(state=tk.NORMAL, text="Scan starten")
                
        threading.Thread(target=task).start()
