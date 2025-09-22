import requests, platform, os, sys, base64, shutil, time, json, subprocess, zipfile, io

# Remove all imports from tkinter and have all UI import stuff in UI.py
# For example instead of importing "from tkinter import filedialog" do from UI import filedialog
# UI would be the UI backend used here.
# Network would be the network backend used here.
from tkinter import Label, Button, Frame, Checkbutton, IntVar, Toplevel, messagebox, StringVar, OptionMenu
from pathlib import Path
from threading import Thread

from UI import filedialog_askopenfile, filedialog_asksaveasfilename, create_window, create_main_page_ui, create_download_mods_page_ui, create_credits_page_ui
from UI import create_more_tools_page_ui, create_game_version_page_ui, on_hover, hide_all_tooltips, on_checkbutton_hover, on_checkbutton_leave, CustomTooltip
from Networking import update_check, download_new_tbmm_version, open_link, download_modse, fetch_filenames, start_download, get_mod_url, get_filename_from_response
from Networking import get_website_name, get_file_contents

# TODO
# Add a latest_log.txt file used purly for logs from the last time TBMM was ran. 
# log.txt is a global log file, but maybe cap it at some kind of size.
# Move more of the UI code from here to UI.py
# Move more of the networking code from here to Networking.py
# Finnish adding support to linux
# Finnish adding support for Mac

# If you want to add support for any other os feel free to do so,
# but MeltingDiamond will only support Windows, Linux and Mac (OSes that the bibites officially supports).

# What os this is running on
os_map = {
    "Windows": "Windows",
    "Darwin": "Mac",
    "Linux": "Linux"
}
OS_TYPE = os_map.get(platform.system(), "Unknown")

# Setup global os specific variables
if OS_TYPE == "Windows":
    # Gets userpath (Usually C:\Users\username)
    USERPROFILE = os.environ['USERPROFILE']
    FILETYPES = [("Executable files", "*.exe")]
elif OS_TYPE == "Linux":
    USERPROFILE = os.environ['HOME']
    FILETYPES = [("Executable files", "*.x86_64"), ("All files", "*.*")] # First is linux specific format, then all files in case they don't use the linux version
elif OS_TYPE == "Mac":
    USERPROFILE = "Unknown" # Someone using MacOS please fix
    FILETYPES = [("Executable files", "*.app"), ("All files", "*.*")] # First is mac specific format, then all files in case they don't use the linux version
else:
    USERPROFILE = os.environ['HOME'] # Just guessing that HOME is what most OSses use
    FILETYPES = [("All files", "*.*")] # Allow choosing all file types (You can't know which version they are running)

# The stable version is the version that gets released on github and is never left in a broken state (No broken code should be in the release version)
# The nightly version auto built in workflow run might be left slightly broken (Try not to make your last commit leave broken code)

# Version number of the next version to be released, not the bibites game version. Must be string
version_number = "0.06.1" # (stable version)

nightly_version = "__VERSION__" # Gets replaced during workflow build with latest version (DO NOT CHANGE, unless you change the name in the workflow too)

# Should it check and download nightly version
if nightly_version.startswith("__VERSION"):
    is_nightly = False
else:
    is_nightly = True

# Store every url that can be used to download TBM mod data from
# The list should be ordered from most up to date and most uptime to least up to date and least uptime.
add_first = "https://api.github.com/repos/MeltingDiamond/TBMM-Mods/contents/Mods" # This is the original keep it first unless I say otherwise - MeltingDiamond
mod_repo_urls = [add_first, "https://www.dropbox.com/scl/fo/fpcl07m7573flcbho85wk/ABr3cK3iIgFC7-QZe_mPpuY?rlkey=8wb5869lkawgcxpwwu0petu3t&st=0tyabw62&dl=1"]

# Variable to hold game version
Game_version = 'All'

# List that holds versions of The Bibites that TBMM has mods for
list_of_versions = ["0.5.0", "0.5.1", "0.6.0.1"]
list_of_versions_link_windows = {"0.5.0" : "https://www.dropbox.com/scl/fi/c1kypn1j4f67h1ezyyehb/the-bibites-0.5.0-windows-64x.zip?rlkey=zojdpcokxelsnjn7pmdgpbi50&st=0p7ria1e&dl=1","0.5.1" : "https://www.dropbox.com/scl/fi/zapwgdrfsxokopijrpp5d/The-Bibites-0.5.1-Windows-64x.zip?rlkey=2hu5kba5uddo2rwtleegr2sv8&st=i373zbys&dl=1", "0.6.0.1" : "https://www.dropbox.com/scl/fi/boh31txr00v77i95hbbai/The-Bibites-0.6.0.1-Windows-64x.zip?rlkey=hkqwkpjy7e5r32t1lau316d9e&st=k5ef2fja&dl=1"} # Direct links to the download windows version
list_of_versions_link_mac = {"0.5.0" : "None","0.5.1" : "https://www.dropbox.com/scl/fi/s490adgdpdb729mdwp7hm/The-Bibites-0.5.1-Mac-Universal.zip?rlkey=03qab761ta5yi7w3d4iqrxln0&st=eoze7gc8&dl=1", "0.6.0.1" : "https://www.dropbox.com/scl/fi/igxy7fq16yl7ieqjh994v/The-Bibites-0.6.0.1-Mac-Universal.zip?rlkey=wfquramlnyf77af2znrbljwbh&st=urrvwiue&dl=1"} # Direct links to the download mac version
list_of_versions_link_linux = {"0.5.0" : "None","0.5.1" : "https://www.dropbox.com/scl/fi/pukgn05ie6gs08qi1havf/The-Bibites-0.5.1-Linux.zip?rlkey=ghgqnrg2yygsi6xo1bl8nlsmw&st=fgzaru3d&dl=1", "0.6.0.1" : "https://www.dropbox.com/scl/fi/vflvk4x6bf2thohddftqj/The-Bibites-0.6.0.1-Linux.zip?rlkey=ubn7srnx2nspfwb5wy95r1a5j&st=1bjvg715&dl=1"} # Direct links to the download linux version

# Discord invite link
Discord_invite_link = "https://discord.gg/ZNPCZPDhCS"

# Used to display what page the user is on
page = ''

# Tooltip
tooltip_state = {
    'hover_index': None,
    'hover_widget': None
}
tooltips = {} # Dictionary to hold tooltips

