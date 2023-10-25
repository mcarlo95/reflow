# Import the required libraries
from tkinter import *
from pystray import MenuItem as item
import pystray
from PIL import Image, ImageTk

# Create an instance of tkinter frame or window
win=Tk()
win.title("Reflow importer")

# Set the size of the window
win.geometry("400x350")


# Add a Scrollbar(horizontal)
v=Scrollbar(win, orient='vertical')
v.pack(side=RIGHT, fill='y')

# Add a text widget
text=Text(win, font=("Arial, 8"), yscrollcommand=v.set)

# Add some text in the text widget
##for i in range(10):
##   text.insert(END, "Welcome to Tutorialspoint...\n")
##   text.pack()

# Attach the scrollbar with the text widget
v.config(command=text.yview)
#text.pack()

# Define a function for quit the window
def quit_window(icon, item):
   icon.stop()
   win.destroy()

# Define a function to show the window again
def show_window(icon, item):
   icon.stop()
   win.after(0,win.deiconify())

# Hide the window and show on the system taskbar
def hide_window():
   win.withdraw()
   image=Image.open("etc/favicon.ico")
   menu=(item('Quit', quit_window), item('Show', show_window))
   icon=pystray.Icon("name", image, "Reflow importer running", menu)
   icon.run()

win.protocol('WM_DELETE_WINDOW', hide_window)

win.update_idletasks()
win.update()
##
#win.mainloop()
