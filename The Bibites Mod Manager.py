import requests, os, sys, base64, shutil, time, json, subprocess, webbrowser, re
from tkinter import Tk, Label, Button, filedialog, Frame, Checkbutton, IntVar, Listbox, Scrollbar, Toplevel, messagebox, StringVar, OptionMenu, PhotoImage
from pathlib import Path
from threading import Thread
from urllib.parse import urlparse, unquote

# Version number of the next version to be released, not the bibites game version. Must be string or float
version_number = "0.06"

# What os this is running on
os_type = "Windows" # "Windows", "Mac" or "Linux"

# List that holds versions of The Bibites that TBMM has mods for
list_of_versions = ["0.5.0", "0.5.1"]
list_of_versions_link_windows = {"0.5.0" : "https://www.dropbox.com/scl/fi/c1kypn1j4f67h1ezyyehb/the-bibites-0.5.0-windows-64x.zip?rlkey=zojdpcokxelsnjn7pmdgpbi50&st=0p7ria1e&dl=1","0.5.1" : "https://www.dropbox.com/scl/fi/zapwgdrfsxokopijrpp5d/The-Bibites-0.5.1-Windows-64x.zip?rlkey=2hu5kba5uddo2rwtleegr2sv8&st=i373zbys&dl=1", "0.6.0.1" : "https://www.dropbox.com/scl/fi/boh31txr00v77i95hbbai/The-Bibites-0.6.0.1-Windows-64x.zip?rlkey=hkqwkpjy7e5r32t1lau316d9e&st=k5ef2fja&dl=1"} # Direct links to the download windows version
list_of_versions_link_mac = {"0.5.0" : "None","0.5.1" : "https://www.dropbox.com/scl/fi/s490adgdpdb729mdwp7hm/The-Bibites-0.5.1-Mac-Universal.zip?rlkey=03qab761ta5yi7w3d4iqrxln0&st=eoze7gc8&dl=1", "0.6.0.1" : "https://www.dropbox.com/scl/fi/igxy7fq16yl7ieqjh994v/The-Bibites-0.6.0.1-Mac-Universal.zip?rlkey=wfquramlnyf77af2znrbljwbh&st=urrvwiue&dl=1"} # Direct links to the download mac version
list_of_versions_link_linux = {"0.5.0" : "None","0.5.1" : "https://www.dropbox.com/scl/fi/pukgn05ie6gs08qi1havf/The-Bibites-0.5.1-Linux.zip?rlkey=ghgqnrg2yygsi6xo1bl8nlsmw&st=fgzaru3d&dl=1", "0.6.0.1" : "https://www.dropbox.com/scl/fi/vflvk4x6bf2thohddftqj/The-Bibites-0.6.0.1-Linux.zip?rlkey=ubn7srnx2nspfwb5wy95r1a5j&st=1bjvg715&dl=1"} # Direct links to the download linux version

# Store every url that can be used to download TBM mod data from
# The list should be ordered from most up to date and most uptime to least up to date and least uptime.
add_first = "https://api.github.com/repos/MeltingDiamond/TBMM-Mods/contents/Mods" # This is the original keep it first unless I say otherwise - MeltingDiamond
mod_repo_urls = [add_first, "https://www.dropbox.com/scl/fo/fpcl07m7573flcbho85wk/ABr3cK3iIgFC7-QZe_mPpuY?rlkey=8wb5869lkawgcxpwwu0petu3t&st=0tyabw62&dl=1"]

# Discord invite link
Discord_invite_link = "https://discord.gg/ZNPCZPDhCS"

# Gets userpath (Usually C:\Users\username)
USERPROFILE = os.environ['USERPROFILE']

# Checkbutton variables
mod_vars = []

# List where mod names are stored to be referenced later
mod_folder_name = ''

# Used to display what page the user is on
page = ''

# Cache variables
mod_content_cache = {}
mod_names_cache = []
cache_time = 0.0
cache_duration = 86400  # Cache duration in seconds (24 hours)

# List to store mod names globaly
downloaded_mods_list = []
mod_names = []
installed_mods_list = []

# Variable to hold game path and folder
Game_path = ''
Game_folder = ''

# Variable to hold game version
Game_version = ''

# Settings dictionary
settings = {}

# Gets the current time in correct time format to be placed in log.txt
def get_time():
    current_time = time.strftime('%x %X')
    return current_time

# Function to get the game path
def get_game_path():
    global Game_path, Game_folder
    Game_path = filedialog.askopenfile(filetypes=[("Executable files", "*.exe")]).name
    Game_folder = os.path.dirname(Game_path)
    game_path_label.config(text=f'Game path: {Game_path}', font=("Arial", 12))
    settings['Game_path'] = Game_path
    settings['Game_folder'] = Game_folder
    save_settings()

