# Anything that accesses the internet, for example if "import requests" is needed
import requests, webbrowser

windows_nightly_download_link = "https://nightly.link/MeltingDiamond/TBMM/workflows/build-cross-platform/main/TBMM-Windows.zip"
linux_nightly_download_link = "https://nightly.link/MeltingDiamond/TBMM/workflows/build-cross-platform/main/TBMM-Linux.zip"
release_download_link = "https://github.com/MeltingDiamond/TBMM/releases/latest"

def open_link(url):
    webbrowser.open_new(url)

def download_new_tbmm_version(os, nightly = False):
    if nightly:
        if os == "Windows":
                open_link(windows_nightly_download_link)
        elif os == "Linux":
            open_link(windows_nightly_download_link)
    else:
        open_link(release_download_link)

def update_check(version, log, nightly=False):
    """
    Checks if the local version is older than the latest nightly. 
    Returns True if there is a newer version.
    
    :param version: the version currently installed (e.g., "nightly-20250725203538")
    :param nightly: if True, checks against nightly version
    """
    try:
        if not nightly:
            log("Release version check not implemented yet.")
            return False
            response = requests.get(release_download_link, allow_redirects=True)

        log("Checking nightly version...")
        response = requests.get("https://raw.githubusercontent.com/MeltingDiamond/TBMM/main/version.txt")
        if response.status_code != 200:
            log("Failed to fetch version info.")
            return False

        latest_version = response.text.strip()
        log(f"Latest nightly version: {latest_version}")

        # Extract numeric part of nightly version and compare as integers
        local_num = int(version.split("-")[1])
        latest_num = int(latest_version.split("-")[1])

        if local_num < latest_num:
            log(f"A newer nightly version is available: {latest_version}")
            return True

        log("You are using the latest nightly version.")
        return False

    except Exception as e:
        log(f"Error during version check: {e}")
        return False
