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
    Checks if the local version is the latest. Only returns True if there is a newer version.
    :param version: the version currently installed
    :param nightly: if True, checks against nightly version
    """
    try:
        if nightly:
            log("Checking nightly version...")
            response = requests.get("https://raw.githubusercontent.com/MeltingDiamond/TBMM/main/version.txt")
            if response.status_code == 200:
                nightly_version = response.text.strip()  # Get the content and strip newline
                log(f"Latest nightly version: {nightly_version}")
                if version != nightly_version:
                    log(f"A newer nightly version is available: {nightly_version}")
                    return True
                else:
                    log("You are using the latest nightly version.")
                    return False
            else:
                log("Failed to fetch version info.")
                False
        else:
            log("Checking release version... (not yet implemented)")
            # TODO: Implement release version check (e.g. GitHub tags or releases)
    except Exception as e:
        log(f"Error during version check: {e}")

#update_check(1.4, True)