import yaml, locale, os
from pathlib import Path

scriptDir = Path(__file__).parent.absolute()

def get_system_language():
    lang, _ = locale.getdefaultlocale()
    return lang

def loadLocalisation(filename = None):

    if filename == None:
        filename = f"{get_system_language()}.yaml"
    
    #filename = "no_NB.yaml" # Uncomment to force a specific language
    
    filepath = f"{scriptDir}/translations/{filename}"

    if os.path.isfile(filepath) == False:
        filepath =f"{scriptDir}/translations/en_GB.yaml"

    with open(f"{scriptDir}/translations/{filename}", mode = "r") as translationFile:
        translations = yaml.safe_load(translationFile)

        return translations