import kivy
kivy.require('2.3.1')
 
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout

class TBMMKivyApp(App):
    def __init__(self, handlers, version_number, **kwargs):
        super().__init__(**kwargs)
        self.handlers = handlers
        self.version_number = version_number
        self.refs = {}  # To store widget references

    def build(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        title_label = Label(text=f"TBMM {self.version_number}", font_size='24sp')
        display_downloaded_mods_button = Button(text="Main", on_press=self.handlers['list_downloaded_mods'])
        find_mods_button = Button(text="Get Mods", on_press=self.handlers['download_mods_page'])
        more_tools_button = Button(text="Community Tools", on_press=self.handlers['more_tools_page'])
        credits_button = Button(text="Credits", on_press=self.handlers['credits_page'])

        # Save references like in Tkinter version
        self.refs['title_label'] = title_label
        self.refs['display_downloaded_mods_button'] = display_downloaded_mods_button
        self.refs['find_mods_button'] = find_mods_button
        self.refs['more_tools_button'] = more_tools_button
        self.refs['credits_button'] = credits_button

        layout.add_widget(title_label)
        layout.add_widget(display_downloaded_mods_button)
        layout.add_widget(find_mods_button)
        layout.add_widget(more_tools_button)
        layout.add_widget(credits_button)

        return layout


def create_windowd():
    # Create Tkinter window
    class HelloKivy(App):
        def build(self):
            return Label(text ="Hello Geeks")

    window = Tk()
    window.title(f"TBMM {version_number}")

    # Convert the image into a format tkinter understands (Different for Windows and Linux/Mac)
    image = Image.open(f"{images_folder}/TBMM icon.ico")
    app_image = ImageTk.PhotoImage(image)
    if OS_TYPE == "Windows":
        window.iconbitmap(app_image)
    elif OS_TYPE == "Linux" or OS_TYPE == "Mac":
        window.iconphoto(True, app_image)

    # Get screen width and height
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Set window size and position to fullscreen windowed
    window_width = int(screen_width * 0.8)
    window_height = int(screen_height * 0.8)
    window.geometry(f"{window_width}x{window_height}+{int((screen_width - window_width) / 2)}+{int((screen_height - window_height) / 2)}")

    window.minsize(1000, 550)

    # Title label
    title_label = Label(text ="Label is Added on screen !!:):)", font=("Arial", 24, "bold")) #Label(window, text=localization["The-Bibites-Mod-Manager"], font=("Arial", 24, "bold"))
    title_label.pack(pady=(20, 10))

    # Button to display downloaded mods (main page)
    display_downloaded_mods_button = Button(window, text=localization["Capital-Main"], command=handlers['list_downloaded_mods'], font=("Arial", 12))

    # Button where you find mods to download and install
    find_mods_button = Button(window, text=localization["Get-Mods"], command=handlers['download_mods_page'], font=("Arial", 12))

    # More tool page where you can find good tools
    more_tools_button = Button(window, text=localization["Community-Tools"], command=handlers['more_tools_page'], font=("Arial", 12))

    # Button That takes you to the credits page
    credits_button = Button(window, text=localization["Show-Credits"], command=handlers['credits_page'], font=("Arial", 12))

    Bibite_Research_Conglomerate_hyperlink = Label(window, text=localization["Join-BRC"], fg="blue", cursor="hand2", font=("Arial", 11))
    Bibite_Research_Conglomerate_hyperlink.bind("<Button-1>", handlers['open_link'])

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