# List to store mod names globaly
downloaded_mods_list = []
mod_names = []
installed_mods_list = []
mod_vars = []

# Cache variables
mod_content_cache = {}
mod_names_cache = []
cache_time = 0.0
cache_duration = 86400  # Cache duration in seconds (24 hours)

# Settings dictionary
settings = {}
Game_folder = None # Default to none because it needs to be initialised on start
bepinex_folder = None # BepInEx isn't installed by default and needs to be checked if is installed

# Gets the current time in correct time format to be placed in log.txt
def get_time():
    '''Gets the current time and date in a human readable format'''
    current_time = time.strftime('%x %X')
    return current_time

# Function to get the game path
def get_game_path():
    '''User input for getting the path to The Bibites game exe'''
    global Game_path, Game_folder, bepinex_folder
    if Game_folder:
        Temp_Game_path = filedialog_askopenfile(initialdir=Game_folder, filetypes=FILETYPES) # Store game path without overwriting existing game path
    else:
        Temp_Game_path = filedialog_askopenfile(filetypes=FILETYPES) # Store game path without overwriting existing game path
    if Temp_Game_path:
        Game_path = Temp_Game_path.name
        Game_folder = os.path.dirname(Game_path)
        bepinex_folder = os.path.join(Game_folder, "BepInEx")
        settings['Game_path'] = Game_path
        settings['Game_folder'] = Game_folder
        settings['bepinex_folder'] = bepinex_folder
        save_settings()
    game_path_label.config(text=f'Game path: {Game_path}', font=("Arial", 9))

# Function to save the selected version and close the window
def get_game_version():
    def save_version():
        global Game_version
        Game_version = selected_version.get()
        if Game_version == "All":
            version_label.config(text=f"You have selected {Game_version} game versions.", font=("Arial", 13))
        else:
            version_label.config(text=f"You have selected game version {Game_version}.", font=("Arial", 13))
        settings['Game_version'] = Game_version
        save_settings()
        game_version_window.destroy()

    ui = create_game_version_page_ui(window, handlers={
        'Game_version': Game_version,
        'list_of_versions': list_of_versions,
        'screen_width': window.winfo_screenwidth(),
        'screen_height': window.winfo_screenheight(),
    })

    game_version_window = ui['window']
    selected_version = ui['selected_version']
    ui['confirm_button'].config(command=save_version)

# Download a specific version of the bibites which TBMM has mods for
def download_the_bibites_of_x_version(version):
    '''Downloads a specific version of The Bibites'''
    # Retrieve the download link for the selected version
    if OS_TYPE == "Windows":
        list_of_versions_link = list_of_versions_link_windows
    elif OS_TYPE == "Mac":
        list_of_versions_link = list_of_versions_link_mac
    elif OS_TYPE == "Linux":
        list_of_versions_link = list_of_versions_link_linux

    version_to_download = list_of_versions_link.get(version)
    if not version_to_download:
        messagebox.showerror("Error", "Selected version does not exist.")
        return

    bibites_game_name = get_filename_from_response(version_to_download)

    # Open a file save dialog
    file_path = filedialog_asksaveasfilename(
        defaultextension=".zip", 
        filetypes=[("ZIP files", "*.zip"), ("All files", "*.*")],
        title="Save Bibites File As",
        initialfile = bibites_game_name
    )

    # If the user cancels the save dialog, exit the function
    if not file_path:
        return

    # Simulate the file download (replace with actual download logic)
    def download(version_to_download, file_path):
        try:
            response = requests.get(version_to_download, stream=True)
            response.raise_for_status()  # Raise an error for HTTP issues
            
            # Save the file to the selected path
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192): 
                    f.write(chunk)
            
            messagebox.showinfo("Success", f"Version {version} downloaded successfully!\nMake sure to update the game path after extracting {bibites_game_name}")
        except Exception as e:
            messagebox.showerror("Download Error", f"An error occurred: {str(e)}")

    download_bibites_of_x_version_thread = Thread(target=download, args=(version_to_download, file_path))
    download_bibites_of_x_version_thread.start()

def get_the_bibites():
    '''UI to download the bibites'''
    # Calculate the width and height for the window
    width_height = f"{int(screen_width / 3.5)}x{int(screen_height / 2.5)}"

    # Create a new window for selecting the game version
    download_the_bibites_window = Toplevel(window)
    download_the_bibites_window.title("Download The Bibites")
    download_the_bibites_window.geometry(width_height)
    window.minsize(800, 432)
    download_the_bibites_window.resizable(False, False)

    # Create a frame to hold the game version options
    download_the_bibites_frame = Frame(download_the_bibites_window)
    download_the_bibites_frame.pack(pady=20)

    # Label for instructions
    label = Label(download_the_bibites_frame, text=f"Choose the version of The Bibites {OS_TYPE} to download:", font=("Arial", 11, "bold"))
    label.pack(pady=10)

    # Create a StringVar to store the selected version
    selected_version = StringVar(value=list_of_versions[len(list_of_versions) - 1])  # Default to the first version in the list

    # Create an OptionMenu (dropdown) for the game versions
    version_dropdown = OptionMenu(download_the_bibites_frame, selected_version, *list_of_versions)
    version_dropdown.pack(pady=10)

    label = Label(download_the_bibites_frame, text="If you can't find a version,\nit is because there are no mods for it", font=("Arial", 11))
    label.pack(pady=10)

    download_button = Button(download_the_bibites_window, text="Confirm", command=lambda: download_the_bibites_of_x_version(selected_version.get()))
    download_button.pack(pady=10)

# Function to get the version of the bibites the mod is made for
def get_mod_game_version(mod_name):
    '''Gets the version a mod is made for'''
    file_contents = get_file_contents(mod_name, cache_duration, save_cache_to_file, mod_content_cache, log, mod_repo_urls)
    if file_contents:

        lines = file_contents.split('\n') # Split the content into lines

        game_version_line = next((line for line in lines if line.startswith('game version: ')), None) # Find the line containing the URL

        if game_version_line:
            game_version = game_version_line.replace('game version: ', '').strip() # Extract the game version from the line
            return game_version
    return None

