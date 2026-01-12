# Anything that accesses the internet, for example if "import requests" is needed
import requests, webbrowser, os, time, re, shutil, io, base64
from zipfile import ZipFile
from threading import Thread
from urllib.parse import urlparse, unquote
from UI import messagebox_showinfo

windows_nightly_download_link = "https://nightly.link/MeltingDiamond/TBMM/workflows/build-nightly/main/TBMM-Windows.zip"
linux_nightly_download_link = "https://nightly.link/MeltingDiamond/TBMM/workflows/build-nightly/main/TBMM-Linux.zip"
mac_nightly_download_link  =  "https://nightly.link/MeltingDiamond/TBMM/workflows/build-nightly/main/TBMM-MacOS.zip"
release_download_link = "https://github.com/MeltingDiamond/TBMM/releases/latest"

def open_link(url):
    webbrowser.open_new(url)

def download_new_tbmm_version(os, tbmm_folder, downloading, log, status_label, safe_unlink, log_file, get_time, nightly = False):
    if nightly:
        if os == "Windows":
            download_tbmm_update(download_link=windows_nightly_download_link, tbmm_folder=tbmm_folder, downloading=downloading, log=log, status_label=status_label, safe_unlink=safe_unlink, log_file=log_file, get_time=get_time)
        elif os == "Linux":
            download_tbmm_update(download_link=linux_nightly_download_link, tbmm_folder=tbmm_folder, downloading=downloading, log=log, status_label=status_label, safe_unlink=safe_unlink, log_file=log_file, get_time=get_time)
        elif os == "Mac":
            download_tbmm_update(download_link=mac_nightly_download_link, tbmm_folder=tbmm_folder, downloading=downloading, log=log, status_label=status_label, safe_unlink=safe_unlink, log_file=log_file, get_time=get_time)
    else:
        open_link(release_download_link)

def download_new_tbmm_version_old(os, nightly = False):
    if nightly:
        if os == "Windows":
            open_link(windows_nightly_download_link)
        elif os == "Linux":
            open_link(linux_nightly_download_link)
        elif os == "Mac":
            open_link(mac_nightly_download_link)
    else:
        open_link(release_download_link)

def download_tbmm_update(download_link, tbmm_folder, downloading, log, status_label, safe_unlink, log_file, get_time):
    try:
        download_file(url=download_link, location=str(tbmm_folder), downloading=downloading, log=log, status_label=status_label, safe_unlink=safe_unlink, log_file=log_file, get_time=get_time)
        with ZipFile(os.path.join(tbmm_folder, get_filename_from_response(download_link)), "r") as update_zip:
            update_zip.extractall(tbmm_folder)
        safe_unlink(os.path.join(tbmm_folder, get_filename_from_response(download_link)))
        status_label.config(text="Restart TBMM to update to the new version")
        messagebox_showinfo("Restart TBMM to update", "Restart TBMM to update to the new version")
    except Exception as e:
        log(f"Failed to update to new version using new update code\nExited with error: {e}", save_to_file=True)

def download_BepInEx(user_os):
    """
    Download BepInEx somewhere
    :param user_os: The os the user is running used for choosing the correct version"""
    response = requests.get("https://api.github.com/repos/BepInEx/BepInEx/releases/latest")
    response_json = response.json()
    response = requests.get(response_json["assets_url"])
    windows_64x_download_url = ""
    windows_32x_download_url = ""
    linux_download_url = ""
    macos_download_url = ""
    for i in response.json():
        if "win_x64" in i["name"]:
            windows_64x_download_url = i["browser_download_url"]
            continue
        if "win_x86" in i["name"]:
            windows_32x_download_url = i["browser_download_url"]
            continue
        if "linux_x64" in i["name"]:
            linux_download_url = i["browser_download_url"]
            continue
        if "macos_x64" in i["name"]:
            macos_download_url = i["browser_download_url"]
            continue
    print(windows_64x_download_url)
    print(windows_32x_download_url)
    print(linux_download_url)
    print(macos_download_url)

