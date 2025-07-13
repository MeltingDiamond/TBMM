# Anything that gets displayed. For example tkinter 
import webbrowser
from tkinter import Tk, Frame, Label, Button, Listbox, Scrollbar, Text, Toplevel, PhotoImage, StringVar, OptionMenu

# Size of different fonts
status_label_font_size = 14

def open_link(url):
    webbrowser.open_new(url)

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

def on_hover(event, listbox, tooltips, tooltip_state):
    index = listbox.nearest(event.y)
    bbox = listbox.bbox(index)

    if not bbox:
        hide_all_tooltips(tooltips)
        tooltip_state['hover_index'] = None
        return

    x, y, width, height = bbox
    buffer_x = 20
    buffer_y = 10

    if (x - buffer_x) <= event.x <= (x + width + buffer_x) and (y - buffer_y) <= event.y <= (y + height + buffer_y):
        if index != tooltip_state['hover_index']:
            hide_all_tooltips(tooltips)
            tooltip_state['hover_index'] = index
            if index in tooltips:
                tooltips[index].show_tooltip(event)
        else:
            if index in tooltips:
                tooltips[index].move_tooltip(event)
    else:
        hide_all_tooltips(tooltips)
        tooltip_state['hover_index'] = None

def hide_all_tooltips(tooltips):
    global current_hover_index
    current_hover_index = None
    for tooltip in tooltips.values():
        tooltip.hide_tooltip()

def on_checkbutton_hover(event, widget, tooltips, tooltip_state):
    if tooltip_state['hover_widget'] != widget:
        on_checkbutton_leave(tooltips, tooltip_state)
        tooltip_state['hover_widget'] = widget

    tooltip = tooltips.get(widget)
    if tooltip:
        tooltip.show_tooltip(event)

def on_checkbutton_leave(tooltips, tooltip_state):
    widget = tooltip_state.get('hover_widget')
    if widget:
        tooltip = tooltips.get(widget)
        if tooltip:
            tooltip.hide_tooltip()
        tooltip_state['hover_widget'] = None

def create_window(images_folder, version_number, Discord_invite_link, handlers):
    # Create Tkinter window
    window = Tk()
    window.title(f"TBMM {version_number}")

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
    display_downloaded_mods_button = Button(window, text="Main", command=handlers['list_downloaded_mods'], font=("Arial", 12))

    # Button where you find mods to download and install
    find_mods_button = Button(window, text="Get Mods", command=handlers['download_mods_page'], font=("Arial", 12))

    # More tool page where you can find good tools
    more_tools_button = Button(window, text="Community Tools", command=handlers['more_tools_page'], font=("Arial", 12))

    # Button That takes you to the credits page
    credits_button = Button(window, text="Show Credits", command=handlers['credits_page'], font=("Arial", 12))

    Bibite_Research_Conglomerate_hyperlink = Label(window, text="Join Bibite Research Conglomerate Discord Server", fg="blue", cursor="hand2", font=("Arial", 11))
    Bibite_Research_Conglomerate_hyperlink.bind("<Button-1>", lambda e: open_link(Discord_invite_link))

    # Status Label used to show status to the user
    status_label = Label(window, text="", wraplength=750, font=("Arial", status_label_font_size))
    status_label.pack(side="bottom", anchor="s", pady=20, padx=(0, 150))

    return {
        'window': window,
        'screen_width': screen_width,
        'screen_height': screen_height,
        'status_label': status_label,
        'display_downloaded_mods_button': display_downloaded_mods_button,
        'find_mods_button': find_mods_button,
        'more_tools_button': more_tools_button,
        'credits_button': credits_button,
        'Bibite_Research_Conglomerate_hyperlink': Bibite_Research_Conglomerate_hyperlink
    }