def get_bibites_to_download(mod_name):
    file_contents = get_file_contents(mod_name, cache_duration, save_cache_to_file, mod_content_cache, log, mod_repo_urls)
    lines = file_contents.splitlines()
    bibites_to_download = next((line for line in lines if line.startswith('bibites:')), None) # if there are bibites download them into the dibites folder
    if bibites_to_download:
        bibites_to_download = bibites_to_download.replace('bibites: ', '').strip()
        # Check if there are multiple URLs separated by commas
        if ',' in bibites_to_download:
            bibites_to_download = bibites_to_download.split(', ')
        else:
            # If there is only one URL, make it a list
            bibites_to_download = [bibites_to_download]
        return bibites_to_download
    return None

def get_mod_install_description(mod_name):
    file_contents = get_file_contents(mod_name, cache_duration, save_cache_to_file, mod_content_cache, log, mod_repo_urls)
    if file_contents:
        lines = file_contents.split('\n')
        install_line = next((line for line in lines if line.startswith('install: ')), None)
        if install_line:
            instruction = install_line.replace('install:', '').strip()
            return instruction

def get_mod_description(mod_name):
    '''Get the description of a mod using the name'''
    file_contents = get_file_contents(mod_name, cache_duration, save_cache_to_file, mod_content_cache, log, mod_repo_urls)
    if file_contents:
        description = ""
        lines = file_contents.split('\n')

        developer_line = next((line for line in lines if line.startswith('original developer: ')), None)
        if developer_line:
            description = developer_line.replace('original developer:', 'Developer:').strip()

        game_version_line = next((line for line in lines if line.startswith('game version: ')), None)
        if game_version_line:
            description = f"{description}\n{game_version_line.replace('game version:', 'Game version:').strip()}"

        instruction = get_mod_install_description(mod_name)
        if instruction == "replace":
            install_line = "Mod type: BibitesAssembly.dll"
        if instruction == "replace+":
            install_line = "Mod type: BibitesAssembly.dll, but needs more files"
        if instruction == "BepInEx":
            install_line = "Mod type: BepInEx"
        if instruction == "BepInEx+":
            install_line = "Mod type: BepInEx, but needs more files"

            description = f"{description}\n{install_line}"

        description_line = next((line for line in lines if line.startswith('description: ')), None)
        if description_line:
            description = f"{description}\n{description_line.replace('description:', '').strip()}"
            return description
        else:
            return f"{description}\nNo detailed information available."
    return f"File content not found, can't get description for {mod_name}"

# Don't use when installing mods only when actually deleting a mod completely
def safe_unlink(path, retries=3, delay=1):
    """
    Attempt to unlink (delete) a file or folder with retries.
    
    :param path: Path to the file or folder to unlink
    :param retries: Number of retry attempts
    :param delay: Delay (in seconds) between retries
    """
    for attempt in range(retries):
        try:
            # Try to remove the folder
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)
            print(f"Successfully unlinked {path}")
            return True
        except Exception as e:
            print(f"Attempt {attempt + 1} to unlink {path} failed: {e}")
            time.sleep(delay)
    print(f"Failed to unlink {path} after {retries} retries.")
    return False

def download_mods():
    download_modse(downloaded_mods, mod_names, mod_vars, not_installed_mods, cache_duration, mod_repo_urls, mod_names_cache, cache_time, downloading, log_file, mod_content_cache, handlers={
        'log': log,
        'get_mod_install_description': get_mod_install_description,
        'save_cache_to_file': save_cache_to_file,
        'get_file_contents': get_file_contents,
        'safe_unlink': safe_unlink,
        'get_time': get_time,
        'status_label': status_label
    })

# Only works with replace mods currently. So if a BepInEx mod is installed as well this wont work correctly
def install_mod_by_replace_dll(mod_name, not_installed_mod_folder, not_installed_mod_path, installed_mods_list): # Used when replace install instruction is needed
    try:
        # If mod isnt installed and no other mod is installed
        if f'{not_installed_mod_path}' not in os.listdir(not_installed_mod_folder) and len(installed_mods_list) == 0 and not os.path.exists(f'{Game_folder}/The Bibites_Data/Managed/BibitesAssembly.dll.TBM'):
            log_message = f"Installing {mod_name}"
            log(log_message, False)
            status_label.config(text=log_message)

            os.symlink(not_installed_mod_path, os.path.join(Game_folder, "The Bibites_Data", "Managed", "BibitesAssembly.dll.TBM"), target_is_directory=False)

            installed_mods_list = mod_name
            print(installed_mods_list)
            with open(installed_mods, 'w') as file: # Write the installed_mod_list to keep it after TBMM closes
                file.write(installed_mods_list)

            log_message = f"Installed {mod_name}"
            log(log_message, False)
            status_label.config(text=log_message)

        # If any other mod is installed replace the curent one
        else:
            log_message = ""
            for mod in installed_mods_list:
                log_message = f"{log_message}{mod} "

            log_message = f"Replacing {log_message}with {mod_name}"
            log(log_message, False)
            status_label.config(text=log_message)

            # Check if mod you are trying to install is installed if it isn't install it
            if mod_name not in installed_mods_list:
                # move other mods back to uninstalled location if there is an installed mod in installed_mods.txt
                for mod in installed_mods_list:
                    safe_unlink(os.path.join(Game_folder, "The Bibites_Data", "Managed", "BibitesAssembly.dll.TBM"))

                # Install the mod
                os.symlink(f'{not_installed_mod_path}', os.path.join(Game_folder, "The Bibites_Data", "Managed", "BibitesAssembly.dll.TBM"), target_is_directory=False) # Move the mod

                # Add the installed mod to the installed_mods_list
                installed_mods_list = [mod_name]
                with open(installed_mods, 'w') as file: # Write the installed_mod_list to keep it after TBMM closes
                    file.write(mod_name)

                # Display that mod is installed
                log_message = f"Installd {mod_name}"
                log(log_message, False)
                status_label.config(text=log_message)

                installed_mods_list_pretty_for_display = [] # List stores the installed mods without .TBM to make it prettier
                for mod in installed_mods_list:
                    mod = mod.split('.')[0]
                    installed_mods_list_pretty_for_display.append(mod)
                installed_mod_label.config(text=f"Installed mod: {''.join(installed_mods_list_pretty_for_display)}", font=("Arial", 12))
                save_settings()
    except Exception as e:
        messagebox.showerror("Error", f"Unexpected error: {e}")
        log(f"Unexpected error: {e}", True)

