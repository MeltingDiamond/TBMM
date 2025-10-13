from tkinter import *

# Create Tkinter window
window = Tk()
window.title(f"TBMM Minimal Build")

# Get screen width and height
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

# Set window size and position to fullscreen windowed
window_width = int(screen_width * 0.8)
window_height = int(screen_height * 0.8)
window.geometry(f"{window_width}x{window_height}+{int((screen_width - window_width) / 2)}+{int((screen_height - window_height) / 2)}")

window.minsize(1000, 550)

# Title label
title_label = Label(window, text="The Bibites Mod Manager Minimal Build", font=("Arial", 24, "bold"))
title_label.pack(pady=(20, 10))

window.mainloop()