def get_game_version():
    # Calculate the width and height for the window
    width_height = f"{int(screen_width / 4)}x{int(screen_height / 3)}"

    # Create a new window for selecting the game version
    game_version_window = Toplevel(window)
    game_version_window.title("Choose Game Version")
    game_version_window.geometry(width_height)
    window.minsize(480, 360)
    game_version_window.resizable(False, False)

    # Create a frame to hold the game version options
    game_version_frame = Frame(game_version_window)
    game_version_frame.pack(pady=20)

    # Label for instructions
    label = Label(game_version_frame, text="Please choose the game version:", font=("Arial", 14))
    label.pack(pady=10)
    
    # List of game versions
    list_of_mod_versions = ["All"] + list_of_versions

    # Create a StringVar to store the selected version
    if Game_version in list_of_mod_versions:
        selected_version = StringVar(value=Game_version)  # Show the version the user selected last time
    else:
        selected_version = StringVar(value=list_of_mod_versions[0])  # Default to the first version in the list

    # Create an OptionMenu (dropdown) for the game versions
    version_dropdown = OptionMenu(game_version_frame, selected_version, *list_of_mod_versions)
    version_dropdown.pack(pady=10)

    label = Label(game_version_frame, text="If you can't find your version,\nit is because there are no mods for it, choose all to show all mods", font=("Arial", 11))
    label.pack(pady=10)

    # Function to save the selected version and close the window
    def save_version():
        global Game_version  # Declare game_version as a global variable to store the selected version
        print(Game_version)
        Game_version = selected_version.get()  # Store the selected version in the global variable
        print(Game_version)
        if Game_version == "All":
            version_label.config(text=f"You have selected {Game_version} game versions.", font=("Arial", 13))
        else:
            version_label.config(text=f"You have selected game version {Game_version}.", font=("Arial", 13))
        settings['Game_version'] = Game_version
        save_settings()
        game_version_window.destroy()  # Close the window

    # Add a button to confirm the selection
    confirm_button = Button(game_version_frame, text="Confirm", command=save_version)
    confirm_button.pack(pady=10)

    # Wait for the user to select a version and confirm
    game_version_window.grab_set()  # Prevent interaction with the main window until this one is closed
    game_version_window.mainloop()  # Start the window's event loop

def get_the_bibites():
    # Calculate the width and height for the window
    width_height = f"{int(screen_width / 3.5)}x{int(screen_height / 2.5)}"

    # Create a new window for selecting the game version
    download_the_bibites_window = Toplevel(window)
    download_the_bibites_window.title("Download The Bibites")
    download_the_bibites_window.geometry(width_height)
    window.minsize(548, 432)
    download_the_bibites_window.resizable(False, False)

    # Create a frame to hold the game version options
    download_the_bibites_frame = Frame(download_the_bibites_window)
    download_the_bibites_frame.pack(pady=20)

    # Label for instructions
    label = Label(download_the_bibites_frame, text=f"Please choose the version of The Bibites {os_type} to download:", font=("Arial", 13, "bold"))
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

# Download a specific version of the bibites which TBMM has mods for
def download_the_bibites_of_x_version(version):
    # Retrieve the download link for the selected version
    if os_type == "Windows":
        list_of_versions_link = list_of_versions_link_windows
    elif os_type == "Mac":
        list_of_versions_link = list_of_versions_link_mac
    elif os_type == "Linux":
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

def check_for_local_mods():
    global installed_mods_list, downloaded_mods_list
    if installed_mods_list != []:
        with open(installed_mods, "r") as file:
            installed_mods_list = [line.strip() for line in file.readlines()]
    
    if os.path.isfile(downloaded_mods) and os.stat(downloaded_mods).st_size != 0:
        with open(downloaded_mods, "r") as file:
            downloaded_mods_list = [line.strip() for line in file.readlines()]

    for mod_folder in os.listdir(not_installed_mods):
        if len(os.listdir(f'{not_installed_mods}/{mod_folder}')) != 0:
            if mod_folder not in downloaded_mods_list:
                downloaded_mods_list.append(mod_folder)
        else:
            if mod_folder not in installed_mods_list:
                safe_unlink(f'{not_installed_mods}/{mod_folder}')
    
    # remove invalid mods
    downloaded_mods_list = [mod for mod in downloaded_mods_list if mod in mod_names_cache]
    with open(downloaded_mods, "w") as file:
        file.write('\n'.join(downloaded_mods_list))
    
    status_label.config(text=f"Checked for local mods and saved them if any where found")