# Install BepInEx mods
def install_mod_bepinex(mod_name, not_installed_mod_folder):
    if not bepinex_folder:
        log("You need to set a path to a bibites installation with BepInEx installed\nAfter doing so try again", save_to_file=False)
        return

    if not os.path.isdir(os.path.join(bepinex_folder, 'plugins')):
        log("Your bepinex install is broken\nplease start the game in vanilla once before trying again.", save_to_file=False)
        return

    log('BepInEx is installed', save_to_file=False)
    
    if mod_name in installed_mods_list:
        print("Is installed")
        return
    print(mod_name + " is not installed, create softlink (symlink)")
    files = os.listdir(not_installed_mod_folder)
    for file in files: 
        if file.endswith(".dll"):
            install_location = os.path.join(bepinex_folder, "plugins", file)
            if not os.path.isfile(install_location):
                os.symlink(os.path.join(not_installed_mod_folder, file), os.path.join(bepinex_folder, "plugins", file), target_is_directory=False)
                print("ITS THE MOD")
        else:
            print("NOT SAID FILE, I MEAN MOD")

def download_bibites(bibites_to_download):
    for bibite in bibites_to_download:
        filename = get_filename_from_response(bibite) # Get filename to determin if it is .bb8 or .bb8template
        log(f"Downloading bibite {filename}", False)
        if OS_TYPE == "Windows":
            if filename.endswith(".bb8"):
                location = f'{USERPROFILE}/AppData/LocalLow/The Bibites/The Bibites/Bibites'
            elif filename.endswith(".bb8template"):
                location = f'{USERPROFILE}/AppData/LocalLow/The Bibites/The Bibites/Bibites/Templates'
        elif OS_TYPE == "Linux":
            if filename.endswith(".bb8"):
                location = f'{USERPROFILE}/.config/unity3d/The Bibites/The Bibites/Bibites'
            elif filename.endswith(".bb8template"):
                location = f'{USERPROFILE}/.config/unity3d/The Bibites/The Bibites/Bibites/Templates'
        else:
            return

        start_download(bibite, location, log, status_label, downloading, safe_unlink, log_file, get_time) # Downloads the bibite to the specified location

def install_mods(): # Install a mod so you can play modded
    '''Installs the selected downloaded mods'''

    if os.path.exists(Game_path) == False:
        log(f"Game path is {Game_path}, you need to set a game path to be able to install mods correctly", False)
        status_label.config(text=f"Game path is {Game_path}, you need to set a game path to be able to install mods correctly")
        return

    # Install selected mods
    for mod_index in downloaded_mods_listbox.curselection():
        mod_name = downloaded_mods_listbox.get(mod_index)

        install_instruction = get_mod_install_description(mod_name)
        not_installed_mod_folder = f'{not_installed_mods}/{install_instruction}/{mod_name}'

        bibites_to_download = get_bibites_to_download(mod_name)

        with open(installed_mods, 'r') as file:
            installed_mods_list = file.read().splitlines()

        if len(os.listdir(not_installed_mod_folder)) == 0 and mod_name not in installed_mods_list: # Check is mod exists or is installed if it is not any of those download it again
            file_contents = get_file_contents(mod_name, cache_duration, save_cache_to_file, mod_content_cache, log, mod_repo_urls)
            url = get_mod_url(file_contents)
            if url:
                start_download(url, not_installed_mod_folder, log, status_label, downloading, safe_unlink, log_file, get_time)

        if mod_name not in installed_mods_list: # The mod is not installed and need to get path to install it
            for file in os.listdir(not_installed_mod_folder):
                if file.endswith('.dll') or file.endswith('dll.TBM'):
                    dll = file
                    break

            not_installed_mod_path = f'{not_installed_mod_folder}/{dll}'

            if install_instruction == "replace":
                if not_installed_mod_path.endswith('.dll'):
                    os.rename(not_installed_mod_path, f'{not_installed_mod_path}.TBM')
                    not_installed_mod_path = f'{not_installed_mod_path}.TBM'
                install_mod_by_replace_dll(mod_name, not_installed_mod_folder, not_installed_mod_path, installed_mods_list)

                if bibites_to_download:
                    download_bibites(bibites_to_download)

            elif install_instruction == "replace+":
                log(f"Install instruction \"replace+\" is not yet added", False)
                status_label.config(text=f"Install instruction \"replace+\" is not yet added")

            elif install_instruction == "BepInEx":
                log(f"Install instruction \"BepInEx\" will be implemented after \"replace\" is implemented", False)
                install_mod_bepinex(mod_name, not_installed_mod_folder)

            elif install_instruction == "BepInEx+":
                log(f"Install instruction \"BepInEx+\" is not yet added", False)
                status_label.config(text=f"Install instruction \"BepInEx+\" is not yet added")

            else: # TBMM can't install the mod yet
                log(f"{mod_name} can't be installed because TBMM does not have instructions implemented for: {install_instruction}", False)
                status_label.config(text=f"{mod_name} can't be installed because TBMM does not have instructions implemented for: {install_instruction}")

        # The mod you are trying to install ia already installed
        else:
            log(f"{mod_name} is aleady installed", False)
            status_label.config(text=f"{mod_name} is aleady installed") # Display that mod is already installed
            installed_mods_list_pretty_for_display = [] # List stores the installed mods without .TBM to make it prettier
            for mod in installed_mods_list:
                mod = mod.split('.')[0]
                installed_mods_list_pretty_for_display.append(mod)
            installed_mod_label.config(text=f"Installed mod: {''.join(installed_mods_list_pretty_for_display)}", font=("Arial", 12))

            settings['installed_mods_list'] = installed_mods_list
            save_settings()

# Function to save cache to a file
def save_cache_to_file(mod_names_cache, cache_time):
    all_cache_data = {"mod_names_cache" : mod_names_cache,"cache_time" : cache_time, "mod_content_cache" : mod_content_cache}
    with open(cache_file, 'w') as file:
        json.dump(all_cache_data, file, indent=2)
    log("Saved cache to file.", False)
    status_label.config(text="Saved cache to file.")

