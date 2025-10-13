import tkinter as tk
#from tbmm.ui.widgets.mod_item_widget import ModItemWidget

class MainWindow(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self._build_ui()

    def _build_ui(self):
        # Example: a frame to hold mod items
        self.mods_frame = tk.Frame(self)
        self.mods_frame.pack(fill="both", expand=True)
        # For demo, just load a few stub mod items
        # In real life: fetch mod list from service, then create widgets dynamically
        # Example stub
        #dummy_mod = {"id": "mod1", "name": "Mod One", "version": "1.0"}
        #w = ModItemWidget(self.mods_frame, dummy_mod, self.controller)
        #w.pack(padx=5, pady=5)

    def refresh_mod_list(self):
        # Clear existing, reload from controller / service, recreate widgets
        for child in self.mods_frame.winfo_children():
            child.destroy()
        mod_list = self.controller.mod_service.get_mod_list()
        for mod in mod_list:
            w = ModItemWidget(self.mods_frame, mod, self.controller)
            w.pack(padx=5, pady=5)
