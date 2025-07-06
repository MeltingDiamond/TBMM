import webbrowser
from tkinter import Tk, Label, Button, Frame, Listbox, Scrollbar, Toplevel, Text, PhotoImage
from pathlib import Path
from The_Bibites_Mod_Manager import version_number, list_downloaded_mods, download_mods_page, more_tools_page, credits_page, Discord_invite_link, status_label_font_size, get_game_path, Game_version, get_game_version, install_mods, play_game, reset_cache, get_the_bibites, get_time, download_mods

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

window.minsize(1000, 550)

# Title label
title_label = Label(window, text="The Bibites Mod Manager rewritten", font=("Arial", 24, "bold"))
title_label.pack(pady=(20, 10))

# Button to display downloaded mods (main page)
display_downloaded_mods_button = Button(window, text="Main", command=list_downloaded_mods, font=("Arial", 12))

# Button where you find mods to download and install
find_mods_button = Button(window, text="Get Mods", command=download_mods_page, font=("Arial", 12))

# More tool page where you can find good tools
more_tools_button = Button(window, text="Community Tools", command=more_tools_page, font=("Arial", 12))

# Button That takes you to the credits page
credits_button = Button(window, text="Show Credits", command=credits_page, font=("Arial", 12))

Bibite_Research_Conglomerate_hyperlink = Label(window, text="Join Bibite Research Conglomerate Discord Server", fg="blue", cursor="hand2", font=("Arial", 11))
Bibite_Research_Conglomerate_hyperlink.bind("<Button-1>", lambda e: open_link(Discord_invite_link))

# Status Label used to show status to the user
status_label = Label(window, text="", wraplength=750, font=("Arial", status_label_font_size))
status_label.pack(side="bottom", anchor="s", pady=20, padx=(0, 150))

def open_link(url):
    webbrowser.open_new(url)

# The main page where you view mods
main_frame = Frame(window)
main_frame.pack(padx=(140, 20), pady=10)
main_frame.grid_rowconfigure(6, weight=1)
main_frame.grid_columnconfigure(2, weight=1)

# Game path label and button
game_path_label = Label(main_frame, text="Game path: None", font=("Arial", 14))
game_path_label.grid(row=1, column=0, columnspan=2, padx=(0, 10))

game_path_button = Button(main_frame, text="Get path to game exe", command=get_game_path, font=("Arial", 12))
game_path_button.grid(row=1, column=2, columnspan=1)

# Label showing what version of the game is being modded
# This will make mods for newer version not able to be installed and older versions will show error
version_label = Label(main_frame, text=f"Game version not specified, defaulting to: {Game_version}", font=("Arial", 13))
version_label.grid(row=0, column=0, columnspan=2, padx=(0, 10), sticky="w")

version_button = Button(main_frame, text="Game version", command=get_game_version, font=("Arial", 12))
version_button.grid(row=0, column=2, columnspan=2, sticky="w")

# Listbox to display downloaded mods
downloaded_mods_listbox = Listbox(main_frame, font=("Arial", 12), width=50, selectmode="single") # selectmode="multiple"
downloaded_mods_listbox.grid(row=2, column=0, columnspan=3, sticky="ew")

# Add scrollbar
scrollbar = Scrollbar(main_frame, orient="vertical", command=downloaded_mods_listbox.yview)
scrollbar.grid(row=2, column=3, sticky="nsw")
downloaded_mods_listbox.config(yscrollcommand=scrollbar.set)

# Button to install mods
install_mods_button = Button(main_frame, text="Install mods", command=install_mods, font=("Arial", 12)) # Button to install mods
install_mods_button.grid(row=3, column=2, sticky="w")

# Button to play the game without mods
vanilla_play_button = Button(main_frame, text="Play Vanilla", command=lambda: play_game('No'), font=("Arial", 12))
vanilla_play_button.grid(row=3, column=0, sticky="w")

# Button to play the game with mods
Mod_play_button = Button(main_frame, text="Play Modded", command=lambda: play_game('Yes'), font=("Arial", 12))
Mod_play_button.grid(row=3, column=1, sticky="w")

refresh_cache_button = Button(main_frame, text="Refresh cache", command=reset_cache, font=("Arial", 12))
refresh_cache_button.grid(row=2, column=4, sticky="n")

get_the_bibites_button = Button(main_frame, text="Download The Bibites", command=get_the_bibites, font=("Arial", 12))
get_the_bibites_button.grid(row=2, column=4, pady=40, sticky="n")

installed_mod_label = Label(main_frame, text="Installed mod: I do not know what mod is installed", font=("Arial", 12))
installed_mod_label.grid(row=4, column=0, columnspan=3, sticky='n', pady=5)

log_text = Text(main_frame, height=20, width=70, state='disabled', bg='white', fg='black', font=('Consolas', 10))
log_text.grid(row=6, column=0, columnspan=3, padx=5, pady=(5, 0), sticky="nsew")