# Function to reset and cleanup cache
def reset_cache():
    '''Resets the cash and '''
    global mod_names_cache, mod_content_cache, cache_time

    # Initialize cleaned cache variables
    cleaned_mod_content_cache = {}

    # Remove mods from mod_content_cache if they are not in mod_names_cache
    for mod_name, mod_data in mod_content_cache.items():
        # Extract mod name without path prefix
        mod_name_only = mod_name.split('/')[-1]  # e.g., "MoreMaterialsMod.TBM"

        # Check if the mod is listed in mod_names_cache
        if mod_name_only in mod_names_cache:
            # Check if the mod content can be fetched (valid mod)
            content = get_file_contents(mod_name_only, cache_duration, save_cache_to_file, mod_content_cache, log, mod_repo_urls)  # Using the name to check if mod exists

            if content:  # If mod content can be fetched, keep it
                cleaned_mod_content_cache[mod_name] = mod_data
            else:
                log(f"Invalid mod content, removing: {mod_name}", True)
                status_label.config(text=f"Invalid mod content, removing: {mod_name}")
        else:
            log(f"Mod not in mod_names_cache, removing: {mod_name}", True)
            status_label.config(text=f"Mod not in mod_names_cache, removing: {mod_name}")

    # Update mod_content_cache with only valid mods that are also in mod_names_cache
    mod_content_cache = cleaned_mod_content_cache
    cache_time = time.time()  # Reset cache time to current time

    # Save the cleaned cache to file
    save_cache_to_file(mod_content_cache, cache_time)
    log("Cache reset, and invalid mods removed.", False)
    status_label.config(text="Cache reset, and invalid mods removed.")

def save_settings(): # Save to settings file
    global settings
    with open(settings_file, 'w') as file:
        json.dump(settings, file, indent=2)

# Function to swap to main page and display downloaded mods
def list_downloaded_mods():
    global page
    if page == "Find_Mods":
        downloadable_mods_frame.pack_forget()

        main_frame.pack()

    if page == "More_Tools":
        more_tools_frame.pack_forget()

        main_frame.pack()

    if page == "Credits":
        credits_frame.pack_forget()
        
        main_frame.pack()

        page = "More_Tools"

    if page != "Main Page":

        downloaded_mods_listbox.delete(0, "end")  # Clear existing list

        #check_for_local_mods() # Check for downloaded mods that are not registerd
        
        # Display downloaded mods with tooltip
        if os.path.isfile(downloaded_mods) and os.stat(downloaded_mods).st_size != 0:
            downloaded_mods_list = ""
            with open(downloaded_mods, "r") as file:
                try:
                    downloaded_mods_list = [line.strip() for line in file.readlines()]
                    downloaded_mods_list = [mod.split('/')[-1] for mod in downloaded_mods_list]
                except:
                    pass
            if downloaded_mods_list:
                # A dictionary to hold tooltip instances for each index
                tooltips = {}

                for index, mod in enumerate(downloaded_mods_list):
                    mod_info = get_mod_description(mod)
                    downloaded_mods_listbox.insert("end", mod)

                    # Create tooltip object for this index
                    tooltips[index] = CustomTooltip(downloaded_mods_listbox, mod_info)

                # Bind mouse motion to detect item under cursor
                downloaded_mods_listbox.bind("<Motion>", lambda event, lb=downloaded_mods_listbox, t=tooltips: on_hover(event, lb, t, tooltip_state))
                downloaded_mods_listbox.bind("<Leave>", lambda event, t=tooltips: hide_all_tooltips(t))
        page = "Main Page"

# Function to swap to the page to where you can find and download mods
def download_mods_page():
    global page, mod_names

    def pack_main_page():
        # Swap on downloadable mods frame
        downloadable_mods_frame.pack()

    if page == 'Main Page':
        main_frame.pack_forget()
        pack_main_page()
        
    
    if page == "More_Tools":
        more_tools_frame.pack_forget()
        pack_main_page()
    
    if page == "Credits":
        credits_frame.pack_forget()
        pack_main_page()

        page = "More_Tools"

    if page != "Find_Mods":
        # Get the names of the available mods
        mod_names = fetch_filenames(log, cache_duration, mod_repo_urls, get_website_name, save_cache_to_file, status_label, mod_names, mod_names_cache, cache_time)  # Use cached data
        # Add the mod names to a checkbutton list
        populate_checkbuttons(mod_names)

        page = "Find_Mods"

# Show more tools page
def more_tools_page():
    global page

    if page == "Main Page":
        main_frame.pack_forget()
        
        more_tools_frame.pack()
        
        page = "More_Tools"

    if page == "Find_Mods":
        downloadable_mods_frame.pack_forget()
        
        more_tools_frame.pack()

        page = "More_Tools"
    
    if page == "Credits":
        credits_frame.pack_forget()
        
        more_tools_frame.pack()

        page = "More_Tools"

# Show credits page
def credits_page():
    global page

    if page == 'Main Page':
        main_frame.pack_forget()
        
        credits_frame.pack()
        
        page = "Credits"

    if page == "Find_Mods":
        downloadable_mods_frame.pack_forget()
        
        credits_frame.pack()

        page = "Credits"
    
    if page == "More_Tools":
        more_tools_frame.pack_forget()

        credits_frame.pack()
        
        page = "Credits"

def populate_checkbuttons(mod_names):
    global mod_vars, tooltips, tooltip_state
    tooltips = {}

    # Remove existing checkbuttons
    for widget in downloadable_mods_frame.winfo_children():
        if isinstance(widget, Checkbutton):
            widget.destroy()

    added_mods = set()
    mod_vars = []

    for mod_name in mod_names:
        mod_game_version = get_mod_game_version(mod_name)
        var = IntVar()
        mod_vars.append(var)

        if (mod_name not in added_mods) and (mod_game_version == Game_version or Game_version == "All"):
            chk = Checkbutton(downloadable_mods_frame, text=mod_name, variable=var, font=("Arial", 12))
            chk.pack(anchor='w', pady=5)

            mod_info = get_mod_description(mod_name)
            tooltips[chk] = CustomTooltip(chk, mod_info)

            # Bind motion and leave events
            chk.bind("<Motion>", lambda event, c=chk: on_checkbutton_hover(event, c, tooltips, tooltip_state))
            chk.bind("<Leave>", lambda event: on_checkbutton_leave(tooltips, tooltip_state))

            added_mods.add(mod_name)