def update_check(version, log, nightly=False):
    """
    Checks if the local version is older than the latest nightly. 
    Returns True if there is a newer version.
    
    :param version: the version currently installed (e.g., "nightly-20250725203538")
    :param nightly: if True, checks against nightly version
    """
    try:
        if not nightly:
            response = requests.get("https://api.github.com/repos/MeltingDiamond/TBMM/releases/latest")
            response_json = response.json()
            latest_stable_version = response_json["tag_name"]
            
            latest_stable_version = latest_stable_version.split("v")[1]

            local_version = [int(p) for p in version.split('.')]
            latest_online_version = [int(p) for p in latest_stable_version.split('.')]

            # Normalize lengths by padding the shorter one with zeros
            max_len = max(len(local_version), len(latest_online_version))
            local_version += [0] * (max_len - len(local_version))
            latest_online_version += [0] * (max_len - len(latest_online_version))

            if local_version < latest_online_version:
                # There exists a newer release version
                log(f"A newer release version is available: {latest_stable_version}", save_to_file=False)
                return True

            return False

        log("Checking nightly version...", save_to_file=False)
        response = requests.get("https://raw.githubusercontent.com/MeltingDiamond/TBMM/main/version.txt")
        if response.status_code != 200:
            log("Failed to fetch version info.", save_to_file=False)
            return False

        latest_version = response.text.strip()
        log(f"Latest nightly version: {latest_version}", save_to_file=False)

        # Extract numeric part of nightly version and compare as integers
        local_num = int(version.split("-")[1])
        latest_num = int(latest_version.split("-")[1])

        if local_num < latest_num:
            log(f"A newer nightly version is available: {latest_version}", save_to_file=False)
            return True

        log("You are using the latest nightly version.", save_to_file=False)
        return False

    except Exception as e:
        log(f"Error during version check: {e}", save_to_file=True)
        return False

# Function to fetch filenames from GitHub or Dropbox with caching
def fetch_filenames(log, cache_duration, mod_repo_urls, get_website_name, save_cache_to_file, status_label, mod_names, mod_names_cache, cache_time):
    '''Get the file names of all the available mods'''

    # Check if cache is valid
    if mod_names_cache is None or time.time() - cache_time > cache_duration or mod_names_cache == []:
        # Check if user has internet access
        if has_internet_connection():
            # Try each URL in the list until one succeeds
            for url in mod_repo_urls:
                website_name = get_website_name(url)
                print(f"Attempting to fetch filename from: {website_name}")

                if "github.com" in website_name:
                    mod_names_cache = fetch_from_github(url, log, status_label)
                elif "dropbox.com" in website_name:
                    mod_names_cache = fetch_from_dropbox(url, mod_names, log, status_label)

                print(mod_names_cache)
                if mod_names_cache:  # Success, stop trying further URLs
                    cache_time = time.time()
                    print(cache_time)
                    print(time.time() - cache_time > cache_duration)
                    save_cache_to_file(cache_time)
                    return mod_names_cache

            # failed to fetch mod names from internet return empty list to avoid breaking code.
            print(" Did not download any mod names, there was an error, returns []")
            return []
        else: # No internet
            log("You have no internet", True)
            status_label.config(text="You have no internet")

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
def fetch_from_github(url, log, status_label):
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
            log(error_message, True)
            status_label.config(text=error_message)
    except Exception as e:
        print(f"Error accessing GitHub: {e}")
    return None

def fetch_from_dropbox(url, mod_names, log, status_label):
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
            
            log(error_message, True)
            status_label.config(text=error_message)

    except Exception as e:
        print(f"Error accessing Dropbox: {e}")

    return None

