import json
import os
from tbmm.app.config import AppConfig

class ConfigStore:
    @staticmethod
    def load_or_default():
        path = os.path.join(os.getcwd(), AppConfig.CONFIG_FILE_NAME)
        if os.path.exists(path):
            with open(path, "r") as f:
                data = json.load(f)
            # you can map that into a config object
            return data
        else:
            # return default as dict or instance
            default = {
                "mod_repo_url": AppConfig.DEFAULT_MOD_REPO_URL,
                "install_dir": AppConfig.DEFAULT_INSTALL_DIR,
                "version_number": AppConfig.version_number
            }
            return default

    @staticmethod
    def save(config_data):
        path = os.path.join(os.getcwd(), AppConfig.CONFIG_FILE_NAME)
        with open(path, "w") as f:
            json.dump(config_data, f, indent=2)