# Starts the game with or without mods
def play_game(Modded):
    global Game_path
    if os.path.exists(Game_path):

        ScriptingAssemblies = f'{Game_folder}/The Bibites_Data/ScriptingAssemblies.json'
        with open(ScriptingAssemblies, "r") as file:
            ScriptingAssembliesText = json.load(file) # Index of 'BibitesAssembly.dll' is 68

        if Modded == ('No'):
            if OS_TYPE == "Windows":
                ScriptingAssembliesText['names'][68] = 'BibitesAssembly.dll.TBM'    # Edit what dll is loaded to the modded one
            elif OS_TYPE == "Linux":
                ScriptingAssembliesText['names'][67] = 'BibitesAssembly.dll.TBM'

            with open(ScriptingAssemblies, "w") as file:                 # Write the info
                json.dump(ScriptingAssembliesText, file)

            try:
                if OS_TYPE == "Windows": # Playing on windows
                    subprocess.Popen([Game_path]) # Run The Bibites without mods.
                    log("Playing without mods", False)
                    status_label.config(text="Playing without mods")
                
                elif OS_TYPE == "Linux": # Playing on Linux
                    subprocess.Popen([Game_path, "-force-vulkan"]) # Run The Bibites without mods.
                    log("Playing without mods", False)
                    status_label.config(text="Playing without mods")

            # Catch and display error to the user
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error running the game", f"Unexpected error: {e}")    # Display message box with error
                
                log(f"Error running the game: {e}", True)
                status_label.config(text=f"Error running the game: {e}") # Display error on status label
            except Exception as e:
                messagebox.showerror("Error", f"Unexpected error: {e}") # Display message box with error
                
                log(f"Unexpected error: {e}", True)
                status_label.config(text=f"Unexpected error: {e}") # Display error on status label

        if Modded == ('Yes'):
            if os.path.isfile(f'{Game_folder}/The Bibites_Data/Managed/BibitesAssembly.dll.TBM'):
                if OS_TYPE == "Windows":
                    ScriptingAssembliesText['names'][68] = 'BibitesAssembly.dll.TBM'    # Edit what dll is loaded to the modded one
                elif OS_TYPE == "Linux":
                    ScriptingAssembliesText['names'][67] = 'BibitesAssembly.dll.TBM'
                with open(ScriptingAssemblies, "w") as file:                            # Write the info
                    json.dump(ScriptingAssembliesText, file)
                log(f"You have installed a replace mod assuming you want to use that", False)
                status_label.config(text=f"You have installed a replace mod assuming you want to use that")
            else:
                log(f"You haven't installed a replace mod assuming you have intalled BepInEx mods. Please use the BepInEx play button.", False)
                status_label.config(text=f"You haven't installed a replace mod assuming you have intalled BepInEx mods. Please use the BepInEx play button.")
                return

            try:
                if OS_TYPE == "Windows": # Playing on windows
                    subprocess.Popen([Game_path]) # Run The Bibites without checking for mods.
                    with open(installed_mods, 'r') as file:
                        installed_mods_list = file.read().splitlines()
                        installed_mods_list_pretty_for_display = [] # List stores the installed mods without .TBM to make it prettier
                        for mod in installed_mods_list:
                            mod = mod.split('.')[0]
                            installed_mods_list_pretty_for_display.append(mod)
                    log(f"Playing with mods:\n{''.join(installed_mods_list_pretty_for_display)}", False)
                    status_label.config(text=f"Playing with mods:\n{''.join(installed_mods_list_pretty_for_display)}")
                
                elif OS_TYPE == "Linux": # Playing on Linux
                    subprocess.Popen([Game_path, "-force-vulkan"]) # Run The Bibites without checking for mods.
                    with open(installed_mods, 'r') as file:
                        installed_mods_list = file.read().splitlines()
                        installed_mods_list_pretty_for_display = [] # List stores the installed mods without .TBM to make it prettier
                        for mod in installed_mods_list:
                            mod = mod.split('.')[0]
                            installed_mods_list_pretty_for_display.append(mod)
                    log(f"Playing with mods:\n{''.join(installed_mods_list_pretty_for_display)}", False)
                    status_label.config(text=f"Playing with mods:\n{''.join(installed_mods_list_pretty_for_display)}")

            # Catch and display error to the user
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error running the game", f"Unexpected error: {e}")    # Display message box with error
                
                log(f"Error running the game: {e}", True)
                status_label.config(text=f"Error running the game: {e}") # Display error on status label
            except Exception as e:
                messagebox.showerror("Error", f"Unexpected error: {e}") # Display message box with error
                
                log(f"Unexpected error: {e}", True)
                status_label.config(text=f"Unexpected error: {e}") # Display error on status label
    else:
        log(f"{Game_path} does not exist, you need to set a valid game path to be able to run the game", False)
        status_label.config(text=f"{Game_path} does not exist, you need to set a valid game path to be able to run the game")

