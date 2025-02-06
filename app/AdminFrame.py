import threading
import tkinter as tk

import customtkinter as ctk
import requests

url = "http://127.0.0.1:8080/admin/apilog"


class AdminFrame(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        button_container = ctk.CTkFrame(self, fg_color="transparent")
        button_container.pack(fill="x")

        self.scan_button = ctk.CTkButton(
            button_container,
            text="Aktualisieren",
            command=self.refresh,
        )
        self.scan_button.pack(padx=20, pady=(20, 0), anchor="e")

        text_container = ctk.CTkFrame(self, fg_color="transparent")
        text_container.pack(fill="both", expand=True)

        self.textbox = ctk.CTkTextbox(text_container)
        self.textbox.pack(padx=20, pady=20, fill="both", expand=True)
        self.after(100, self.refresh)

    def refresh(self):
        def task():
            try:
                rv = requests.get(url, params={"lastnlines": 200})
                rv.raise_for_status()
                lines = rv.json().get("lines", [])
                self.update_textbox(lines)
            except Exception as e:
                pass

        threading.Thread(target=task).start()

    def update_textbox(self, lines):
        self.textbox.delete("1.0", tk.END)
        for line in lines:
            self.textbox.insert(tk.END, line + "\n")