def download_file(url, download_file_function_mod_folder_name, is_bibite, download_directly, path = None): # Slowly trying to make this work for every type of download (bibite, mod, reskin, other files a mod needs)
    global downloaded_mods_list

    error_downloading_file = False # Has there been an error
    mod_exists = False # Is the mod already installed
    filename = get_filename_from_response(url)

    # Config paths
    if is_bibite:
        if filename.endswith(".bb8"):
            downloading_folder = f'{USERPROFILE}\AppData\LocalLow\The Bibites\The Bibites\Bibites'
            downloading_path = f'{downloading_folder}/{filename}'
        elif filename.endswith(".bb8template"):
            downloading_folder = f'{USERPROFILE}\AppData\LocalLow\The Bibites\The Bibites\Bibites\Templates'
            downloading_path = f'{downloading_folder}/{filename}'

    else:
        downloading_path = f'{downloading}/{download_file_function_mod_folder_name}/{filename}' # The path to the file that is downloaded
        downloading_folder = f'{downloading}/{download_file_function_mod_folder_name}' # The folder where the file you download is in
        destination_folder = f'{path}' # Folder where the mod will be moved to after downloading
        destination_path = f'{path}/{filename}' # Path to the new location for the dll

    try: # Checks if it can connect with internet
        response = requests.get(url, stream=True)
        total = int(response.headers.get('content-length', 0))
    except requests.exceptions.MissingSchema as e:
        # Save error to a log file
        with open(log_file, 'a') as file:
            file.write(f"\n{get_time()} {e}")

        status_label.config(text=e)
    except Exception as e:
        # Save error to a log file
        with open(log_file, 'a') as file:
            file.write(f"\n{get_time()} Can not connect to Github, error: {e}")
        status_label.config(text=f"Can not connect to Github to get mod data")
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
            status_label.config(text=f"Downloading... {percent_done}%")

    # Check if downloaded size matches the total size
    if downloaded >= total:
        try:
            # New download code
            with open(downloading_path, 'rb') as new_file:
                new_content = new_file.read()
            # Check if mod is downloaded
            if download_file_function_mod_folder_name not in downloaded_mods_list and is_bibite == False:
                # Loop throug all the mods downloaded and check if exact mod and version is installed
                for mod_folder in os.listdir(not_installed_mods): 
                    if len(os.listdir(f'{not_installed_mods}/{mod_folder}')) != 0:
                        for mod in os.listdir(f'{not_installed_mods}/{mod_folder}'):  
                            if os.path.isfile(f'{not_installed_mods}/{mod_folder}/{mod}'):
                                with open(f'{not_installed_mods}/{mod_folder}/{mod}', 'rb') as existing_file:
                                    existing_content = existing_file.read()
                                if new_content == existing_content: # Mod exists do nothing
                                    mod_exists = True
                                    break

                if mod_exists == False and download_directly == False: # If mod exists and should be moved install it else discard downloaded mod.
                    # Check if mod exists
                    if not os.path.isfile(destination_path):
                        if not os.path.exists(destination_folder):
                            os.makedirs(destination_folder)# folder does not exist make it
                        shutil.move(downloading_path, destination_path) # Mod doesnt exist move the mod
                        safe_unlink(downloading_folder) # Remove mod folder in downloading folder since it isnt needed
                    else:
                        os.replace(downloading_path, destination_path) # Mod exists replace the mod
                        safe_unlink(downloading_folder) # Remove mod folder in downloading folder since it isnt needed
                else:
                    safe_unlink(downloading_folder) # Delete folder and mod in downloading folder

        except Exception as e:
            error_downloading_file = True

            # Save error to a log file
            with open(log_file, 'a') as file:
                file.write(f"\n{get_time()} Error downloading mod: {e}")

            status_label.config(text=f"Error download mod: {e}", font=("Arial", 12))
        
        if os.path.exists(downloaded_mods):
            try:
                with open(downloaded_mods, "r") as file:
                    downloaded_mods_list = [line.strip() for line in file.readlines()]
            except:
                safe_unlink(downloaded_mods)
                open(downloaded_mods, 'a').close()
                downloaded_mods_list = []
        else:
            open(downloaded_mods, 'a').close()
            downloaded_mods_list = []
        
        if download_file_function_mod_folder_name not in downloaded_mods_list and is_bibite == False:
            with open(downloaded_mods, "w") as file:
                # Filter out empty strings and write each mod name on a new line
                downloaded_mods_list = [mod_name for mod_name in downloaded_mods_list if mod_name != '']
                # Avoids adding a empty line before first mod if no mods are downloaded
                if downloaded_mods_list:
                    file.write('\n'.join(downloaded_mods_list))
                    # Append the new mod name
                    file.write('\n' + download_file_function_mod_folder_name)
                else:
                    # Add the new mod name to not
                    file.write(download_file_function_mod_folder_name)

        if error_downloading_file == False:
            status_label.config(text="Download complete!")

# Function to extract filename from url
def get_filename_from_response(url):
    parsed_url = urlparse(url)
    filename = parsed_url.path.split('/')[-1]
    decoded_filename = unquote(filename)  # Decode URL-encoded characters
    return decoded_filename

# Function to start the download process
def start_download(url, mod_folder_name):
    global progress_bar
    status_label.config(text="Downloading...")
    download_thread = Thread(target=download_file, args=(url, mod_folder_name, False, False, f'{not_installed_mods}/{mod_folder_name}'))
    download_thread.start()

# Function to swap to the page where you can find and download mods
def Find_Mods():
    global page, mod_vars

    if page == 'display_downloaded_mods':
        for component in installed_mods_page_list:
            component.pack_forget()
        
        # Swap on downloadable mods frame
        for component in downloadable_mods_page_list:
            component.pack()
    
    if page == "More_Tools":
        for component in more_tools_page_list:
            component.pack_forget()

        # Swap on downloadable mods frame
        for component in downloadable_mods_page_list:
            component.pack()
    
    if page == "Credits":
        for component in credits_page_list:
            component.pack_forget()
        
        for component in downloadable_mods_page_list:
            component.pack()

        page = "More_Tools"

    if page != "Find_Mods":
        # Get the names of the available mods
        mod_names[:] = fetch_filenames()  # Use cached data
        # Add the mod names to a checkbutton list
        mod_vars = [] # Reset mod_vars list to stop duplicates checkbuttons from being added to the list braking other parts of code
        populate_checkbuttons(mod_names)

        page = "Find_Mods"

# Function to display downloaded mods on the first page
def List_Downloaded_Mods():
    global page
    if page == "Find_Mods":
        for component in downloadable_mods_page_list:
            component.pack_forget()

        for component in installed_mods_page_list:
            component.pack()
    
    if page == "More_Tools":
        for component in more_tools_page_list:
            component.pack_forget()

        for component in installed_mods_page_list:
            component.pack()
    
    if page == "Credits":
        for component in credits_page_list:
            component.pack_forget()
        
        for component in installed_mods_page_list:
            component.pack()

        page = "More_Tools"

    if page != "display_downloaded_mods":

        downloaded_mods_listbox.delete(0, "end")  # Clear existing list

        check_for_local_mods() # Check for downloaded mods that are not registerd

        # Display downloaded mods
        if os.path.isfile(downloaded_mods) and os.stat(downloaded_mods).st_size != 0:
            downloaded_mods_list = ""
            with open(downloaded_mods, "r") as file:
                try:
                    downloaded_mods_list = [line.strip() for line in file.readlines()]
                    downloaded_mods_list = [mod.split('/')[-1] for mod in downloaded_mods_list]
                except:
                    pass
            if downloaded_mods_list:
                for mod in downloaded_mods_list:
                    downloaded_mods_listbox.insert("end", mod)
        page = "display_downloaded_mods"

