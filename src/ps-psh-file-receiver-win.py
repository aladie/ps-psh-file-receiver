import json
import os
import re
import socket
import sys
import tkinter as tk
from tkinter import filedialog as fd
from tkinter import messagebox as mb

MAGIC = 0x0000EA6E
PORT = 9045

def getCurrentDirectory():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(__file__)

def choosedirectory():
    directory = fd.askdirectory()

    # Check if location is not emtpy
    if os.path.exists(directory):
        choose_folder_box.delete(0, tk.END)
        choose_folder_box.insert(0, directory + "/")
    else:
        mb.showerror("Error", "Invalid folder location!")

def recievefile():
    # Disable button while downloading
    recievefile_button.config(state="disabled")

    # Get chosen target directory
    directory = choose_folder_box.get()

    # Validate directory
    if not os.path.exists(directory):
        mb.showerror("Error", "Invalid folder location!")
        recievefile_button.config(state="normal")
        return

    # Validate IP address
    ip = enter_ip.get()
    if not re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip):
        mb.showerror("Error", "Invalid IP address!")
        recievefile_button.config(state="normal")
        return

    try:
        # Connect to console
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        sock.connect((ip, PORT))

        # Receive filename
        file = directory + sock.recv(128).decode('UTF-8')

        # Download file in chunks
        with open(file, 'wb') as f:
            while True:
                data = sock.recv(4096)

                if data == b'':
                    f.close()
                    break

                f.write(data)

        # Close connection
        sock.close()

        # Save values to config
        with open(os.path.join(getCurrentDirectory(), 'ps-psh-file-receiver.json'), 'w') as f:
            f.write(json.dumps({
                'ip': ip,
                'folder': choose_folder_box.get(),
            }, indent=4))

        mb.showinfo("Success", "Successfully received file from PS4/PS5!")

        # Re-enable button after download finished
        recievefile_button.config(state="normal")
    except socket.error:
        mb.showerror("Error", "Failed to connect!")
        recievefile_button.config(state="normal")

if __name__ == "__main__":
    window = tk.Tk()

    window.geometry("380x125")
    window.resizable(False, False)

    window.title("PS-PSH File Receiver v0.1.1")

    choose_folder_box = tk.Entry(window, width=42)
    choose_folder = tk.Button(window, text="Select Folder", command=choosedirectory)

    enter_ip_label = tk.Label(window, text="Enter IP-Address of your PS4/PS5:")
    enter_ip = tk.Entry(window, width=27)

    recievefile_button = tk.Button(window, text="Receive File from PS4/PS5", width=49, command=recievefile)

    # Load config
    try:
        with open(os.path.join(getCurrentDirectory(), 'ps-psh-file-receiver.json')) as f:
            config = json.load(f)
            if 'ip' in config:
                enter_ip.insert(0, config['ip'])
            if 'folder' in config:
                choose_folder_box.insert(0, config['folder'])
    except:
        config = {}

    choose_folder_box.place(x=10, y=12)
    choose_folder.place(x=285, y=8)

    enter_ip_label.place(x=10, y=50)
    enter_ip.place(x=200, y=50)

    recievefile_button.place(x=10, y=90)

    window.mainloop()