# Function to fetch file contents
def get_file_contents(mod_name, cache_duration, save_cache_to_file, mod_content_cache, log, mod_repo_urls):
    '''Gets file content from cache, if that isn't valid either github or dropbox using the name of the mod'''

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
            log(f"Attempting to fetch content from: {website_name}", False)

            if "github.com" in website_name:
                mod_cache = get_file_contents_from_github(mod_name, mod_content_cache, cache_duration)
            elif "dropbox.com" in website_name:
                mod_cache = get_file_contents_from_dropbox(mod_name, url, mod_content_cache)

            if mod_cache:
                cache_time = time.time()
                save_cache_to_file(cache_time)
                return mod_content_cache[path]['content']
    else:
        return None

# Function to fetch file contents from GitHub repository
def get_file_contents_from_github(mod_name, mod_content_cache, cache_duration):
    '''Get the content for a mod from github'''
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

def get_file_contents_from_dropbox(mod_name, url, mod_content_cache):
    '''Get the content for a mod from dropbox'''
    path = f"Mods/{mod_name}"

    try:
        # Download the ZIP file from Dropbox
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print(f"Error downloading from Dropbox: {response.status_code}")
            return None
        
        # Open the ZIP file in memory
        zip_file = ZipFile(io.BytesIO(response.content))

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

# Function to get mod install instructions for chosen mod from GitHub repository based on filename
def get_mod_url(file_contents):
    '''Get url from a .TBM file'''
    if file_contents:
        
        lines = file_contents.split('\n') # Split the content into lines

        url_line = next((line for line in lines if line.startswith('url: ')), None) # Find the line containing the URL

        if url_line:
            url = url_line.replace('url:', '').strip() # Extract the URL from the line
            return url
    return None

# Function to extract filename from url
def get_filename_from_response(url):
    '''Gets the filename from a url (the ending)
    :param url: any url'''
    parsed_url = urlparse(url)
    filename = parsed_url.path.split('/')[-1]
    decoded_filename = unquote(filename)  # Decode URL-encoded characters
    return decoded_filename

def get_website_name(url):
    '''Gets the name of a website from a url'''
    parsed_url = urlparse(url)
    return parsed_url.netloc

def download_file(url, location, downloading, log, status_label, safe_unlink, log_file, get_time): # Downloads the file at url and places it in location
    '''
    Downloads the file at url and places it in location.
    :param url: Web url to file to download
    :param location: Location the file is downloaded to
    :param downloading: Path to where the file gets temporarily downloaded to before it is moved to the location.
    :param log: Function used to write logs
    :param status_label: UI label where the current status gets written
    :param safe_unlink: A function that safely deletes a file in almost any circumstance'''

    filename = get_filename_from_response(url) # The name of the file being downloaded
    location_folder = get_filename_from_response(location) # The folder where the file will end up
    filepath = f"{location}/{filename}" # Where the file will end up after this function finishes
    
    if location_folder.endswith(".TBM"):
        mod_name = location_folder
    else:
        mod_name = filename

    downloading_folder = f'{downloading}/{location_folder}'
    downloading_path = f'{downloading_folder}/{filename}' # Where the file will be downloaded to temporarily before being moved to the correct location
    website = get_website_name(url)

    error_downloading_file = False # False unless there are at least 1 error downloading files
    mod_exists = False

    try: # Checks if it can connect with internet
        response = requests.get(url, stream=True)
        total = int(response.headers.get('content-length', 0))
    except requests.exceptions.MissingSchema as e:

        log(e, True)
        status_label.config(text=e)
    except Exception as e:
        log(f"Can not connect to {website} to get mod data, error: {e}", True)
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
            log(f"Downloading... {percent_done}%", False)
            status_label.config(text=f"Downloading... {percent_done}%")

    # Check if downloaded size matches the total size
    if downloaded >= total:
        try:
            if not os.path.exists(location):
                    os.makedirs(location)# folder does not exist make it
            if not os.path.isfile(filepath):
                shutil.move(downloading_path, filepath) # Mod doesn't exist move the mod
                safe_unlink(downloading_folder) # Remove mod folder in downloading folder since it isn't needed

            elif os.path.isfile(filepath):
                with open(downloading_path, 'rb') as new_file:
                    new_content = new_file.read()
                with open(filepath, 'rb') as existing_file:
                    existing_content = existing_file.read()
                if new_content == existing_content: # Mod exists do nothing
                    mod_exists = True
                    log(f"{filename} already downloaded", False)
                    status_label.config(text=f"{filename} already downloaded")

        except Exception as e:
            error_downloading_file = True

            if os.path.exists(location):
                if os.listdir(location) == 0 and mod_exists == False:
                    os.remove(location) # Folder exists, is empty and the mod doesn't exist, remove it

            # Save error to a log file
            with open(log_file, 'a') as file:
                file.write(f"\n{get_time()} Error downloading {mod_name}: {e}")

            log(f"Error download {mod_name}: {e}", False)
            status_label.config(text=f"Error download {mod_name}: {e}")
        
        if error_downloading_file == False and mod_exists == False:
            log(f"Downloading {mod_name} complete!", False)
            status_label.config(text=f"Downloading {mod_name} complete!")