def play_bepinex():
    # Only neccesary for OSes where any play button might modify it.
    ScriptingAssemblies = f'{Game_folder}/The Bibites_Data/ScriptingAssemblies.json'
    with open(ScriptingAssemblies, "r") as file:
        ScriptingAssembliesText = json.load(file) # Index of 'BibitesAssembly.dll' is 68

    if OS_TYPE == "Windows": # Playing on windows
        ScriptingAssembliesText['names'][68] = 'BibitesAssembly.dll' # Edit what dll is loaded to the normal unmodded one
        with open(ScriptingAssemblies, "w") as file:                 # Write the info
            json.dump(ScriptingAssembliesText, file)

        try:
            subprocess.Popen([Game_path]) # Run The Bibites without file dll replace mods.
            log("Playing with BepInEx mods", False)
            status_label.config(text="Playing with BepInEx mods")

        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error running the game", f"Unexpected error: {e}") # Display message box with error
            
            log(f"Error running the game: {e}", True)
            status_label.config(text=f"Error running the game: {e}") # Display error on status label
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {e}") # Display message box with error
            
            log(f"Unexpected error: {e}", True)
            status_label.config(text=f"Unexpected error: {e}") # Display error on status label
    
    elif OS_TYPE == "Linux": # Playing on Linux
        ScriptingAssembliesText['names'][68] = 'BibitesAssembly.dll' # Edit what dll is loaded to the normal unmodded one
        with open(ScriptingAssemblies, "w") as file:                 # Write the info
            json.dump(ScriptingAssembliesText, file)

        try:
            subprocess.Popen([f"{Game_folder}/run_bepinex.sh", Game_path, "-force-vulkan"]) # Run The Bibites without file dll replace mods.
            log("Playing with BepInEx mods", False)
            status_label.config(text="Playing with BepInEx mods")

        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error running the game", f"Unexpected error: {e}")        # Display message box with error
            
            log(f"Error running the game: {e}", True)
            status_label.config(text=f"Error running the game: {e}")                        # Display error on status label
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {e}")                         # Display message box with error
            
            log(f"Unexpected error: {e}", True)
            status_label.config(text=f"Unexpected error: {e}")                              # Display error on status label
    
    else:
        ScriptingAssembliesText['names'][68] = 'BibitesAssembly.dll' # Edit what dll is loaded to the normal unmodded one
        with open(ScriptingAssemblies, "w") as file:                 # Write the info
            json.dump(ScriptingAssembliesText, file)

        try:
            subprocess.Popen([Game_path]) # Run The Bibites without file dll replace mods.
            log("Playing with BepInEx mods", False)
            status_label.config(text="Playing with BepInEx mods")

        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error running the game", f"Unexpected error: {e}") # Display message box with error
            
            log(f"Error running the game: {e}", True)
            status_label.config(text=f"Error running the game: {e}") # Display error on status label
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {e}") # Display message box with error
            
            log(f"Unexpected error: {e}", True)
            status_label.config(text=f"Unexpected error: {e}") # Display error on status label

def log(message, save_to_file):
    timestamp = get_time()
    log_text.config(state='normal')
    log_text.insert('end', f"{timestamp} {message}" + '\n')
    log_text.see('end')  # Auto-scroll
    log_text.config(state='disabled')
    if save_to_file:
        # Save error to a log file
        with open(log_file, 'a') as file:
            file.write(f"\n{timestamp} {message}")

def swap_between_nightly_and_stable():
    global is_nightly
    is_nightly = not is_nightly
    if is_nightly:
        status_label.config(text=f'You are now on the nightly branch')
    else:
        status_label.config(text=f'You are now on the stable branch')
    
    save_settings()


# Get the script dir
script_dir = Path(__file__).parent.absolute()
images_folder = f'{script_dir}/Images' # Path to folder with images

# Setup UI links with UI.py
# Create window
window_widgets = create_window(images_folder, version_number, Discord_invite_link, OS_TYPE, handlers={
    'list_downloaded_mods': list_downloaded_mods,
    'download_mods_page': download_mods_page,
    'more_tools_page': more_tools_page,
    'credits_page': credits_page,
    'open_link':lambda e: open_link(Discord_invite_link)
})

window = window_widgets['window']
screen_width = window_widgets['screen_width']
screen_height = window_widgets['screen_height']
status_label = window_widgets['status_label']
display_downloaded_mods_button = window_widgets['display_downloaded_mods_button']
find_mods_button = window_widgets['find_mods_button']
more_tools_button = window_widgets['more_tools_button']
credits_button = window_widgets['credits_button']
Bibite_Research_Conglomerate_hyperlink = window_widgets['Bibite_Research_Conglomerate_hyperlink']

# Create the main page UI and store widgets
main_page_widgets = create_main_page_ui(window, handlers={
    'get_game_path': get_game_path,
    'get_game_version': get_game_version,
    'install_mods': install_mods,
    'play_vanilla': lambda: play_game('No'),
    "Play Modded": lambda: play_game('Yes'),
    'Play BepInEx': play_bepinex,
    'swap_between_nightly_and_stable': swap_between_nightly_and_stable,
    'reset_cache': reset_cache,
    'get_the_bibites': get_the_bibites,
    'download_new_tbmm_version': lambda: download_new_tbmm_version(OS_TYPE, is_nightly)
})

main_frame = main_page_widgets['frame']
game_path_label = main_page_widgets['game_path_label']
version_label = main_page_widgets['version_label']
downloaded_mods_listbox = main_page_widgets['downloaded_mods_listbox']
installed_mod_label = main_page_widgets['installed_mod_label']
log_text = main_page_widgets['log_text']
dowload_new_version_button = main_page_widgets['dowload_new_version_button']

# Create the download mods page UI and store widgets
downlod_mods_page_widgets = create_download_mods_page_ui(window, handlers={
    'download_mods': download_mods
})

downloadable_mods_frame = downlod_mods_page_widgets['frame']

# Create the credits page UI and store widgets
credits_page_widgets = create_credits_page_ui(window)

credits_frame = credits_page_widgets['frame']

more_tools_page_widgets = create_more_tools_page_ui(window, handlers={
    'open_link':lambda e: open_link("https://github.com/quaris628/EinsteinEditor/releases/latest"),
    'images_folder':images_folder
})

more_tools_frame = more_tools_page_widgets['frame']
Einstein_info_lable = more_tools_page_widgets['Einstein_info_lable']

def update_screen_size():
    global window_width, window_height
    window_width = window.winfo_width()
    window_height = window.winfo_height()

# Function moves the buttons on the sides when you scale the window always keping them on screen
def move_left_buttons(event):
    update_screen_size()

    button_height = display_downloaded_mods_button.winfo_reqheight() # Button height are so similar the same hight can be used for all buttons

    # Calculate padding based on window height, shrinking as height decreases
    min_padding = 0  # Minimum padding
    max_padding = 10  # Maximum padding
    height_threshold = 500  # Height threshold when padding starts shrinking
    padding = max(min_padding, min(max_padding, max_padding * (window_height / height_threshold)))  # Shrink padding as height decreases and cap at max_padding

    x = 10 # amount stuff is offset from the left edge of the window

    # Apply button positions
    display_downloaded_mods_button.place(x=x, y=window_height / 12.5)
    find_mods_button.place(x=x, y=display_downloaded_mods_button.winfo_y() + button_height + padding)
    more_tools_button.place(x=x, y=find_mods_button.winfo_y() + button_height + padding)
    
    credits_button.place(x=x, y=window_height - button_height - 15)

    # Position Bibite_Research_Conglomerate_hyperlink in bottom-right corner
    hyperlink_width = Bibite_Research_Conglomerate_hyperlink.winfo_reqwidth()
    hyperlink_height = Bibite_Research_Conglomerate_hyperlink.winfo_reqheight()
    Bibite_Research_Conglomerate_hyperlink.place(x=window_width - hyperlink_width - 20, y=window_height - hyperlink_height - 20)

    # Update wraplengt of text to make it look better on smaller windows
    Einstein_info_lable.configure(wraplength=min(1000, window_width - 375))

