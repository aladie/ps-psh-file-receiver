import json
import os
import re
import socket
import sys
import tkinter as tk
from tkinter import filedialog as fd
from tkinter import messagebox as mb

DATA_PORT = 9046

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
    origin_directory = choose_folder_box.get()

    # Validate directory
    if not os.path.exists(origin_directory):
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
        data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        data_sock.settimeout(3)
        data_sock.connect((ip, DATA_PORT))

        # Receive data_type of send bytes (file/directory/end)
        data_type = data_sock.recv(1).decode('UTF-8')

        current_directory = origin_directory

        # Keep receiving until exit command was received
        while data_type != 'e':

            if data_type == 'd':
                # Receive directory name and create new directory
                temp_dir = data_sock.recv(128).decode('UTF-8')
                new_directory = current_directory

                for i in range(0, 128):
                    if temp_dir[i] == '/':
                        new_directory += '/'
                        break

                    new_directory += temp_dir[i]

                # Notify console that the new directory was created successfully
                data_sock.sendall(b'D_OK')

                try:
                    os.makedirs(new_directory)
                except FileExistsError:
                    print("Folder already exists!")

                current_directory = new_directory
            elif data_type == 'r':
                # Go up in the directory tree
                current_directory = current_directory[0:current_directory.rfind('/')]
                current_directory = current_directory[0:current_directory.rfind('/') + 1]

            elif data_type == 'f':
                # Receive infos
                temp_info = data_sock.recv(20).decode('UTF-8')
                temp_length = ''

                for i in range(0, 20):
                    if temp_info[i] == 'R':
                        break

                    temp_length += str(int(temp_info[i]))

                filename_length = int(temp_length)

                # Receive filename
                filename = data_sock.recv(filename_length).decode('UTF-8')

                file = current_directory + filename

                # Notify console of successfull filename transfer
                data_sock.sendall(b'F_OK')

                # Download file in chunks
                with open(file, 'wb') as f:
                    while True:
                        # VERY EXPERIMENTAL WAY OF CLOSING THE FILE!!
                        try:
                            data = data_sock.recv(4096)
                        except socket.timeout:
                            f.close()
                            break

                        f.write(data)

                # Notify console of possible successfull file transfer
                data_sock.sendall(b'R_OK')
            else:
                mb.showerror("Error", "Something broke while communicating with the console")

            # Receive data_type of send bytes (file/directory/end)
            data_type = data_sock.recv(1).decode('UTF-8')

        # Close connection
        data_sock.close()

        # Save values to config
        with open(os.path.join(getCurrentDirectory(), 'ps-psh-file-receiver.json'), 'w') as f:
            f.write(json.dumps({
                'ip': ip,
                'folder': choose_folder_box.get(),
            }, indent=4))

        mb.showinfo("Success", "Successfully received file from PS4/PS5!")

        # Re-enable button after download finished
        recievefile_button.config(state="normal")

    except socket.timeout:
        mb.showerror("Error", "Timeout")
    except socket.error:
        mb.showerror("Error", "Failed to connect!")
        recievefile_button.config(state="normal")


if __name__ == "__main__":
    window = tk.Tk()

    # Remove menu bar on top
    window.config(menu=tk.Menu(window))

    window.geometry("500x140")
    window.resizable(False, False)

    window.title("PS-PSH File Receiver")

    choose_folder_box = tk.Entry(window, width=38)
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

    choose_folder_box.place(x=10, y=10)
    choose_folder.place(x=370, y=8)

    enter_ip_label.place(x=10, y=50)
    enter_ip.place(x=230, y=48)

    recievefile_button.place(x=10, y=90)

    window.mainloop()