# Show more tools button
def more_tools_page():
    global page

    if page == "display_downloaded_mods":
        for component in installed_mods_page_list:
            component.pack_forget()
        
        for component in more_tools_page_list:
            component.pack()
        
        page = "More_Tools"

    if page == "Find_Mods":
        for component in downloadable_mods_page_list:
            component.pack_forget()
        
        for component in more_tools_page_list:
            component.pack()

        page = "More_Tools"
    
    if page == "Credits":
        for component in credits_page_list:
            component.pack_forget()
        
        for component in more_tools_page_list:
            component.pack()

        page = "More_Tools"

# Show more tools button
def credits_page():
    global page

    if page == "display_downloaded_mods":
        for component in installed_mods_page_list:
            component.pack_forget()
        
        for component in credits_page_list:
            component.pack()
        
        page = "Credits"

    if page == "Find_Mods":
        for component in downloadable_mods_page_list:
            component.pack_forget()
        
        for component in credits_page_list:
            component.pack()

        page = "Credits"
    
    if page == "More_Tools":
        for component in more_tools_page_list:
            component.pack_forget()

        for component in credits_page_list:
            component.pack()
        
        page = "Credits"

# Function to fetch filenames from GitHub or Dropbox with caching
def fetch_filenames():
    global mod_names_cache, cache_time, mod_repo_urls

    # Check if cache is valid
    if mod_names_cache is None or time.time() - cache_time > cache_duration:
        # Try each URL in the list until one succeeds
        for url in mod_repo_urls:
            parsed_url = urlparse(url)
            website_name = parsed_url.netloc
            print(f"Attempting to fetch from: {website_name}")

            if "github.com" in website_name:
                mod_names_cache = fetch_from_github(url)
            elif "dropbox.com" in website_name:
                mod_names_cache = fetch_from_dropbox(url)

            if mod_names_cache:  # Success, stop trying further URLs
                cache_time = time.time()
                save_cache_to_file()
                break

    return mod_names_cache

# Function to fetch mod filenames from GitHub
def fetch_from_github(url):
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
            status_label.config(text=error_message)
            
            # Save error to a log file
            with open(log_file, 'a') as file:
                file.write(f"\n{get_time()} {error_message}")
    except Exception as e:
        print(f"Error accessing GitHub: {e}")
    return None

def fetch_from_dropbox(url):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            content = response.text
            # Regex to find all filenames ending with ".TBM"
            mod_names = re.findall(r'([\w\-\.\d]+\.TBM)', content)
            print(mod_names)
            mod_names = list(set(mod_names))  # Remove duplicates
            
            if mod_names:
                return mod_names
            else:
                print("No .TBM files found in Dropbox data.")
        else:
            # Handle HTTP errors
            error_message = f"Dropbox status code: {response.status_code}"
            if response.status_code == 404:
                error_message += " - can't access page"
            if response.status_code == 403:
                error_message += " - Dropbox refused access to page"
            
            status_label.config(text=error_message)
            with open(log_file, 'a') as file:
                file.write(f"\n{get_time()} {error_message}")

    except Exception as e:
        print(f"Error accessing Dropbox: {e}")

    return None

# Function to fetch file contents from GitHub repository
def get_file_contents(mod_name):
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
        save_cache_to_file()
        
        if decoded_content:
            return decoded_content
    return None

# Function to save cache to a file
def save_cache_to_file():
    all_cache_data = {"mod_names_cache" : mod_names_cache,"cache_time" : cache_time, "mod_content_cache" : mod_content_cache}
    with open(cache_file, 'w') as file:
        json.dump(all_cache_data, file)
    status_label.config(text=f"Saved cache to file.")

# Function to reset and cleanup cache
def reset_cache():
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
                status_label.config(text=f"Invalid mod content, removing: {mod_name}")
        else:
            status_label.config(text=f"Mod not in mod_names_cache, removing: {mod_name}")

    # Update mod_content_cache with only valid mods that are also in mod_names_cache
    mod_content_cache = cleaned_mod_content_cache
    cache_time = time.time()  # Reset cache time to current time

    # Optionally, save the cleaned cache to file
    save_cache_to_file()
    status_label.config(text="Cache reset, and invalid mods removed.")

# Function to get mod install instructions for chosen mod from GitHub repository based on filename
def get_mod_url(mod_name):
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
    file_contents = get_file_contents(mod_name)
    if file_contents:
        
        lines = file_contents.split('\n') # Split the content into lines

        game_version_line = next((line for line in lines if line.startswith('game version: ')), None) # Find the line containing the URL

        if game_version_line:
            game_version = game_version_line.replace('game version: ', '').strip() # Extract the game version from the line
            return game_version
    return None

