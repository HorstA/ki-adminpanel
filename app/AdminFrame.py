import threading
import tkinter as tk
from datetime import datetime

import customtkinter as ctk
import requests
from loguru import logger

url = "http://127.0.0.1:8080/admin/apilog"


class AdminFrame(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.auto_refresh = False
        self.auto_refresh_job = None

        button_container = ctk.CTkFrame(self, fg_color="transparent")
        button_container.pack(fill="x")

        # Left side controls
        left_controls = ctk.CTkFrame(button_container, fg_color="transparent")
        left_controls.pack(side="left", padx=20, pady=(20, 0))
        
        self.auto_refresh_switch = ctk.CTkSwitch(
            left_controls,
            text="Auto-Refresh",
            command=self.toggle_auto_refresh
        )
        self.auto_refresh_switch.pack(side="left", padx=(0, 10))

        self.clear_button = ctk.CTkButton(
            left_controls,
            text="Clear",
            command=self.clear_log
        )
        self.clear_button.pack(side="left")

        # Right side controls
        self.scan_button = ctk.CTkButton(
            button_container,
            text="Aktualisieren",
            command=self.refresh,
        )
        self.scan_button.pack(side="right", padx=20, pady=(20, 0))

        # Status label
        self.status_label = ctk.CTkLabel(
            self,
            text="",
            text_color="gray70"
        )
        self.status_label.pack(pady=(5, 0))

        text_container = ctk.CTkFrame(self, fg_color="transparent")
        text_container.pack(fill="both", expand=True)

        self.textbox = ctk.CTkTextbox(
            text_container,
            font=("Courier", 12)
        )
        self.textbox.pack(padx=20, pady=20, fill="both", expand=True)
        self.after(100, self.refresh)

    def toggle_auto_refresh(self):
        self.auto_refresh = self.auto_refresh_switch.get()
        if self.auto_refresh:
            self.schedule_refresh()
        elif self.auto_refresh_job:
            self.after_cancel(self.auto_refresh_job)
            self.auto_refresh_job = None

    def schedule_refresh(self):
        if self.auto_refresh:
            self.refresh()
            self.auto_refresh_job = self.after(5000, self.schedule_refresh)

    def clear_log(self):
        self.textbox.delete("1.0", tk.END)
        self.update_status("Log cleared", "gray70")

    def refresh(self):
        self.scan_button.configure(state="disabled")
        self.update_status("Refreshing...", "gray70")

        def task():
            try:
                rv = requests.get(url, params={"lastnlines": 200})
                rv.raise_for_status()
                lines = rv.json().get("lines", [])
                self.after(0, lambda: self.update_textbox(lines))
                self.after(0, lambda: self.update_status(
                    f"Last updated: {datetime.now().strftime('%H:%M:%S')}", 
                    "green"
                ))
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                logger.error(error_msg)
                self.after(0, lambda: self.update_status(error_msg, "red"))
            finally:
                self.after(0, lambda: self.scan_button.configure(state="normal"))

        threading.Thread(target=task).start()

    def update_status(self, message, color):
        self.status_label.configure(text=message, text_color=color)

    def update_textbox(self, lines):
        self.textbox.delete("1.0", tk.END)
        for line in lines:
            self.textbox.insert(tk.END, line + "\n")