def create_main_page_ui(window, handlers):
    # The main page where you view mods
    main_frame = Frame(window)
    main_frame.pack(padx=(140, 20), pady=10)
    main_frame.grid_rowconfigure(6, weight=1)
    main_frame.grid_columnconfigure(2, weight=1)

    # Buttons
    game_path_button = Button(main_frame, text="Get path to game exe", command=handlers['get_game_path'], font=("Arial", 12))
    version_button = Button(main_frame, text="Game version", command=handlers["get_game_version"], font=("Arial", 12))
    install_mods_button = Button(main_frame, text="Install mods", command=handlers["install_mods"], font=("Arial", 12)) # Button to install mods
    vanilla_play_button = Button(main_frame, text="Play Vanilla", command=handlers["play_vanilla"], font=("Arial", 12)) # Button to play the game without mods
    Mod_play_button = Button(main_frame, text="Play Modded", command=handlers["Play Modded"], font=("Arial", 12)) # Button to play the game with mods
    refresh_cache_button = Button(main_frame, text="Refresh cache", command=handlers['reset_cache'], font=("Arial", 12))
    get_the_bibites_button = Button(main_frame, text="Download The Bibites", command=handlers['get_the_bibites'], font=("Arial", 12))
    dowload_new_version_button = Button(main_frame, text="Download new TBMM update", command=handlers['download_new_tbmm_version'], font=("Arial", 12), bg="#0060e6", fg="#003C00")

    # Labels
    game_path_label = Label(main_frame, text="Game path: None", font=("Arial", 14))
    version_label = Label(main_frame, text=f"Game version not specified, defaulting to: {"Game_version"}", font=("Arial", 13)) # Label showing what version of the game is being modded
    installed_mod_label = Label(main_frame, text="Installed mod: I do not know what mod is installed", font=("Arial", 12))

    # Listbox to display downloaded mods
    downloaded_mods_listbox = Listbox(main_frame, font=("Arial", 12), width=50, selectmode="single") # selectmode="multiple"

    # Add scrollbar
    scrollbar = Scrollbar(main_frame, orient="vertical", command=downloaded_mods_listbox.yview)
    downloaded_mods_listbox.config(yscrollcommand=scrollbar.set)
    log_text = Text(main_frame, height=20, width=70, state='disabled', bg='white', fg='black', font=('Consolas', 10))
    log_scrollbar = Scrollbar(main_frame, command=log_text.yview)
    log_text.config(yscrollcommand=log_scrollbar.set)

    # Layout
    game_path_label.grid(row=1, column=0, columnspan=2, padx=(0, 10))
    game_path_button.grid(row=1, column=2, columnspan=1)
    version_label.grid(row=0, column=0, columnspan=2, padx=(0, 10), sticky="w")
    version_button.grid(row=0, column=2, columnspan=2, sticky="w")
    downloaded_mods_listbox.grid(row=2, column=0, columnspan=3, sticky="ew")
    scrollbar.grid(row=2, column=3, sticky="nsw")
    install_mods_button.grid(row=3, column=2, sticky="w")
    vanilla_play_button.grid(row=3, column=0, sticky="w")
    Mod_play_button.grid(row=3, column=1, sticky="w")
    refresh_cache_button.grid(row=2, column=4, sticky="n")
    get_the_bibites_button.grid(row=2, column=4, pady=40, sticky="n")
    installed_mod_label.grid(row=4, column=0, columnspan=3, sticky='n', pady=5)
    log_text.grid(row=6, column=0, columnspan=3, padx=5, pady=(5, 0), sticky="nsew")
    log_scrollbar.grid(row=6, column=3, sticky='nsw')

    return {
        'frame': main_frame,
        'game_path_label': game_path_label,
        'version_label': version_label,
        'downloaded_mods_listbox': downloaded_mods_listbox,
        'installed_mod_label': installed_mod_label,
        'log_text': log_text,
        'dowload_new_version_button': dowload_new_version_button
    }

def create_download_mods_page_ui(window, handlers):
    # Frame that has the list of mods/reskins you can download
    downloadable_mods_frame = Frame(window)

    # Buttons
    download_mods_button = Button(downloadable_mods_frame, text="Download mods", command=handlers['download_mods'], font=("Arial", 16))

    # Layout
    download_mods_button.pack(pady=(10, 20), side="bottom")

    return {
        'frame': downloadable_mods_frame
    }

