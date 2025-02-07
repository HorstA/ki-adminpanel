import customtkinter as ctk
from AdminFrame import AdminFrame
from HomeFrame import HomeFrame
from ImportFrame import ImportFrame
from loguru import logger
from NavigationFrame import NavigationFrame
from ScanFrame import ScanFrame
from utils.utils import init_app


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        init_app()

        self.title("KI-Tools Admin Panel")
        self.geometry("700x450")

        # set grid layout 1x2
        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.navigation_frame = NavigationFrame(
            self,
            self.navigation_button_event,
            self.change_appearance_mode_event,
            corner_radius=0,
        )
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")

        self.home_frame = HomeFrame(self, corner_radius=0, fg_color="transparent")
        self.scan_frame = ScanFrame(self, corner_radius=0, fg_color="transparent")
        self.import_frame = ImportFrame(self, corner_radius=0, fg_color="transparent")
        self.admin_frame = AdminFrame(self, corner_radius=0, fg_color="transparent")

        self.select_frame_by_name("home")

    def select_frame_by_name(self, name):
        # set button color for selected button
        self.navigation_frame.home_button.configure(
            fg_color=("gray75", "gray25") if name == "home" else "transparent"
        )
        self.navigation_frame.scan_button.configure(
            fg_color=("gray75", "gray25") if name == "scan" else "transparent"
        )
        self.navigation_frame.import_button.configure(
            fg_color=("gray75", "gray25") if name == "import" else "transparent"
        )
        self.navigation_frame.admin_button.configure(
            fg_color=("gray75", "gray25") if name == "admin" else "transparent"
        )

        # show selected frame
        if name == "home":
            self.home_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.home_frame.grid_forget()
        if name == "scan":
            self.scan_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.scan_frame.grid_forget()
        if name == "import":
            self.import_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.import_frame.grid_forget()
        if name == "admin":
            self.admin_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.admin_frame.grid_forget()

    def navigation_button_event(self, name):
        self.select_frame_by_name(name)

    def change_appearance_mode_event(self, new_appearance_mode):
        ctk.set_appearance_mode(new_appearance_mode)


if __name__ == "__main__":
    app = App()
    app.mainloop()
    # input("Press Enter to exit...")