# Bind the function to move find_mods_button
window.bind('<Configure>', move_left_buttons)

# Set path for saving and loading
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    print("Running as compiled executable")
    executable_path = Path(sys.executable).parent
    print("Executable path " + executable_path)
    executable_path_temp = filedialog_askdirectory(title="Folder where you want generated files to be stored")
    print("Executable path temp " + executable_path_temp)
    if executable_path_temp != "":
        executable_path = executable_path_temp
    print("Executable path " + executable_path)

    downloading = executable_path/'Downloading'
    not_installed_mods = executable_path/'not_installed_mods'
    installed_mods = executable_path/'installed_mods.txt'
    downloaded_mods = executable_path/'downloaded_mods.txt'
    cache_file = executable_path/'cache.json'
    settings_file = executable_path/'settings.json'
    log_file = executable_path/'log.txt'
else:
    # Running as a standalone Python script
    downloading = f'{script_dir}/Downloading'
    not_installed_mods = f'{script_dir}/not_installed_mods'
    installed_mods = f'{script_dir}/installed_mods.txt'
    downloaded_mods = f'{script_dir}/downloaded_mods.txt'
    cache_file = f'{script_dir}/cache.json'
    settings_file = f'{script_dir}/settings.json'
    log_file = f'{script_dir}/log.txt'

# Make folders and files
if not os.path.isdir(downloading):
    os.makedirs(downloading)
if not os.path.isdir(not_installed_mods):
    os.makedirs(not_installed_mods)
if not os.path.isfile(downloaded_mods):
    open(downloaded_mods, 'a').close()
if not os.path.isfile(installed_mods):
    open(installed_mods, 'a').close()
if not os.path.isfile(settings_file):
    open(settings_file, 'a').close()
if not os.path.isfile(log_file):
    open(log_file, 'a').close()
else:
    try:
        with open(settings_file, 'r') as file:

            # Try to get all settings data from json file to a dictionary and the variables that uses settings
            error = False # Set to true if error loading any setting
            errormessage = '' # Append what setting is not loaded correctly
            settings = json.load(file)
            # Only if game path is there should we check the the folders
            if 'Game_path' in settings:
                Game_path = settings['Game_path']

                if 'Game_folder' in settings:
                    Game_folder = settings['Game_folder']
                else:
                    error = True
                    errormessage = errormessage + 'Game_folder '

                if 'bepinex_folder' in settings:
                    bepinex_folder = settings['bepinex_folder']
                else:
                    error = True
                    errormessage = errormessage + 'bepinex_folder '
            else:
                error = True
                errormessage = errormessage + 'Game_path '


            if 'Game_version' in settings:
                Game_version = settings['Game_version']

                if Game_version == "All":
                    version_label.config(text=f"You have selected {Game_version} game versions.", font=("Arial", 13))
                else:
                    version_label.config(text=f"You have selected game version {Game_version}.", font=("Arial", 13))
            else:
                error = True
                errormessage = errormessage + 'Game_version '
            
            if is_nightly:
                settings['is_nightly'] = True
            else:
                settings['is_nightly'] = False

            if 'is_nightly' in settings:
                is_nightly = settings['is_nightly']
            else:
                error = True
                errormessage = errormessage + 'is_nightly'

            
            if 'installed_mods_list' in settings:
                try:
                    installed_mods_list = settings['installed_mods_list']
                    installed_mods_list_pretty_for_display = [] # List stores the installed mods without .TBM to make it prettier
                    for mod in installed_mods_list:
                        mod = mod.split('.')[0]
                        installed_mods_list_pretty_for_display.append(mod)
                    installed_mod_label.config(text=f"Installed mod: {''.join(installed_mods_list_pretty_for_display)}", font=("Arial", 12))
                except Exception as e:
                    error = True
                    errormessage = errormessage + f'installed_mods_list {e}'
            else:
                installed_mod_label.config(text=f"Installed mod: I do not know what mod is installed", font=("Arial", 12))

            if error == True:
                log(f'Error loading settings: {errormessage}', False)
                status_label.config(text=f'Error loading settings: {errormessage}')
            else:
                log(f'Settings loaded successfully', False)
                status_label.config(text=f'Settings loaded successfully')
    
            if 'Game_path' in settings and os.path.isfile(Game_path):
                game_path_label.config(text=f'Game path: {Game_path}', font=("Arial", 9))
            else:
                game_path_label.config(text=f'Error game path can not be found', font=("Arial", 9))
                Game_path = ''
    except Exception as e:
        log(f'Can not read settings file', False)
        status_label.config(text=f'Can not read settings file')

# Load cache from json file
if os.path.isfile(cache_file) and os.stat(cache_file).st_size != 0: # I have no idea how to check if it is empty, because an empty json file is not 0 bytes
    with open(cache_file, 'r') as file:                             # I wrap in try except
        all_cache_data = {}
        try:
            all_cache_data = json.load(file) # Get all cache data from json file to variable
        except Exception as e:
            print(e)
        if "mod_names_cache" in all_cache_data: # check if mod_names_cache exists in cache
            mod_names_cache = all_cache_data["mod_names_cache"] # Load mod names from cache to cache variable

        if "cache_time" in all_cache_data: # check if cache_time exists in cache
            cache_time = all_cache_data["cache_time"] # Load cache time from cache to cache variable

        if "mod_content_cache" in all_cache_data: # check if mod_content_cache exists in cache
            mod_content_cache = all_cache_data["mod_content_cache"] # Load content of mod files into a cache variable

# Check for newer version
if is_nightly:
    newer_version = update_check(nightly_version, log, is_nightly)
else:
    newer_version = update_check(version_number, log, is_nightly)

if newer_version:
    dowload_new_version_button.grid(row=2, column=4, pady=130, sticky="n")

list_downloaded_mods()

# Runs the app
window.mainloop()