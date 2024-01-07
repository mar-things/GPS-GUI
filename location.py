from tkinter import *
import tkinter as tk
import tkintermapview
import customtkinter as ctk

root = Tk()
root.title('User gui Map')
root.geometry("900x700")

my_label = LabelFrame(root)
my_label.pack(pady=20)

map_widget = tkintermapview.TkinterMapView(my_label,width=800, height=600,corner_radius= 1)
# Create buttons
start_button = ctk.CTkButton(master = root, text="Start")
stop_button = tk.Button(root, text="Stop")
save_button = tk.Button(root, text="Save")
open_button = tk.Button(root, text="Open")

'''
start_button.grid(row=1, column=0, padx=10, pady=10)
stop_button.grid(row=1, column=1, padx=10, pady=10)
save_button.grid(row=1, column=2, padx=10, pady=10)
open_button.grid(row=1, column=3, padx=10, pady=10)
'''
#Setting Coordinates
map_widget.set_position(54.898521, 23.903597,marker=True)
map_widget.set_zoom(13)
map_widget.pack()
root.mainloop()
