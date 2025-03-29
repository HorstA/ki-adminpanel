import json
import re
import threading
import tkinter as tk
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from tkinter import filedialog, ttk
from typing import Dict, List

import customtkinter as ctk
import matplotlib.pyplot as plt
import requests
from loguru import logger
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

url = "http://127.0.0.1:8080/admin/apilog"


class AdminFrame(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.auto_refresh = False
        self.auto_refresh_job = None
        self.log_lines: List[str] = []
        self.stats_window = None
        self.viz_window = None
        self.viz_notebook = None

        # Main container with padding
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Header
        header_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 15))

        header_label = ctk.CTkLabel(
            header_frame,
            text="Log-Verwaltung",
            font=ctk.CTkFont(size=20, weight="bold"),
            anchor="w",
        )
        header_label.pack(side="left")

        # Top control panel with better styling
        control_panel = ctk.CTkFrame(main_container)
        control_panel.pack(fill="x", pady=(0, 15))

        # Time filter frame
        time_filter_frame = ctk.CTkFrame(control_panel, fg_color="transparent")
        time_filter_frame.pack(side="top", fill="x", padx=15, pady=15)

        time_label = ctk.CTkLabel(
            time_filter_frame,
            text="Zeitfilter:",
            font=ctk.CTkFont(weight="bold"),
        )
        time_label.pack(side="left")

        self.time_filter = ctk.CTkOptionMenu(
            time_filter_frame,
            values=["Gesamt", "Letzte Stunde", "Heute", "Letzten 24h", "Diese Woche"],
            command=self.apply_filters,
            width=150,
        )
        self.time_filter.pack(side="left", padx=(10, 0))

        # Stats and Viz buttons
        buttons_frame = ctk.CTkFrame(time_filter_frame, fg_color="transparent")
        buttons_frame.pack(side="right")

        self.viz_button = ctk.CTkButton(
            buttons_frame,
            text="Visualisierung",
            command=self.show_visualization,
            width=150,
            height=32,
        )
        self.viz_button.pack(side="right", padx=(10, 0))

        self.stats_button = ctk.CTkButton(
            buttons_frame,
            text="Statistiken",
            command=self.show_statistics,
            width=150,
            height=32,
        )
        self.stats_button.pack(side="right")

        # Search and filter frame
        search_frame = ctk.CTkFrame(control_panel, fg_color="transparent")
        search_frame.pack(side="top", fill="x", padx=15, pady=(0, 15))

        search_label = ctk.CTkLabel(
            search_frame,
            text="Suche:",
            font=ctk.CTkFont(weight="bold"),
        )
        search_label.pack(side="left")

        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Suchbegriff eingeben...",
            width=250,
            height=32,
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(10, 10))
        self.search_entry.bind("<Return>", lambda e: self.apply_filters())

        search_button = ctk.CTkButton(
            search_frame,
            text="Suchen",
            command=self.apply_filters,
            width=100,
            height=32,
        )
        search_button.pack(side="left", padx=(0, 10))

        filter_label = ctk.CTkLabel(
            search_frame,
            text="Log-Level:",
            font=ctk.CTkFont(weight="bold"),
        )
        filter_label.pack(side="left")

        self.filter_menu = ctk.CTkOptionMenu(
            search_frame,
            values=["Alle", "INFO", "ERROR", "SUCCESS", "WARNING", "DEBUG"],
            command=self.apply_filters,
            width=150,
            height=32,
        )
        self.filter_menu.pack(side="left", padx=(10, 0))

        # Button container with better organization
        button_container = ctk.CTkFrame(main_container)
        button_container.pack(fill="x", pady=(0, 15))

        # Left side controls
        left_controls = ctk.CTkFrame(button_container, fg_color="transparent")
        left_controls.pack(side="left", padx=15, pady=15)

        self.auto_refresh_switch = ctk.CTkSwitch(
            left_controls,
            text="Auto-Refresh (5s)",
            command=self.toggle_auto_refresh,
            font=ctk.CTkFont(weight="bold"),
        )
        self.auto_refresh_switch.pack(side="left", padx=(0, 20))

        self.clear_button = ctk.CTkButton(
            left_controls,
            text="Log leeren",
            command=self.clear_log,
            width=130,
            height=32,
        )
        self.clear_button.pack(side="left", padx=(0, 10))

        self.export_button = ctk.CTkButton(
            left_controls,
            text="Exportieren",
            command=self.export_log,
            width=130,
            height=32,
        )
        self.export_button.pack(side="left")

        # Right side controls
        right_controls = ctk.CTkFrame(button_container, fg_color="transparent")
        right_controls.pack(side="right", padx=15, pady=15)

        self.scan_button = ctk.CTkButton(
            right_controls,
            text="Aktualisieren",
            command=self.refresh,
            width=130,
            height=32,
        )
        self.scan_button.pack(side="right")

        # Status label with statistics
        self.status_label = ctk.CTkLabel(
            main_container,
            text="",
            text_color="gray70",
            height=25,
            anchor="w",
            justify="left",
        )
        self.status_label.pack(fill="x", pady=(0, 10))

        # Text container with better styling
        text_container = ctk.CTkFrame(main_container)
        text_container.pack(fill="both", expand=True)

        # Add a label for the log content
        log_header = ctk.CTkLabel(
            text_container,
            text="Log-Einträge",
            font=ctk.CTkFont(weight="bold"),
            anchor="w",
        )
        log_header.pack(anchor="w", padx=15, pady=(15, 0))

        self.textbox = ctk.CTkTextbox(
            text_container,
            font=("Courier", 12),
        )
        self.textbox.pack(padx=15, pady=(5, 15), fill="both", expand=True)
        self.after(100, self.refresh)

    def parse_log_time(self, line: str) -> datetime:
        try:
            time_str = re.search(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", line)
            if time_str:
                return datetime.strptime(time_str.group(), "%Y-%m-%d %H:%M:%S")
        except Exception:
            pass
        return datetime.now()

    def apply_time_filter(self, lines: List[str]) -> List[str]:
        time_filter = self.time_filter.get()
        now = datetime.now()

        if time_filter == "Gesamt":
            return lines

        time_filters = {
            "Letzte Stunde": lambda dt: now - dt <= timedelta(hours=1),
            "Heute": lambda dt: dt.date() == now.date(),
            "Letzten 24h": lambda dt: now - dt <= timedelta(days=1),
            "Diese Woche": lambda dt: now - dt <= timedelta(weeks=1),
        }

        filter_func = time_filters.get(time_filter)
        if filter_func:
            return [line for line in lines if filter_func(self.parse_log_time(line))]
        return lines

    def show_statistics(self):
        if self.stats_window is None or not tk.Toplevel.winfo_exists(self.stats_window):
            self.stats_window = tk.Toplevel(self)
            self.stats_window.title("Log Statistiken")
            self.stats_window.geometry("400x500")

            # Calculate statistics with improved log level counting
            log_levels = defaultdict(int)
            level_patterns = {
                "INFO": r"\| INFO\s+\|",
                "ERROR": r"\| ERROR\s+\|",
                "SUCCESS": r"\| SUCCESS\s+\|",
                "WARNING": r"\| WARNING\s+\|",
                "DEBUG": r"\| DEBUG\s+\|",
            }

            for line in self.log_lines:
                for level, pattern in level_patterns.items():
                    if re.search(pattern, line):
                        log_levels[level] += 1
                        break  # Each line should only match one level

            # Time-based statistics
            now = datetime.now()
            last_hour = len(
                [
                    line
                    for line in self.log_lines
                    if now - self.parse_log_time(line) <= timedelta(hours=1)
                ]
            )
            last_day = len(
                [
                    line
                    for line in self.log_lines
                    if now - self.parse_log_time(line) <= timedelta(days=1)
                ]
            )

            # Create statistics display
            stats_frame = ctk.CTkFrame(self.stats_window)
            stats_frame.pack(fill="both", expand=True, padx=20, pady=20)

            # Log level distribution
            ctk.CTkLabel(
                stats_frame, text="Log Level Verteilung", font=("", 16, "bold")
            ).pack(pady=(0, 10))

            # Keep consistent order and only show levels that exist
            ordered_levels = ["INFO", "ERROR", "SUCCESS", "WARNING", "DEBUG"]
            max_count = max(log_levels.values()) if log_levels else 1

            for level in ordered_levels:
                count = log_levels[level]
                if count > 0:  # Only show levels that have entries
                    frame = ctk.CTkFrame(stats_frame, fg_color="transparent")
                    frame.pack(fill="x", pady=2)

                    # Level label
                    ctk.CTkLabel(frame, text=f"{level}:", width=80).pack(side="left")

                    # Progress bar
                    progress = ctk.CTkProgressBar(frame, width=200)
                    progress.pack(side="left", padx=10)
                    progress.set(count / max_count)

                    # Count label with appropriate color
                    color = {
                        "SUCCESS": "green",
                        "ERROR": "red",
                        "INFO": "gray70",
                        "WARNING": "orange",
                        "DEBUG": "blue",
                    }[level]
                    ctk.CTkLabel(frame, text=str(count), text_color=color).pack(
                        side="left"
                    )

            # Time-based statistics
            ctk.CTkLabel(
                stats_frame, text="\nZeitbasierte Statistiken", font=("", 16, "bold")
            ).pack(pady=(20, 10))
            ctk.CTkLabel(
                stats_frame, text=f"Logs in der letzten Stunde: {last_hour}"
            ).pack()
            ctk.CTkLabel(
                stats_frame, text=f"Logs in den letzten 24 Stunden: {last_day}"
            ).pack()
            ctk.CTkLabel(
                stats_frame, text=f"Gesamtzahl der Logs: {len(self.log_lines)}"
            ).pack()

    def show_visualization(self):
        if self.viz_window is None or not tk.Toplevel.winfo_exists(self.viz_window):
            self.viz_window = tk.Toplevel(self)
            self.viz_window.title("Log Visualisierung")
            self.viz_window.geometry("800x600")

            # Create notebook for multiple charts
            self.viz_notebook = ttk.Notebook(self.viz_window)
            self.viz_notebook.pack(fill="both", expand=True, padx=10, pady=10)

            # Log Level Distribution Tab
            level_tab = ttk.Frame(self.viz_notebook)
            self.viz_notebook.add(level_tab, text="Log Level Verteilung")
            self.create_level_distribution_chart(level_tab)

            # Time Distribution Tab
            time_tab = ttk.Frame(self.viz_notebook)
            self.viz_notebook.add(time_tab, text="Zeitliche Verteilung")
            self.create_time_distribution_chart(time_tab)

            # Error Trend Tab
            error_tab = ttk.Frame(self.viz_notebook)
            self.viz_notebook.add(error_tab, text="Fehler Trend")
            self.create_error_trend_chart(error_tab)

            # Configure window close behavior
            self.viz_window.protocol("WM_DELETE_WINDOW", self.on_viz_window_close)

    def on_viz_window_close(self):
        """Handle visualization window closing."""
        self.viz_window.destroy()
        self.viz_window = None
        self.viz_notebook = None

    def create_level_distribution_chart(self, parent):
        fig = Figure(figsize=(8, 4))
        ax = fig.add_subplot(111)

        # Improved log level counting
        log_levels = defaultdict(int)
        level_patterns = {
            "INFO": r"\| INFO\s+\|",
            "ERROR": r"\| ERROR\s+\|",
            "SUCCESS": r"\| SUCCESS\s+\|",
            "WARNING": r"\| WARNING\s+\|",
            "DEBUG": r"\| DEBUG\s+\|",
        }

        for line in self.log_lines:
            for level, pattern in level_patterns.items():
                if re.search(pattern, line):
                    log_levels[level] += 1
                    break  # Each line should only match one level

        # Keep consistent order
        ordered_levels = ["INFO", "ERROR", "SUCCESS", "WARNING", "DEBUG"]
        levels = [level for level in ordered_levels if level in log_levels]
        values = [log_levels[level] for level in levels]
        colors = {
            "INFO": "gray",
            "ERROR": "red",
            "SUCCESS": "green",
            "WARNING": "orange",
            "DEBUG": "blue",
        }
        bar_colors = [colors[level] for level in levels]

        bars = ax.bar(levels, values, color=bar_colors)
        ax.set_title("Log Level Verteilung")
        ax.set_ylabel("Anzahl")

        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                f"{int(height)}",
                ha="center",
                va="bottom",
            )

        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def create_time_distribution_chart(self, parent):
        fig = Figure(figsize=(8, 4))
        ax = fig.add_subplot(111)

        # Group logs by hour
        hour_distribution = defaultdict(int)
        now = datetime.now()
        for line in self.log_lines:
            log_time = self.parse_log_time(line)
            if now - log_time <= timedelta(days=1):
                hour = log_time.strftime("%H:00")
                hour_distribution[hour] += 1

        hours = sorted(hour_distribution.keys())
        counts = [hour_distribution[hour] for hour in hours]

        ax.plot(hours, counts, marker="o")
        ax.set_title("Log Verteilung (24 Stunden)")
        ax.set_xlabel("Stunde")
        ax.set_ylabel("Anzahl Logs")
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def create_error_trend_chart(self, parent):
        fig = Figure(figsize=(8, 4))
        ax = fig.add_subplot(111)

        # Group errors by hour
        error_trend = defaultdict(int)
        now = datetime.now()
        for line in self.log_lines:
            if "ERROR" in line:
                log_time = self.parse_log_time(line)
                if now - log_time <= timedelta(days=1):
                    hour = log_time.strftime("%H:00")
                    error_trend[hour] += 1

        hours = sorted(error_trend.keys())
        counts = [error_trend[hour] for hour in hours]

        ax.plot(hours, counts, marker="o", color="red")
        ax.fill_between(hours, counts, alpha=0.2, color="red")
        ax.set_title("Fehler Trend (24 Stunden)")
        ax.set_xlabel("Stunde")
        ax.set_ylabel("Anzahl Fehler")
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

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
        self.textbox.see("end")  # Auto-scroll to end
        self.log_lines = []
        self.update_status("Log cleared", "gray70")

    def apply_filters(self, *args):
        search_text = self.search_entry.get().lower()
        log_level = self.filter_menu.get()

        # Apply time filter first
        filtered_lines = self.apply_time_filter(self.log_lines)

        # Then apply search and log level filters
        if search_text:
            filtered_lines = [
                line for line in filtered_lines if search_text in line.lower()
            ]
        if log_level != "Alle":
            filtered_lines = [line for line in filtered_lines if log_level in line]

        self.textbox.delete("1.0", tk.END)
        for line in filtered_lines:
            self.textbox.insert(tk.END, line + "\n")
        self.textbox.see("end")  # Auto-scroll to the end
        # Color coding for different log levels
        self.highlight_log_levels()

        # Update status with filter statistics
        total = len(filtered_lines)
        original = len(self.log_lines)
        self.update_status(f"Angezeigt: {total} von {original} Logs", "gray70")

    def highlight_log_levels(self):
        def apply_tag(text, tag_name, color):
            start = "1.0"
            while True:
                start = self.textbox.search(text, start, tk.END)
                if not start:
                    break
                end = f"{start}+{len(text)}c"
                self.textbox.tag_add(tag_name, start, end)
                self.textbox.tag_config(tag_name, foreground=color)
                start = end

        self.textbox.tag_delete("success", "error", "info", "warning", "debug")
        apply_tag("SUCCESS", "success", "green")
        apply_tag("ERROR", "error", "red")
        apply_tag("INFO", "info", "gray70")
        apply_tag("WARNING", "warning", "orange")
        apply_tag("DEBUG", "debug", "blue")

    def export_log(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[
                ("Text files", "*.txt"),
                ("Log files", "*.log"),
                ("All files", "*.*"),
            ],
        )
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(self.log_lines))
                self.update_status(f"Log exported to {file_path}", "green")
            except Exception as e:
                self.update_status(f"Export failed: {str(e)}", "red")

    def refresh(self):
        self.scan_button.configure(state="disabled")
        self.update_status("Refreshing...", "gray70")

        def task():
            try:
                rv = requests.get(url, params={"lastnlines": 200})
                rv.raise_for_status()
                self.log_lines = rv.json().get("lines", [])
                self.after(0, lambda: self.update_textbox(self.log_lines))
                self.after(
                    0,
                    lambda: self.update_status(
                        f"Last updated: {datetime.now().strftime('%H:%M:%S')}", "green"
                    ),
                )
                # Update visualization if window is open
                if self.viz_window and tk.Toplevel.winfo_exists(self.viz_window):
                    self.after(0, self.update_visualization)
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
        self.textbox.see("end")  # Auto-scroll to the end
        self.highlight_log_levels()

    def update_visualization(self):
        """Update all visualization charts with current data."""
        if not hasattr(self, "viz_notebook"):
            return

        # Get the current tab
        current_tab = self.viz_notebook.select()
        if not current_tab:
            return

        # Clear the current tab and recreate its chart
        current_frame = self.viz_notebook.nametowidget(current_tab)
        for widget in current_frame.winfo_children():
            widget.destroy()

        # Recreate the appropriate chart based on the tab name
        tab_text = self.viz_notebook.tab(current_tab, "text")
        if tab_text == "Log Level Verteilung":
            self.create_level_distribution_chart(current_frame)
        elif tab_text == "Zeitliche Verteilung":
            self.create_time_distribution_chart(current_frame)
        elif tab_text == "Fehler Trend":
            self.create_error_trend_chart(current_frame)
