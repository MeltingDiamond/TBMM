import os

# Example default configuration
class AppConfig:
    version_number = "0.06.1"
    DEFAULT_MOD_REPO_URL = "https://example.com/mods"
    DEFAULT_INSTALL_DIR = os.path.expanduser("~/TheBibites/Mods")
    CONFIG_FILE_NAME = "tbmm_config.json"