def create_credits_page_ui(window):
    # Credits page to show who helped with TBMM
    credits_frame = Frame(window)

    # Label
    credits_headline_text = "Thanks to all these awesome people for helping"
    credits_headline_label = Label(credits_frame, text=credits_headline_text, font=("Arial", 18))
    credits_label_text = "MOD MAKERS:\nFiveBalesofHay\nMelting Diamond\n\nRESKIN MAKERS:\nmiau\nFiveBalesofHay\n\nTBMM ART:\n\nTBMM icon - miau"
    credits_label = Label(credits_frame, text=credits_label_text, font=("Arial", 14))
    
    # Layout
    credits_headline_label.pack(anchor="center", pady=5)
    credits_label.pack(anchor="center", pady=10)

    return {
        'frame': credits_frame
    }

def create_more_tools_page_ui(window, images_folder):
    more_tools_frame = Frame(window)

    # Label
    Best_tools_lable = Label(more_tools_frame, font=("Arial", 10, "bold"), wraplength=1000, text="Best tools made for The Bibites")
    Einstein_lable = Label(more_tools_frame, font=("Arial", 18, "bold"), wraplength=1000, text="Einstein\n(discontinued 0.6.1+)")
    Einstein_info_lable = Label(more_tools_frame, font=("Arial", 12), wraplength=1000, text="Edit brains by interacting with a diagram of neurons and synapses. Zoom and pan around the diagram, paint neurons different colors, automatically convert brains between bibite versions, view neuron values calculated tick-by-tick and discover other bells and whistles.\nEven though its discontinued its still one of the best tools ever made")
    Einstein_hyperlink = Label(more_tools_frame, text="Download Einstein", fg="blue", cursor="hand2", font=("Arial", 12))
    Einstein_hyperlink.bind("<Button-1>", lambda e: open_link("https://github.com/quaris628/EinsteinEditor/releases/latest"))
    Einstein_image = PhotoImage(file=f"{images_folder}/Einstein_Review.png")
    Einstein_image_label = Label(more_tools_frame, image = Einstein_image)

    # Layout
    Best_tools_lable.grid(row=0, column=0, sticky="n")
    Einstein_lable.grid(row=1, column=0)
    Einstein_info_lable.grid(row=2, column=0)
    Einstein_hyperlink.grid(row=3, column=0)
    Einstein_image_label.grid(row=4, column=0, pady=5)

    return {
        'frame': more_tools_frame,
        'Einstein_info_lable': Einstein_info_lable
    }

def create_game_version_page_ui(window, handlers):
    Game_version = handlers['Game_version']
    width_height = f"{int(handlers['screen_width'] / 4)}x{int(handlers['screen_height'] / 3)}"

    game_version_window = Toplevel(window)
    game_version_window.title("Choose Game Version")
    game_version_window.geometry(width_height)
    game_version_window.resizable(False, False)

    game_version_frame = Frame(game_version_window)
    game_version_frame.pack(pady=20)

    label = Label(game_version_frame, text="Please choose the game version:", font=("Arial", 14))
    label.pack(pady=10)

    list_of_mod_versions = ["All"] + handlers['list_of_versions']
    selected_version = StringVar(value=Game_version if Game_version in list_of_mod_versions else list_of_mod_versions[0])
    version_dropdown = OptionMenu(game_version_frame, selected_version, *list_of_mod_versions)
    version_dropdown.pack(pady=10)

    Label(game_version_frame, text="If you can't find a version,\nit is because there are no mods for it,\n choose all to show all mods", font=("Arial", 10)).pack(pady=10)

    confirm_button = Button(game_version_frame, text="Confirm")  # No command here
    confirm_button.pack(pady=10)

    game_version_window.grab_set()  # Block input to main window until closed

    return {
        'window': game_version_window,
        'selected_version': selected_version,
        'confirm_button': confirm_button
    }