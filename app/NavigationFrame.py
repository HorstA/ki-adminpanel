import os

import customtkinter as ctk
from PIL import Image


class NaviButton(ctk.CTkButton):
    def __init__(self, parent, text, image, navigation_button_event, **kwargs):
        super().__init__(
            parent,
            corner_radius=0,
            height=40,
            border_spacing=10,
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            anchor="w",
            text=text,
            image=image,
            command=navigation_button_event,
            **kwargs
        )


class NavigationFrame(ctk.CTkFrame):
    def __init__(
        self, parent, navigation_button_event, change_appearance_mode_event, **kwargs
    ):
        super().__init__(parent, **kwargs)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(5, weight=1)

        image_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "resources"
        )
        self.logo_image = ctk.CTkImage(
            Image.open(os.path.join(image_path, "robot.png")),
            size=(40, 40),
        )
        self.home_image = ctk.CTkImage(
            light_image=Image.open(os.path.join(image_path, "home_dark.png")),
            dark_image=Image.open(os.path.join(image_path, "home_light.png")),
            size=(20, 20),
        )
        self.chat_image = ctk.CTkImage(
            light_image=Image.open(os.path.join(image_path, "chat_dark.png")),
            dark_image=Image.open(os.path.join(image_path, "chat_light.png")),
            size=(20, 20),
        )
        self.add_user_image = ctk.CTkImage(
            light_image=Image.open(os.path.join(image_path, "add_user_dark.png")),
            dark_image=Image.open(os.path.join(image_path, "add_user_light.png")),
            size=(20, 20),
        )

        self.label = ctk.CTkLabel(
            self,
            text="  Admin Panel",
            image=self.logo_image,
            compound="left",
            font=ctk.CTkFont(size=15, weight="bold"),
        )
        self.label.grid(row=0, column=0, padx=20, pady=20)

        self.home_button = NaviButton(
            self,
            text="Home",
            image=self.home_image,
            navigation_button_event=lambda: navigation_button_event("home"),
        )
        self.home_button.grid(row=1, column=0, sticky="ew")

        self.scan_button = NaviButton(
            self,
            text="Scan",
            image=self.chat_image,
            navigation_button_event=lambda: navigation_button_event("scan"),
        )
        self.scan_button.grid(row=2, column=0, sticky="ew")

        self.import_button = NaviButton(
            self,
            text="Import",
            image=self.add_user_image,
            navigation_button_event=lambda: navigation_button_event("import"),
        )
        self.import_button.grid(row=3, column=0, sticky="ew")

        self.admin_button = NaviButton(
            self,
            text="Admin",
            image=self.add_user_image,
            navigation_button_event=lambda: navigation_button_event("admin"),
        )
        self.admin_button.grid(row=4, column=0, sticky="ew")

        # grid 5 is empty

        self.appearance_mode_menu = ctk.CTkOptionMenu(
            self,
            values=["Light", "Dark", "System"],
            command=change_appearance_mode_event,
        )
        self.appearance_mode_menu.grid(row=6, column=0, padx=20, pady=20, sticky="s")
