import tkinter as tk
from tbmm.ui.windows.main_window import MainWindow

class UIManager:
    def __init__(self, controller, config):
        self.controller = controller
        self.config = config
        self.root = tk.Tk()
        self.main_window = None

    def start_main_loop(self):

        self.root.title(f"TBMM {self.config['version_number']}")

        # Get screen width and height
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Set window size and position to fullscreen windowed
        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.8)

        self.root.geometry(f"{window_width}x{window_height}+{int((screen_width - window_width) / 2)}+{int((screen_height - window_height) / 2)}")
        self.root.minsize(1000, 550)



        self.main_window = MainWindow(self.root, self.controller)
        self.main_window.pack(fill="both", expand=True)
        self.root.mainloop()

    def refresh_mod_list(self):
        if self.main_window:
            self.main_window.refresh_mod_list()

    # Optionally add methods to open settings, progress windows etc