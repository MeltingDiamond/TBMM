# Anything that accesses the internet, for example if "import requests" is needed
import requests

windows_nightly_download_link = "https://nightly.link/MeltingDiamond/TBMM/workflows/build-cross-platform/main/TBMM-Windows.zip"
linux_nightly_download_link = "https://nightly.link/MeltingDiamond/TBMM/workflows/build-cross-platform/main/TBMM-Linux.zip"

def update_check(nightly = False): # Checks if the version you hve installed is the newest version
    if nightly:
        print("Download nightly WIP")
    else:
        print("Download release WIP")