log_scrollbar = Scrollbar(main_frame, command=log_text.yview)
log_scrollbar.grid(row=6, column=3, sticky='nsw')
log_text.config(yscrollcommand=log_scrollbar.set)

def log(message):
    timestamp = get_time()
    log_text.config(state='normal')
    log_text.insert('end', f"{timestamp} {message}" + '\n')
    log_text.see('end')  # Auto-scroll
    log_text.config(state='disabled')

# Frame that has the list of mods/reskins you can download
downloadable_mods_frame = Frame(window)

# Download mods
download_mods_button = Button(downloadable_mods_frame, text="Download mods", command=download_mods, font=("Arial", 16))
download_mods_button.pack(pady=(10, 20), side="bottom")

more_tools_frame = Frame(window)

# Label that shows the text Einstein
Best_tools_lable = Label(more_tools_frame, font=("Arial", 10, "bold"), wraplength=1000, text="Best tools made for The Bibites")
Best_tools_lable.grid(row=0, column=0, sticky="n")

# Label that shows the text Einstein
Einstein_lable = Label(more_tools_frame, font=("Arial", 18, "bold"), wraplength=1000, text="Einstein\n(discontinued 0.6.1+)")
Einstein_lable.grid(row=1, column=0)

# Label to display a short descriptive text for Einstein brain editor
Einstein_info_lable = Label(more_tools_frame, font=("Arial", 12), wraplength=1000, text="Edit brains by interacting with a diagram of neurons and synapses. Zoom and pan around the diagram, paint neurons different colors, automatically convert brains between bibite versions, view neuron values calculated tick-by-tick and discover other bells and whistles.\nEven though its discontinued its still one of the best tools ever made")
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

# Credits page to show who helped with TBMM
credits_frame = Frame(window)

# Lable that displays the credits
credits_headline_text = "Thanks to all these awesome people for helping"
credits_headline_label = Label(credits_frame, text=credits_headline_text, font=("Arial", 18))
credits_headline_label.pack(anchor="center", pady=5)
credits_label_text = "MOD MAKERS:\nFiveBalesofHay\nMelting Diamond\n\nRESKIN MAKERS:\nmiau\nFiveBalesofHay\n\nTBMM ART:\n\nTBMM icon - miau"
credits_label = Label(credits_frame, text=credits_label_text, font=("Arial", 14))
credits_label.pack(anchor="center", pady=10)

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

class CustomTooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.label = None
        self.visible = False

    def show_tooltip(self, event=None):
        x = event.x_root
        y = event.y_root + 10

        if not self.tooltip_window:
            self.tooltip_window = Toplevel(self.widget)
            self.tooltip_window.wm_overrideredirect(True)

            self.label = Label(
                self.tooltip_window, text=self.text, justify='left',
                background='gainsboro', relief='solid',
                borderwidth=1, wraplength=300
            )
            self.label.pack(ipadx=1)

        self.tooltip_window.geometry(f"+{x}+{y}")
        self.visible = True

    def move_tooltip(self, event):
        if self.tooltip_window:
            x = event.x_root
            y = event.y_root + 10
            self.tooltip_window.geometry(f"+{x}+{y}")

    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
            self.visible = False

current_hover_index = None  # Global variable

def on_hover(event, listbox, tooltips):
    global current_hover_index
    index = listbox.nearest(event.y)
    bbox = listbox.bbox(index)

    if not bbox:
        hide_all_tooltips(tooltips)
        current_hover_index = None
        return

    x, y, width, height = bbox
    buffer_x = 20
    buffer_y = 10

    # Only show/move tooltip if over visible text area
    if (x - buffer_x) <= event.x <= (x + width + buffer_x) and (y - buffer_y) <= event.y <= (y + height + buffer_y):
        if index != current_hover_index:
            hide_all_tooltips(tooltips)
            current_hover_index = index
            if index in tooltips:
                tooltips[index].show_tooltip(event)
        else:
            # Just move the tooltip with the mouse
            if index in tooltips:
                tooltips[index].move_tooltip(event)
    else:
        hide_all_tooltips(tooltips)
        current_hover_index = None

def hide_all_tooltips(tooltips):
    global current_hover_index
    current_hover_index = None
    for tooltip in tooltips.values():
        tooltip.hide_tooltip()

def on_checkbutton_hover(event, widget):
    global current_hover_widget
    tooltip = tooltips.get(widget)

    if current_hover_widget != widget:
        on_checkbutton_leave()  # Hide any existing tooltip
        current_hover_widget = widget

    if tooltip:
        tooltip.show_tooltip(event)

def on_checkbutton_leave():
    global current_hover_widget
    if current_hover_widget:
        tooltip = tooltips.get(current_hover_widget)
        if tooltip:
            tooltip.hide_tooltip()
        current_hover_widget = None

# Dictionary to hold tooltips
tooltips = {}