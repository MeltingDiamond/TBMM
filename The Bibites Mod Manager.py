import requests, platform, os, sys, base64, shutil, time, json, subprocess, re, zipfile, io
from tkinter import Label, Button, filedialog, Frame, Checkbutton, IntVar, Toplevel, messagebox, StringVar, OptionMenu
from pathlib import Path
from threading import Thread
from urllib.parse import urlparse, unquote

from UI import create_window, create_main_page_ui, create_download_mods_page_ui, create_credits_page_ui, create_more_tools_page_ui, create_game_version_page_ui, on_hover, hide_all_tooltips, on_checkbutton_hover, on_checkbutton_leave, CustomTooltip
from Networking import update_check, download_new_tbmm_version

# TODO Merge log() and write to log file into one function log()

# Gets userpath (Usually C:\Users\username)
USERPROFILE = os.environ['USERPROFILE']

# What os this is running on
os_map = {
    "Windows": "Windows",
    "Darwin": "Mac",
    "Linux": "Linux"
}
OS_TYPE = os_map.get(platform.system(), "Unknown")

# Version number of the next version to be released, not the bibites game version. Must be string or float
version_number = "0.06.1"

nightly_version = "__VERSION__" # Gets replaced during workflow build with latest version

# Should it check and download nightly version
if nightly_version ==  "__VERSION__":
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

# Gets the current time in correct time format to be placed in log.txt
def get_time():
    '''Gets the current time and date in a human readable format'''
    current_time = time.strftime('%x %X')
    return current_time

# Function to get the game path
def get_game_path():
    '''User input for getting the path to The Bibites game exe'''
    global Game_path, Game_folder
    if Game_folder:
        Temp_Game_path = filedialog.askopenfile(initialdir=Game_folder, filetypes=[("Executable files", "*.exe")]) # Store game path without overwriting existing game path
    else:
        Temp_Game_path = filedialog.askopenfile(filetypes=[("Executable files", "*.exe")]) # Store game path without overwriting existing game path
    if Temp_Game_path:
        Game_path = Temp_Game_path.name
        Game_folder = os.path.dirname(Game_path)
        settings['Game_path'] = Game_path
        settings['Game_folder'] = Game_folder
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

