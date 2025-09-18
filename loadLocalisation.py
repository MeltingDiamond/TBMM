import yaml
from pathlib import Path

scriptDir = Path(__file__).parent.absolute()

def loadLocalisation(filename):
    with open(f"{scriptDir}/translations/{filename}", mode = "r") as translationFile:
        translations = yaml.safe_load(translationFile)

        return translations