# Function to populate Checkbuttons with mod names and tooltips
def populate_checkbuttons(mod_names):
    for widget in downloadable_mods_frame.winfo_children():
        if isinstance(widget, Checkbutton):
            widget.destroy()

    # Keep track of mods already added
    added_mods = set()

    for mod_name in mod_names:
        mod_game_version = get_mod_game_version(mod_name)
        if (mod_name not in added_mods) and (mod_game_version == Game_version or Game_version == "All"):
            var = IntVar()
            mod_vars.append(var)
            chk = Checkbutton(downloadable_mods_frame, text=mod_name, variable=var, font=("Arial", 12))
            chk.pack(anchor='w', pady=5)

            mod_info = get_mod_decription(mod_name) # Get mod description

            # Create tooltip for each item in Checkbutton
            tooltips[chk] = CustomTooltip(downloadable_mods_frame, mod_info)
            chk.bind("<Enter>", tooltips[chk].show_tooltip)
            chk.bind("<Leave>", tooltips[chk].hide_tooltip)
            added_mods.add(mod_name)

def get_mod_decription(mod_name):
    file_contents = get_file_contents(mod_name)
    if file_contents:
        # Extract detailed information (e.g., description) from the file contents
        # This is an example, adjust according to how the information is stored in the file
        lines = file_contents.split('\n')
        description_line = next((line for line in lines if line.startswith('description: ')), None)
        if description_line:
            description = description_line.replace('description:', '').strip()
            return description
    return "No detailed information available."

def download_mods():
    global mod_folder_name, mod_names, downloaded_mods_list

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
                status_label.config(text=f"{mod_names[i].split('.')[0]} already downloaded")
            else: # Mod is not downloaded
                url = get_mod_url(mod_names[i])
                urls[i] = url
                if urls[i]:
                    # Download the mod
                    start_download(urls[i], mod_folder_name)
                else:
                    status_label.config(text=f"URL for {mod_names[i]} not found.")

# Used in install mods that way it can be used multiple times
def replace_dll(mod_name, not_installed_mod_path, not_installed_mod_folder, installed_mods_list):
    try:
        status_label.config(text=f"Installing {mod_name}") # Show what mod is being installed
        
        # If mod isnt installed and no other mod is installed
        if f'{not_installed_mod_path}' not in os.listdir(not_installed_mod_folder) and len(installed_mods_list) == 0 and not os.path.exists(f'{Game_folder}/The Bibites_Data/Managed/BibitesAssembly.dll.TBM'):
            shutil.move(f'{not_installed_mod_path}', f'{Game_folder}/The Bibites_Data/Managed') # Move the mod

            status_label.config(text=f"Installed {mod_name}") # Display that mod is installed
            
            # Add the installed mod to the installed_mods_list
            installed_mods_list = mod_name
            with open(installed_mods, 'w') as file: # Write the installed_mod_list to keep it after TBMM closes
                file.write(installed_mods_list)
        
        # If any other mod is installed replace the curent one
        else:
            # Check if mod you are trying to install is installed if it isn't install it
            if mod_name not in installed_mods_list:
                # move other mods back to uninstalled location
                for mod in installed_mods_list:
                    try:
                        for mod in installed_mods_list:
                            installed_mod_not_installed_mod_folder = f'{not_installed_mods}/{mod}'
                            shutil.move(f'{Game_folder}/The Bibites_Data/Managed/BibitesAssembly.dll.TBM', installed_mod_not_installed_mod_folder) # Move the mod
                    except:
                        if os.path.exists(f'{Game_folder}/The Bibites_Data/Managed/BibitesAssembly.dll.TBM'):
                            os.unlink(f'{Game_folder}/The Bibites_Data/Managed/BibitesAssembly.dll.TBM')

                # Install the mod
                if not os.path.exists(f'{Game_folder}/The Bibites_Data/Managed/BibitesAssembly.dll.TBM'): # Check if mod isnt installed
                    shutil.move(f'{not_installed_mod_path}', f'{Game_folder}/The Bibites_Data/Managed') # Mod is not installed move the mod
                else:
                    with open(not_installed_mod_path, 'rb') as file:
                        temp = file.read()
                    
                    with open(f'{Game_folder}/The Bibites_Data/Managed/BibitesAssembly.dll.TBM', 'wb') as file:
                        file.write(temp)
                    shutil.move(not_installed_mod_path, f'{Game_folder}/The Bibites_Data/Managed/BibitesAssembly.dll.TBM')

                # Add the installed mod to the installed_mods_list
                installed_mods_list = [mod_name]
                with open(installed_mods, 'w') as file: # Write the installed_mod_list to keep it after TBMM closes
                    file.write(mod_name)
                
                status_label.config(text=f"Installed {mod_name}") # Display that mod is installed
                installed_mods_list_pretty_for_display = [] # List stores the installed mods without .TBM to make it prettier
                for mod in installed_mods_list:
                    mod = mod.split('.')[0]
                    installed_mods_list_pretty_for_display.append(mod)
                installed_mod_label.config(text=f"Installed mod: {''.join(installed_mods_list_pretty_for_display)}", font=("Arial", 12))
                settings['installed_mods_list'] = installed_mods_list
                save_settings(installed_mods_list)

    except Exception as e:
        messagebox.showerror("Error", f"Unexpected error: {e}")
        
        # Save error to a log file
        with open(log_file, 'a') as file:
            file.write(f"\n{get_time()} Unexpected error: {e}")

