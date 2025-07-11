# Anything that accesses the internet, for example if "import requests" is needed
import requests

windows_nightly_download_link = "https://nightly.link/MeltingDiamond/TBMM/workflows/build-cross-platform/main/TBMM-Windows.zip"
linux_nightly_download_link = "https://nightly.link/MeltingDiamond/TBMM/workflows/build-cross-platform/main/TBMM-Linux.zip"

def update_check(version, nightly = False): # Checks if the version you hve installed is the newest version
    if nightly:
        print("Download nightly WIP")
        response =requests.get("https://github.com/MeltingDiamond/TBMM/blob/main/version.txt")
        if response.status_code == 200:
            contents = response.json()
            print(contents)
    else:
        print("Download release WIP")

update_check(1.4, True)