# Function to start the download process
def start_download(url, location, log, status_label, downloading, safe_unlink, log_file, get_time):
    '''Starts downloading a file from a url in a thread'''
    log("Downloading...", False)
    status_label.config(text="Downloading...")
    download_thread = Thread(target=download_file, args=(url, location, downloading, log, status_label, safe_unlink, log_file, get_time))
    download_thread.start()

def download_modse(downloaded_mods, mod_names, mod_vars, not_installed_mods, cache_duration, mod_repo_urls, mod_names_cache, cache_time, downloading, log_file, mod_content_cache, handlers):
    '''Download selected mods from mod_vars'''

    log = handlers['log']
    status_label = handlers['status_label']
    get_mod_install_description = handlers['get_mod_install_description']
    save_cache_to_file = handlers['save_cache_to_file']
    get_file_contents = handlers['get_file_contents']
    safe_unlink = handlers['safe_unlink']
    get_time = handlers['get_time']

    # Get a list of downloaded mods
    if os.path.isfile(downloaded_mods):
        try:
            with open(downloaded_mods, "r") as file:
                downloaded_mods_list = [line.strip() for line in file.readlines()] # List of mods that are downloaded
        except:
            open(downloaded_mods, 'a').close() # file is none existent or broken. Recreate it


    urls = []
    if len(mod_names) >= len(mod_vars): # Check if mod_vars is equal or less than mod_names to avoid trying to get a mod that is outside the mod_names list
        mod_names[:] = fetch_filenames(log, cache_duration, mod_repo_urls, get_website_name, save_cache_to_file, status_label, mod_names, mod_names_cache, cache_time)
    
    # Loop through all mod Checkbuttons to check which ones are selected, so the selected ones can be downloaded if not already downloaded.
    for i, var in enumerate(mod_vars):
        urls.append(None)
        if var.get() == 1: # The mod is selected and will be downloaded
            mod_folder_name = mod_names[i]
            if mod_folder_name in downloaded_mods_list: # Check if mod is downloaded
                log(f"{mod_names[i].split('.')[0]} already downloaded", False)
                status_label.config(text=f"{mod_names[i].split('.')[0]} already downloaded")
            else: # Mod is not downloaded
                file_content = get_file_contents(mod_names[i], cache_duration, save_cache_to_file, mod_content_cache, log, mod_repo_urls)
                url = get_mod_url(file_content)
                urls[i] = url
                if urls[i]:
                    install_type = get_mod_install_description(mod_names[i])
                    download_location = f"{not_installed_mods}/{install_type}/{mod_folder_name}"
                    # Download the mod
                    start_download(urls[i], download_location, log, status_label, downloading, safe_unlink, log_file, get_time)
                    
                    # Add mod name to the list
                    downloaded_mods_list.append(mod_folder_name)
                else:
                    log(f"URL for {mod_names[i]} not found.", False)
                    status_label.config(text=f"URL for {mod_names[i]} not found.")
    with open(downloaded_mods, "w") as downloaded_mods_file:
        downloaded_mods_file.write('\n'.join(downloaded_mods_list))