def install_mods(): # Install a mod so you can play modded

    if os.path.exists(Game_path) == False:
        status_label.config(text=f"Game path is {Game_path}, you need to set a game path to be able to install mods correctly")
        return
    
    # Install selected mods
    for mod_index in downloaded_mods_listbox.curselection():
        mod_name = downloaded_mods_listbox.get(mod_index)
        not_installed_mod_folder = f'{not_installed_mods}/{mod_name}'

        with open(installed_mods, 'r') as file:
            installed_mods_list = file.read().splitlines()

        if len(os.listdir(not_installed_mod_folder)) == 0 and mod_name not in installed_mods_list: # Check is mod exists or is installed if it is not any of those download it again
            url = get_mod_url(mod_name)
            if url:
                mod_folder_name = mod_name
                download_file(url, mod_folder_name, False, False, f'{not_installed_mods}/{mod_folder_name}')

        if mod_name not in installed_mods_list: # The mod is not installed and need to get path to install it
            for file in os.listdir(not_installed_mod_folder):
                if file.endswith('.dll') or file.endswith('dll.TBM'):
                    dll = file
                    break

            not_installed_mod_path = f'{not_installed_mod_folder}/{dll}'

            file_contents = get_file_contents(mod_name) # Get content of mod file

            # Get install instructions from the mod file
            lines = file_contents.split('\n')
            how_install = next((line for line in lines if line.startswith('install:')), None)
            if how_install:
                install_instructions = how_install.replace('install: ', '').strip()
                if not_installed_mod_path.endswith('.dll'):
                    os.rename(not_installed_mod_path, f'{not_installed_mod_path}.TBM')
                    not_installed_mod_path = f'{not_installed_mod_path}.TBM'
            
            if install_instructions == 'replace':   # Mod is installed by replacing BibitesAssembly.dll
                replace_dll(mod_name, not_installed_mod_path, not_installed_mod_folder, installed_mods_list)

                bibites_to_download = next((line for line in lines if line.startswith('bibites:')), None) # if there are bibites download them into the dibites folder
                if bibites_to_download != None:
                    bibites_to_download = bibites_to_download.replace('bibites: ', '').strip()
                    # Check if there are multiple URLs separated by commas
                    if ',' in bibites_to_download:
                        bibites_to_download = bibites_to_download.split(', ')
                    else:
                        # If there is only one URL, make it a list
                        bibites_to_download = [bibites_to_download]
                
                    download_bibites(bibites_to_download)

            elif install_instructions == 'replace+':   # Mod is installed by replacing BibitesAssembly.dll and it needs additional files
                status_label.config(text=f'Install instructions: {install_instructions} will be implemented in the next update 0.07')
                return
                replace_dll(mod_name, not_installed_mod_path, not_installed_mod_folder, installed_mods_list)

                extra_files = next((line for line in lines if line.startswith('extra_files:')), None)
                print(extra_files)
                list_of_files = extra_files.split(',')
                print(list_of_files)

# extra_files: list all extra files like this comma marks a new file: url: url goes here location: excact location to where it is installed starting from the location where the game exe is
# for folders do folder: url to the folder
                status_label.config(text=f'Install instructions: {install_instructions} is being worked on.\nHope it installed correctly')

            else: # TBMM can't install the mod yet
                status_label.config(text=f"{mod_name} can't be installed because TBMM cant install with install instructions: {install_instructions}")
        
        # The mod you are trying to install ia already installed
        else:
            status_label.config(text=f"{mod_name} is aleady installed") # Display that mod is already installed
            installed_mods_list_pretty_for_display = [] # List stores the installed mods without .TBM to make it prettier
            for mod in installed_mods_list:
                mod = mod.split('.')[0]
                installed_mods_list_pretty_for_display.append(mod)
            installed_mod_label.config(text=f"Installed mod: {''.join(installed_mods_list_pretty_for_display)}", font=("Arial", 12))

            settings['installed_mods_list'] = installed_mods_list
            save_settings(installed_mods_list)

def download_bibites(bibites_to_download):
    for bibite in bibites_to_download:
        download_file(bibite, "bibites", True, True) # URL, Name of the folder where downloaded to, Is it a bibite file that is downloaded?, Where to move the downloaded file

def save_settings(): # Save to settings file
    global settings
    with open(settings_file, 'w') as file:
        print(settings)
        json.dump(settings, file, indent=2)
        print("saved settings")

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
                status_label.config(text="Playing without mods")

            # Catch and display error to the user
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error running the game", f"Unexpected error: {e}")    # Display message box with error
                
                # Save error to a log file
                with open(log_file, 'a') as file:
                    file.write(f"\n{get_time()} Error running the game: {e}")
                
                status_label.config(text=f"Error running the game: {e}") # Display error on status label
            except Exception as e:
                messagebox.showerror("Error", f"Unexpected error: {e}") # Display message box with error
                
                # Save error to a log file
                with open(log_file, 'a') as file:
                    file.write(f"\n{get_time()} Unexpected error: {e}")
                
                status_label.config(text=f"Unexpected error: {e}") # Display error on status label

        if Modded == ('Yes'):
            ScriptingAssembliesText['names'][68] = 'BibitesAssembly.dll.TBM' # Edit what dll is loaded to the modded one
            with open(ScriptingAssemblies, "w") as file:                     # Write the info
                json.dump(ScriptingAssembliesText, file)

            try:
                subprocess.Popen([Game_path]) # Run The Bibites without checking for mods.
                with open(installed_mods, 'r') as file:
                    installed_mods_list = file.read().splitlines()
                    installed_mods_list_pretty_for_display = [] # List stores the installed mods without .TBM to make it prettier
                    for mod in installed_mods_list:
                        mod = mod.split('.')[0]
                        installed_mods_list_pretty_for_display.append(mod)
                status_label.config(text=f"Playing with mods:\n{''.join(installed_mods_list_pretty_for_display)}")

            # Catch and display error to the user
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error running the game", f"Unexpected error: {e}")    # Display message box with error
                
                # Save error to a log file
                with open(log_file, 'a') as file:
                    file.write(f"\n{get_time()} Error running the game: {e}")
                
                status_label.config(text=f"Error running the game: {e}") # Display error on status label
            except Exception as e:
                messagebox.showerror("Error", f"Unexpected error: {e}") # Display message box with error
                
                # Save error to a log file
                with open(log_file, 'a') as file:
                    file.write(f"\n{get_time()} Unexpected error: {e}")
                
                status_label.config(text=f"Unexpected error: {e}") # Display error on status label
    else:
        status_label.config(text=f"{Game_path} does not exist, you need to set a valid game path to be able to run the game")