# Function to extract filename from url
def get_filename_from_response(url):
    '''Gets the filename from a url (the ending)
    :param url: any url'''
    parsed_url = urlparse(url)
    filename = parsed_url.path.split('/')[-1]
    decoded_filename = unquote(filename)  # Decode URL-encoded characters
    return decoded_filename

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
    file_path = filedialog.asksaveasfilename(
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

# Function to get mod install instructions for chosen mod from GitHub repository based on filename
def get_mod_url(mod_name):
    '''Get url from a .TBM file'''
    file_contents = get_file_contents(mod_name)
    if file_contents:
        
        lines = file_contents.split('\n') # Split the content into lines

        url_line = next((line for line in lines if line.startswith('url: ')), None) # Find the line containing the URL

        if url_line:
            url = url_line.replace('url:', '').strip() # Extract the URL from the line
            return url
    return None

# Function to get the version of the bibites the mod is made for
def get_mod_game_version(mod_name):
    '''Gets the version a mod is made for'''
    file_contents = get_file_contents(mod_name)
    if file_contents:
        
        lines = file_contents.split('\n') # Split the content into lines

        game_version_line = next((line for line in lines if line.startswith('game version: ')), None) # Find the line containing the URL

        if game_version_line:
            game_version = game_version_line.replace('game version: ', '').strip() # Extract the game version from the line
            return game_version
    return None

# Function to fetch filenames from GitHub or Dropbox with caching
def fetch_filenames():
    '''Get the file names of all the available mods'''
    global mod_names_cache, cache_time, mod_repo_urls

    # Check if cache is valid
    if mod_names_cache is None or time.time() - cache_time > cache_duration or mod_names_cache == []:
        # Check if user has intenett access
        if has_internet_connection():
            # Try each URL in the list until one succeeds
            for url in mod_repo_urls:
                website_name = get_website_name(url)
                print(f"Attempting to fetch filename from: {website_name}")

                if "github.com" in website_name:
                    mod_names_cache = fetch_from_github(url)
                elif "dropbox.com" in website_name:
                    mod_names_cache = fetch_from_dropbox(url)

                if mod_names_cache:  # Success, stop trying further URLs
                    cache_time = time.time()
                    save_cache_to_file()
                    return mod_names_cache

            # failed to fetch mod names from internett return empty list to avoid breaking code.
            print(" Did not download any mod names there was an error returns []")
            return []
        else: # No internett
            log("You have no internett")
            status_label.config(text="You have no internett")
            # Save error to a log file
            with open(log_file, 'a') as file:
                file.write(f"\n{get_time()} You have no internett")

            return mod_names_cache # Mod names cache should never be in a breaking state.
    
    # mod_names_cache was valid return it
    print("Returned mod_names_cache because it is valid")
    return mod_names_cache

def has_internet_connection(timeout=3):
    try:
        requests.get("https://www.google.com", timeout=timeout)
        return True
    except requests.RequestException:
        return False

# Function to fetch mod filenames from GitHub
def fetch_from_github(url):
    '''Get mod file names from github'''
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            contents = response.json()
            return [item["name"] for item in contents if item["name"].endswith(".TBM")]
        else:
            # Errors for Github access
            error_message = f"GitHub status code: {response.status_code}"
            if response.status_code == 404:
                error_message = f"GitHub status code: {response.status_code} can't access page"
            if response.status_code == 403:
                error_message = f"GitHub status code: {response.status_code} GitHub refused access to page"
            log(error_message)
            status_label.config(text=error_message)
            
            # Save error to a log file
            with open(log_file, 'a') as file:
                file.write(f"\n{get_time()} {error_message}")
    except Exception as e:
        print(f"Error accessing GitHub: {e}")
    return None

def fetch_from_dropbox(url):
    '''Get mod file names from dropbox'''
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            content = response.text
            # Regex to find all filenames ending with ".TBM"
            mod_names_from_dropbox = re.findall(r'([\w\-\.\d]+\.TBM)', content)
            mod_names_from_dropbox = list(set(mod_names))  # Remove duplicates
            
            if mod_names_from_dropbox:
                return mod_names_from_dropbox
            else:
                print("No .TBM files found in Dropbox data.")
        else:
            # Handle HTTP errors
            error_message = f"Dropbox status code: {response.status_code}"
            if response.status_code == 404:
                error_message += " - can't access page"
            if response.status_code == 403:
                error_message += " - Dropbox refused access to page"
            
            log(error_message)
            status_label.config(text=error_message)
            with open(log_file, 'a') as file:
                file.write(f"\n{get_time()} {error_message}")

    except Exception as e:
        print(f"Error accessing Dropbox: {e}")

    return None

# Function to fetch file contents from GitHub repository
def get_file_contents_from_github(mod_name):
    '''Get the content for a mod from github'''
    global mod_content_cache#, four_zero_three_cache
    owner = "MeltingDiamond"
    repo = "TBMM-Mods"
    path = f"Mods/{mod_name}"

    if path in mod_content_cache and time.time() - mod_content_cache[path]['time'] < cache_duration:
        return mod_content_cache[path]['content']

    api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    response = requests.get(api_url)
    if response.status_code == 200:
        content = response.json().get('content')
        decoded_content = base64.b64decode(content).decode('utf-8')
        
        # Cache the content and save the cache
        mod_content_cache[path] = {'content': decoded_content, 'time': time.time()}
        
        if decoded_content:
            return True

    return None

def get_file_contents_from_dropbox(mod_name):
    '''Get the content for a mod from dropbox'''
    global mod_content_cache
    path = f"Mods/{mod_name}"

    try:
        # Download the ZIP file from Dropbox
        response = requests.get(mod_repo_urls[0], timeout=10)
        if response.status_code != 200:
            print(f"Error downloading from Dropbox: {response.status_code}")
            return None
        
        # Open the ZIP file in memory
        zip_file = zipfile.ZipFile(io.BytesIO(response.content))

        # Look for the requested .TBM file
        for file in zip_file.namelist():
            print(file)
            if file.endswith(f"/{mod_name}") or file == mod_name:
                with zip_file.open(file) as f:
                    content = f.read().decode("utf-8")  # Read & decode content
                    
                    # Cache the content
                    mod_content_cache[path] = {'content': content, 'time': time.time()}
                    
                    return content  # Return the file's text content
        
        print(f"File '{mod_name}' not found in Dropbox ZIP")
        return None

    except Exception as e:
        print(f"Error processing Dropbox ZIP: {e}")
        return None

def get_website_name(url):
    '''Gets the name of a website from a url'''
    parsed_url = urlparse(url)
    return parsed_url.netloc

# Function to fetch file contents
def get_file_contents(mod_name):
    '''Gets file content from cache, if that isn't valid either github or dropbox using the name of the mod'''
    global cache_time, mod_repo_urls

    #owner = "MeltingDiamond"
    #repo = "TBMM-Mods"
    path = f"Mods/{mod_name}"

    # Check cache first
    if path in mod_content_cache and time.time() - mod_content_cache[path]['time'] < cache_duration:
        return mod_content_cache[path]['content']
    
    if has_internet_connection():
        mod_cache = {}
        for url in mod_repo_urls:
            website_name = get_website_name(url)
            log(f"Attempting to fetch content from: {website_name}")

            if "github.com" in website_name:
                mod_cache = get_file_contents_from_github(mod_name)
            elif "dropbox.com" in website_name:
                mod_cache = get_file_contents_from_dropbox(mod_name)

            if mod_cache:
                cache_time = time.time()
                save_cache_to_file()
                return mod_content_cache[path]['content']
    else:
        return None

def get_bibites_to_download(mod_name):
    file_contents = get_file_contents(mod_name)
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
    file_contents = get_file_contents(mod_name)
    if file_contents:
        lines = file_contents.split('\n')
        install_line = next((line for line in lines if line.startswith('install: ')), None)
        if install_line:
            instruction = install_line.replace('install:', '').strip()
            return instruction


def get_mod_description(mod_name):
    '''Get the description of a mod using the name'''
    file_contents = get_file_contents(mod_name)
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

def download_file(url, location): # Downloads the file at url and places it in location
    '''
    Downloads the file at url and places it in location.
    :param url: Web url to file to download
    :param location: Location the file is downloaded to'''
    
    filename = get_filename_from_response(url) # The name of the file being downloaded
    location_folder = get_filename_from_response(location) # The folder where the file will end up
    filepath = f"{location}/{filename}" # Where the file will end up after this function finishes
    
    if location_folder.endswith(".TBM"):
        mod_name = location_folder
    else:
        mod_name = filename

    downloading_folder = f'{downloading}/{location_folder}'
    downloading_path = f'{downloading_folder}/{filename}' # Where the file will be downloaded to temporarily before beeing moved to the correct location
    website = get_website_name(url)

    error_downloading_file = False # False unless there are at least 1 error downloading files
    mod_exists = False

    try: # Checks if it can connect with internet
        response = requests.get(url, stream=True)
        total = int(response.headers.get('content-length', 0))
    except requests.exceptions.MissingSchema as e:
        # Save error to a log file
        with open(log_file, 'a') as file:
            file.write(f"\n{get_time()} {e}")

        log(e)
        status_label.config(text=e)
    except Exception as e:
        # Save error to a log file
        with open(log_file, 'a') as file:
            file.write(f"\n{get_time()} Can not connect to {website}, error: {e}")
        log(f"Can not connect to {website} to get mod data")
        status_label.config(text=f"Can not connect to {website} to get mod data")
        return

    # Check if downloading folder exists if it doesn't make it
    if not os.path.isfile(downloading_path) and not os.path.isdir(downloading_folder):
        os.makedirs(os.path.dirname(downloading_path), exist_ok=True)
    elif not os.path.isdir(downloading_path):
        open(downloading_path, 'a').close()

    with open(downloading_path, 'wb') as file:
        downloaded = 0
        for data in response.iter_content(chunk_size=1024):
            size = file.write(data)
            downloaded += size
            percent_done = int(downloaded / total * 100)
            log(f"Downloading... {percent_done}%")
            status_label.config(text=f"Downloading... {percent_done}%")

    # Check if downloaded size matches the total size
    if downloaded >= total:
        try:
            if not os.path.exists(location):
                    os.makedirs(location)# folder does not exist make it
            if not os.path.isfile(filepath):
                shutil.move(downloading_path, filepath) # Mod doesnt exist move the mod
                safe_unlink(downloading_folder) # Remove mod folder in downloading folder since it isnt needed

            elif os.path.isfile(filepath):
                with open(downloading_path, 'rb') as new_file:
                    new_content = new_file.read()
                with open(filepath, 'rb') as existing_file:
                    existing_content = existing_file.read()
                if new_content == existing_content: # Mod exists do nothing
                    mod_exists = True
                    log(f"{filename} already downloaded")
                    status_label.config(text=f"{filename} already downloaded")

        except Exception as e:
            error_downloading_file = True

            if os.path.exists(location):
                if os.listdir(location) == 0 and mod_exists == False:
                    os.remove(location) # Folder exixts, is empty and the mod doesn't exist, remove it

            # Save error to a log file
            with open(log_file, 'a') as file:
                file.write(f"\n{get_time()} Error downloading {mod_name}: {e}")

            log(f"Error download {mod_name}: {e}")
            status_label.config(text=f"Error download {mod_name}: {e}")
        
        if error_downloading_file == False and mod_exists == False:
            log(f"Downloading {mod_name} complete!")
            status_label.config(text=f"Downloading {mod_name} complete!")

# Function to start the download process
def start_download(url, location):
    '''Starts downloading a file from a url in a thread'''
    log("Downloading...")
    status_label.config(text="Downloading...")
    download_thread = Thread(target=download_file, args=(url,location))
    download_thread.start()

def download_mods():
    '''Download selected mods from mod_vars'''
    global mod_folder_name, mod_names, downloaded_mods_list, mod_vars

    # Get a list of downloaded mods
    if os.path.isfile(downloaded_mods):
        try:
            with open(downloaded_mods, "r") as file:
                downloaded_mods_list = [line.strip() for line in file.readlines()] # List of mods that are downloaded
        except:
            open(downloaded_mods, 'a').close() # file is none existent or broken. Recreate it


    urls = []
    if len(mod_names) >= len(mod_vars): # Check if mod_vars is equal or less than mod_names to avoid trying to get a mod that is outside the mod_names list
        mod_names[:] = fetch_filenames()
    
    # Loop through all mod Checkbuttons to check which ones are selected, so the selected ones can be downloaded if not already downloaded.
    for i, var in enumerate(mod_vars):
        urls.append(None)
        if var.get() == 1: # The mod is selected and will be downloaded
            mod_folder_name = mod_names[i]
            if mod_folder_name in downloaded_mods_list: # Check if mod is downloaded
                log(f"{mod_names[i].split('.')[0]} already downloaded")
                status_label.config(text=f"{mod_names[i].split('.')[0]} already downloaded")
            else: # Mod is not downloaded
                url = get_mod_url(mod_names[i])
                urls[i] = url
                if urls[i]:
                    install_type = get_mod_install_description(mod_names[i])
                    download_location = f"{not_installed_mods}/{install_type}/{mod_folder_name}"
                    # Download the mod
                    start_download(urls[i], download_location)
                    
                    # Add mod name to the list
                    downloaded_mods_list.append(mod_folder_name)
                else:
                    log(f"URL for {mod_names[i]} not found.")
                    status_label.config(text=f"URL for {mod_names[i]} not found.")
    with open(downloaded_mods, "w") as downloaded_mods_file:
        downloaded_mods_file.write('\n'.join(downloaded_mods_list))

# Only works with replace mods currently. So if a BepInEx mod is installed as well this wont work correctly
def install_mod_by_replace_dll(mod_name, not_installed_mod_folder, not_installed_mod_path, installed_mods_list): # Used when replace install instruction is needed
    try:
        # If mod isnt installed and no other mod is installed
        if f'{not_installed_mod_path}' not in os.listdir(not_installed_mod_folder) and len(installed_mods_list) == 0 and not os.path.exists(f'{Game_folder}/The Bibites_Data/Managed/BibitesAssembly.dll.TBM'):
            log_message = f"Installing {mod_name}"
            log(log_message)
            status_label.config(text=log_message)
            shutil.move(f'{not_installed_mod_path}', f'{Game_folder}/The Bibites_Data/Managed') # Move the mod
            installed_mods_list = mod_name
            print(installed_mods_list)
            with open(installed_mods, 'w') as file: # Write the installed_mod_list to keep it after TBMM closes
                file.write(installed_mods_list)

            log_message = f"Installed {mod_name}"
            log(log_message)
            status_label.config(text=log_message)
        
        # If any other mod is installed replace the curent one
        else:
            log_message = ""
            for mod in installed_mods_list:
                log_message = f"{log_message}{mod} "
            
            log_message = f"Replacing {log_message}with {mod_name}"
            log(log_message)
            status_label.config(text=log_message)

            # Check if mod you are trying to install is installed if it isn't install it
            if mod_name not in installed_mods_list:
                # move other mods back to uninstalled location if there is an installed mod in installed_mods.txt
                for mod in installed_mods_list:
                    installed_mod_not_installed_mod_folder = f'{not_installed_mods}/replace/{mod}'
                    shutil.move(f'{Game_folder}/The Bibites_Data/Managed/BibitesAssembly.dll.TBM', installed_mod_not_installed_mod_folder) # Move the mod
                
                # if there is a mod in the location where there should be none unlink it
                if os.path.exists(f'{Game_folder}/The Bibites_Data/Managed/BibitesAssembly.dll.TBM'):
                    os.unlink(f'{Game_folder}/The Bibites_Data/Managed/BibitesAssembly.dll.TBM')

                # Install the mod
                shutil.move(f'{not_installed_mod_path}', f'{Game_folder}/The Bibites_Data/Managed') # Move the mod

                # Add the installed mod to the installed_mods_list
                installed_mods_list = [mod_name]
                with open(installed_mods, 'w') as file: # Write the installed_mod_list to keep it after TBMM closes
                    file.write(mod_name)
                
                # Display that mod is installed
                log_message = f"Installd {mod_name}"
                log(log_message)
                status_label.config(text=log_message)

                installed_mods_list_pretty_for_display = [] # List stores the installed mods without .TBM to make it prettier
                for mod in installed_mods_list:
                    mod = mod.split('.')[0]
                    installed_mods_list_pretty_for_display.append(mod)
                installed_mod_label.config(text=f"Installed mod: {''.join(installed_mods_list_pretty_for_display)}", font=("Arial", 12))
                save_settings()
    except Exception as e:
        messagebox.showerror("Error", f"Unexpected error: {e}")
        
        # Save error to a log file
        with open(log_file, 'a') as file:
            file.write(f"\n{get_time()} Unexpected error: {e}")
        log(f"Unexpected error: {e}")

def download_bibites(bibites_to_download):
    for bibite in bibites_to_download:
        filename = get_filename_from_response(bibite) # Get filename to determin if it is .bb8 or .bb8template
        log(f"Downloading bibite {filename}")
        if OS_TYPE == "Windows":
            if filename.endswith(".bb8"):
                location = f'{USERPROFILE}/AppData/LocalLow/The Bibites/The Bibites/Bibites'
            elif filename.endswith(".bb8template"):
                location = f'{USERPROFILE}/AppData/LocalLow/The Bibites/The Bibites/Bibites/Templates'
        start_download(bibite, location) # Downloads the bibite to the specified location


def install_mods(): # Install a mod so you can play modded
    '''Installs the selected downloaded mods'''

    if os.path.exists(Game_path) == False:
        log(f"Game path is {Game_path}, you need to set a game path to be able to install mods correctly")
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
            url = get_mod_url(mod_name)
            if url:
                start_download(url, not_installed_mod_folder)
        
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
                log(f"Install instruction \"replace+\" is not yet added")
                status_label.config(text=f"Install instruction \"replace+\" is not yet added")

            elif install_instruction == "BepInEx":
                log(f"Install instruction \"BepInEx\" will be implemented after \"replace\" is implemented")
                status_label.config(text=f"Install instruction \"BepInEx\" will be implemented after \"replace\" is implemented")
            
            elif install_instruction == "BepInEx+":
                log(f"Install instruction \"BepInEx+\" is not yet added")
                status_label.config(text=f"Install instruction \"BepInEx+\" is not yet added")

            else: # TBMM can't install the mod yet
                log(f"{mod_name} can't be installed because TBMM does not have instructions implemented for: {install_instruction}")
                status_label.config(text=f"{mod_name} can't be installed because TBMM does not have instructions implemented for: {install_instruction}")

        # The mod you are trying to install ia already installed
        else:
            log(f"{mod_name} is aleady installed")
            status_label.config(text=f"{mod_name} is aleady installed") # Display that mod is already installed
            installed_mods_list_pretty_for_display = [] # List stores the installed mods without .TBM to make it prettier
            for mod in installed_mods_list:
                mod = mod.split('.')[0]
                installed_mods_list_pretty_for_display.append(mod)
            installed_mod_label.config(text=f"Installed mod: {''.join(installed_mods_list_pretty_for_display)}", font=("Arial", 12))

            settings['installed_mods_list'] = installed_mods_list
            save_settings()

# Function to save cache to a file
def save_cache_to_file():
    all_cache_data = {"mod_names_cache" : mod_names_cache,"cache_time" : cache_time, "mod_content_cache" : mod_content_cache}
    with open(cache_file, 'w') as file:
        json.dump(all_cache_data, file)
    log("Saved cache to file.")
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
            content = get_file_contents(mod_name_only)  # Using the name to check if mod exists

            if content:  # If mod content can be fetched, keep it
                cleaned_mod_content_cache[mod_name] = mod_data
            else:
                # Save error to a log file
                with open(log_file, 'a') as file:
                    file.write(f"\n{get_time()} Invalid mod content, removing: {mod_name}")
                log(f"Invalid mod content, removing: {mod_name}")
                status_label.config(text=f"Invalid mod content, removing: {mod_name}")
        else:
            # Save error to a log file
            with open(log_file, 'a') as file:
                file.write(f"\n{get_time()} Mod not in mod_names_cache, removing: {mod_name}")
            log(f"Mod not in mod_names_cache, removing: {mod_name}")
            status_label.config(text=f"Mod not in mod_names_cache, removing: {mod_name}")

    # Update mod_content_cache with only valid mods that are also in mod_names_cache
    mod_content_cache = cleaned_mod_content_cache
    cache_time = time.time()  # Reset cache time to current time

    # Save the cleaned cache to file
    save_cache_to_file()
    log("Cache reset, and invalid mods removed.")
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
        mod_names = fetch_filenames()  # Use cached data
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
            ScriptingAssembliesText['names'][68] = 'BibitesAssembly.dll' # Edit what dll is loaded to the normal unmodded one
            with open(ScriptingAssemblies, "w") as file:                 # Write the info
                json.dump(ScriptingAssembliesText, file)

            try:
                subprocess.Popen([Game_path]) # Run The Bibites without mods.
                log("Playing without mods")
                status_label.config(text="Playing without mods")

            # Catch and display error to the user
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error running the game", f"Unexpected error: {e}")    # Display message box with error
                
                # Save error to a log file
                with open(log_file, 'a') as file:
                    file.write(f"\n{get_time()} Error running the game: {e}")
                
                log(f"Error running the game: {e}")
                status_label.config(text=f"Error running the game: {e}") # Display error on status label
            except Exception as e:
                messagebox.showerror("Error", f"Unexpected error: {e}") # Display message box with error
                
                # Save error to a log file
                with open(log_file, 'a') as file:
                    file.write(f"\n{get_time()} Unexpected error: {e}")
                
                log(f"Unexpected error: {e}")
                status_label.config(text=f"Unexpected error: {e}") # Display error on status label

        if Modded == ('Yes'):
            if os.path.isfile(f'{Game_folder}/The Bibites_Data/Managed/BibitesAssembly.dll.TBM'):
                ScriptingAssembliesText['names'][68] = 'BibitesAssembly.dll.TBM' # Edit what dll is loaded to the modded one
                with open(ScriptingAssemblies, "w") as file:                     # Write the info
                    json.dump(ScriptingAssembliesText, file)
                log(f"You have installed a replace mod assuming you want to use that")
                status_label.config(text=f"You have installed a replace mod assuming you want to use that")
            else:
                log(f"You haven't installed a replace mod assuming you have intalled BepInEx mods")
                status_label.config(text=f"You haven't installed a replace mod assuming you have intalled BepInEx mods")

            try:
                subprocess.Popen([Game_path]) # Run The Bibites without checking for mods.
                with open(installed_mods, 'r') as file:
                    installed_mods_list = file.read().splitlines()
                    installed_mods_list_pretty_for_display = [] # List stores the installed mods without .TBM to make it prettier
                    for mod in installed_mods_list:
                        mod = mod.split('.')[0]
                        installed_mods_list_pretty_for_display.append(mod)
                log(f"Playing with mods:\n{''.join(installed_mods_list_pretty_for_display)}")
                status_label.config(text=f"Playing with mods:\n{''.join(installed_mods_list_pretty_for_display)}")

            # Catch and display error to the user
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error running the game", f"Unexpected error: {e}")    # Display message box with error
                
                # Save error to a log file
                with open(log_file, 'a') as file:
                    file.write(f"\n{get_time()} Error running the game: {e}")
                
                log(f"Error running the game: {e}")
                status_label.config(text=f"Error running the game: {e}") # Display error on status label
            except Exception as e:
                messagebox.showerror("Error", f"Unexpected error: {e}") # Display message box with error
                
                # Save error to a log file
                with open(log_file, 'a') as file:
                    file.write(f"\n{get_time()} Unexpected error: {e}")
                
                log(f"Unexpected error: {e}")
                status_label.config(text=f"Unexpected error: {e}") # Display error on status label
    else:
        log(f"{Game_path} does not exist, you need to set a valid game path to be able to run the game")
        status_label.config(text=f"{Game_path} does not exist, you need to set a valid game path to be able to run the game")

def log(message):
    timestamp = get_time()
    log_text.config(state='normal')
    log_text.insert('end', f"{timestamp} {message}" + '\n')
    log_text.see('end')  # Auto-scroll
    log_text.config(state='disabled')

# Get the script dir
script_dir = Path(__file__).parent.absolute()
images_folder = f'{script_dir}/Images' # Path to folder with images

# Setup UI links with UI.py
# Create window
window_widgets = create_window(images_folder, version_number, Discord_invite_link, handlers={
    'list_downloaded_mods': list_downloaded_mods,
    'download_mods_page': download_mods_page,
    'more_tools_page': more_tools_page,
    'credits_page': credits_page
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
    'reset_cache': reset_cache,
    'get_the_bibites': get_the_bibites,
    'download_new_tbmm_version': lambda: download_new_tbmm_version(OS_TYPE, False)
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

more_tools_page_widgets = create_more_tools_page_ui(window, images_folder)

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
    executable_path = Path(sys.executable).parent
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
            if 'Game_path' in settings:
                Game_path = settings['Game_path']
            else:
                error = True
                errormessage = errormessage + 'Game_path '

            if 'Game_folder' in settings:
                Game_folder = settings['Game_folder']
            else:
                error = True
                errormessage = errormessage + 'Game_folder '

            if 'Game_version' in settings:
                Game_version = settings['Game_version']

                if Game_version == "All":
                    version_label.config(text=f"You have selected {Game_version} game versions.", font=("Arial", 13))
                else:
                    version_label.config(text=f"You have selected game version {Game_version}.", font=("Arial", 13))
            else:
                error = True
                errormessage = errormessage + 'Game_version '
            
            if 'is_nightly' in settings:
                nightly_version = settings['is_nightly']
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
                log(f'Error loading settings: {errormessage}')
                status_label.config(text=f'Error loading settings: {errormessage}')
            else:
                log(f'Settings loaded successfully')
                status_label.config(text=f'Settings loaded successfully')
    
            if 'Game_path' in settings and os.path.isfile(Game_path):
                game_path_label.config(text=f'Game path: {Game_path}', font=("Arial", 9))
            else:
                game_path_label.config(text=f'Error game path can not be found', font=("Arial", 9))
                Game_path = ''
    except Exception as e:
        log(f'Can not read settings file')
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
    dowload_new_version_button.grid(row=2, column=4, pady=80, sticky="n")

list_downloaded_mods()

# Runs the app
window.mainloop()