#from tbmm.app.config import AppConfig
from tbmm.app.ui_manager import UIManager
from tbmm.persistence.config_store import ConfigStore
#from tbmm.services.mod_service import ModService

class AppController:
    def __init__(self):
        # load or initialize config
        self.config = ConfigStore.load_or_default()
        # initialize services
        #self.mod_service = ModService(self.config)
        # UI manager
        self.ui_manager = UIManager(self, self.config)

    def run(self):
        self.ui_manager.start_main_loop()

    # Example method: called by UI when user wants to install a mod
    def install_mod(self, mod_id):
        # You may want to wrap in try/except or run in background
        self.mod_service.install_mod(mod_id)
        # Then notify UI to refresh state etc
        self.ui_manager.refresh_mod_list()