# Create Tkinter window
window = Tk()
window.title(f"TBMM {version_number}")
# Get the script dir
script_dir = Path(__file__).parent.absolute()
images_folder = f'{script_dir}/Images' # Path to folder with images
window.iconbitmap(f"{images_folder}/TBMM icon.ico") # Needs to use script dir and have the icon in the root folder

# Get screen width and height
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

# Set window size and position to fullscreen windowed
window_width = int(screen_width * 0.8)
window_height = int(screen_height * 0.8)
window.geometry(f"{window_width}x{window_height}+{int((screen_width - window_width) / 2)}+{int((screen_height - window_height) / 2)}")

window.minsize(1000, 450)

# Title label
title_label = Label(window, text="The Bibites Mod Manager", font=("Arial", 24, "bold"))
title_label.pack(pady=(20, 10))

# Button to display downloaded mods (main page)
display_downloaded_mods_button = Button(window, text="View Installed Mods", command=List_Downloaded_Mods, font=("Arial", 12))

# Button where you find mods to download and install
find_mods_button = Button(window, text="Get Mods", command=Find_Mods, font=("Arial", 12))

# Button That takes you to the credits page
credits_button = Button(window, text="Show Credits", command=credits_page, font=("Arial", 12))

Bibite_Research_Conglomerate_hyperlink = Label(window, text="Join Bibite Research Conglomerate Discord Server", fg="blue", cursor="hand2", font=("Arial", 12))
Bibite_Research_Conglomerate_hyperlink.bind("<Button-1>", lambda e: open_link(Discord_invite_link))

# Status Label
status_label = Label(window, text="", font=("Arial", 14))
status_label.pack(side="bottom", anchor="s", pady=20)

# Frame for inputs
input_frame = Frame(window)
input_frame.pack(padx=20, pady=10)

# Game path label and button
game_path_label = Label(input_frame, text="Game path: None", font=("Arial", 14))
game_path_label.grid(row=1, column=0, columnspan=2, padx=(0, 10))

game_path_button = Button(input_frame, text="Get path to game exe", command=get_game_path, font=("Arial", 12))
game_path_button.grid(row=1, column=2, columnspan=1)

# Label showing what version of the game is being modded
# This will make mods for newer version not able to be installed and older versions will show error
version_label = Label(input_frame, text="Game version not specified", font=("Arial", 13))
version_label.grid(row=0, column=0, columnspan=2, padx=(0, 10), sticky="w")

version_button = Button(input_frame, text="Game version", command=get_game_version, font=("Arial", 12))
version_button.grid(row=0, column=2, columnspan=2, sticky="w")

# Listbox to display downloaded mods
downloaded_mods_listbox = Listbox(input_frame, font=("Arial", 12), width=50, selectmode="single") # selectmode="multiple"
downloaded_mods_listbox.grid(row=2, column=0, columnspan=3, sticky="ew")

# Add scrollbar
scrollbar = Scrollbar(input_frame, orient="vertical", command=downloaded_mods_listbox.yview)
scrollbar.grid(row=2, column=3, sticky="nsw")
downloaded_mods_listbox.config(yscrollcommand=scrollbar.set)

# Button to install mods
install_mods_button = Button(input_frame, text="Install mods", command=install_mods, font=("Arial", 12)) # Button to install mods
install_mods_button.grid(row=3, column=2, sticky="w")

# Button to play the game without mods
vanilla_play_button = Button(input_frame, text="Play Vanilla", command=lambda: play_game(Modded='No'), font=("Arial", 12))
vanilla_play_button.grid(row=3, column=0, sticky="w")

# Button to play the game with mods
Mod_play_button = Button(input_frame, text="Play Modded", command=lambda: play_game(Modded='Yes'), font=("Arial", 12))
Mod_play_button.grid(row=3, column=1, sticky="w")

refresh_cache_button = Button(input_frame, text="Refresh cache", command=reset_cache, font=("Arial", 12))
refresh_cache_button.grid(row=2, column=4, sticky="n")

get_the_bibites_button = Button(input_frame, text="Download The Bibites", command=get_the_bibites, font=("Arial", 12))
get_the_bibites_button.grid(row=2, column=4, pady=40, sticky="n")

installed_mod_label = Label(input_frame, text="Installed mod: I do not know what mod is installed", font=("Arial", 12))
installed_mod_label.grid(row=4, column=0, columnspan=3)

# A list of all components on the installed mods page to make swapping pages easier
installed_mods_page_list = [input_frame]

# Frame that has the list of mods/reskins you can download
downloadable_mods_frame = Frame(window)

# Download mods
download_mods_button = Button(downloadable_mods_frame, text="Download mods", command=download_mods, font=("Arial", 16))
download_mods_button.pack(pady=(10, 20), side="bottom")

