# Anything that accesses the internet, for example if "import requests" is needed
import requests, webbrowser

windows_nightly_download_link = "https://nightly.link/MeltingDiamond/TBMM/workflows/build-cross-platform/main/TBMM-Windows.zip"
linux_nightly_download_link = "https://nightly.link/MeltingDiamond/TBMM/workflows/build-cross-platform/main/TBMM-Linux.zip"
release_download_link = "https://github.com/MeltingDiamond/TBMM/releases/latest"

def download_new_tbmm_version(os, nightly = False):
    if nightly:
        if os == "Windows":
                webbrowser.open(windows_nightly_download_link)
        elif os == "Linux":
            webbrowser.open(windows_nightly_download_link)
    else:
        webbrowser.open(release_download_link)

def update_check(version, nightly=False):
    """
    Checks if the local version is the latest. Only returns True if there is a newer version.
    :param version: the version currently installed
    :param nightly: if True, checks against nightly version
    """
    try:
        if nightly:
            print("Checking nightly version...")
            response = requests.get("https://raw.githubusercontent.com/MeltingDiamond/TBMM/main/version.txt")
            if response.status_code == 200:
                nightly_version = response.text.strip()  # Get the content and strip newline
                print(f"Latest nightly version: {nightly_version}")
                if version != nightly_version:
                    print(f"A newer nightly version is available: {nightly_version}")
                    return True
                else:
                    print("You are using the latest nightly version.")
                    return False
            else:
                print("Failed to fetch version info.")
                False
        else:
            print("Checking release version... (not yet implemented)")
            # TODO: Implement release version check (e.g. GitHub tags or releases)
    except Exception as e:
        print(f"Error during version check: {e}")

#update_check(1.4, True)