# A list of all components on the downloadable mods page to make swapping pages easier
downloadable_mods_page_list = [downloadable_mods_frame]

# More tool page where you can find good tools
more_tools_button = Button(window, text="Community Tools", command=more_tools_page, font=("Arial", 12))

more_tools_frame = Frame(window)

# Label that shows the text Einstein
Best_tools_lable = Label(more_tools_frame, font=("Arial", 10, "bold"), wraplength=1000, text="Best tools made for The Bibites")
Best_tools_lable.grid(row=0, column=0, sticky="n")

# Label that shows the text Einstein
Einstein_lable = Label(more_tools_frame, font=("Arial", 18, "bold"), wraplength=1000, text="Einstein")
Einstein_lable.grid(row=1, column=0)

# Label to display a short descriptive text for Einstein brain editor
Einstein_info_lable = Label(more_tools_frame, font=("Arial", 12), wraplength=1000, text="Edit brains by interacting with a diagram of neurons and synapses. Zoom and pan around the diagram, paint neurons different colors, automatically convert brains between bibite versions, view neuron values calculated tick-by-tick and discover other bells and whistles.")
Einstein_info_lable.grid(row=2, column=0)

# Label with hyperlink that takes you to Einstein latest release github page with download
Einstein_hyperlink = Label(more_tools_frame, text="Download Einstein", fg="blue", cursor="hand2", font=("Arial", 12))
Einstein_hyperlink.grid(row=3, column=0)
Einstein_hyperlink.bind("<Button-1>", lambda e: open_link("https://github.com/quaris628/EinsteinEditor/releases/latest"))

def open_link(url):
    webbrowser.open_new(url)

Einstein_image = PhotoImage(file=f"{images_folder}/Einstein_Review.png")

Einstein_image_label = Label(more_tools_frame, image = Einstein_image)
Einstein_image_label.grid(row=4, column=0, pady=5)

more_tools_page_list = [more_tools_frame]

# Credits page to show who helped with TBMM
credits_frame = Frame(window)

# Lable that displays the credits
credits_label_text = "MOD MAKERS:\nFiveBalesofHay\nMelting Diamond\n\nRESKIN MAKERS:\nmiau\nFiveBalesofHay\n\nART:\n\nTBMM icon - miau"
credits_label = Label(credits_frame, text=credits_label_text, font=("Arial", 14))
credits_label.pack(anchor="center", pady=20)

credits_page_list = [credits_frame]

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

    # Apply button positions
    display_downloaded_mods_button.place(x=20, y=window_height / 12.5)
    find_mods_button.place(x=20, y=display_downloaded_mods_button.winfo_y() + button_height + padding)
    more_tools_button.place(x=20, y=find_mods_button.winfo_y() + button_height + padding)
    
    credits_button.place(x=20, y=window_height - button_height - 15)

    # Position Bibite_Research_Conglomerate_hyperlink in bottom-right corner
    hyperlink_width = Bibite_Research_Conglomerate_hyperlink.winfo_reqwidth()
    hyperlink_height = Bibite_Research_Conglomerate_hyperlink.winfo_reqheight()
    Bibite_Research_Conglomerate_hyperlink.place(x=window_width - hyperlink_width - 20, y=window_height - hyperlink_height - 20)

    # Update wraplengt of text to make it look better on smaller windows
    Einstein_info_lable.configure(wraplength=min(1000, window_width - 375))

# Bind the function to move find_mods_button
window.bind('<Configure>', move_left_buttons)

# Define custom tooltip class
class CustomTooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None

    def show_tooltip(self, event=None):
        x = event.x_root
        y = event.y_root + 10

        self.tooltip_window = Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")

        label = Label(self.tooltip_window, text=self.text, justify='left', background='gainsboro', relief='solid', borderwidth=1, wraplength=300)
        label.pack(ipadx=1)

        # Update the position of the tooltip window
        self.widget.update_idletasks()
        self.tooltip_window.geometry(f"+{x}+{y}")

    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()

# Dictionary to hold tooltips
tooltips = {}

# Set destination path
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    downloading = 'Download'
    not_installed_mods = 'not_installed_mods'
    installed_mods = 'installed_mods.txt'
    downloaded_mods = 'downloaded_mods.txt'
    cache_file = 'cache.json'
    settings_file = 'settings.json'
    log_file = f'log.txt'
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
            
            if 'installed_mods_list' in settings:
                installed_mods_list = settings['installed_mods_list']
                installed_mods_list_pretty_for_display = [] # List stores the installed mods without .TBM to make it prettier
                for mod in installed_mods_list:
                    mod = mod.split('.')[0]
                    installed_mods_list_pretty_for_display.append(mod)
                installed_mod_label.config(text=f"Installed mod: {''.join(installed_mods_list_pretty_for_display)}", font=("Arial", 12))
            else:
                installed_mod_label.config(text=f"Installed mod: I do not know what mod is installed", font=("Arial", 12))
                error = True
                errormessage = errormessage + 'installed_mods_list '

            if error == True:
                status_label.config(text=f'Error loading settings: {errormessage}')
    
            if 'Game_path' in settings and os.path.isfile(Game_path):
                game_path_label.config(text=f'Game path: {Game_path}', font=("Arial", 12))
            else:
                game_path_label.config(text=f'Error game path can not be found', font=("Arial", 12))
                Game_path = ''
    except Exception as e:
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

# Update list of installed mods on start
List_Downloaded_Mods()

# Runs the app
window.mainloop()