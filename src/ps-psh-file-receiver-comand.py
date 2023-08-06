#!/usr/bin/env python3
import argparse
import os.path
import socket
import re

def main(args):
    # Validate folder path
    if not os.path.exists(args.folder):
        print('The folder: ' + args.folder + ' does not exist!')
        return

    # Add '/' if necessary
    if args.folder[len(args.folder) - 1] != '/':
        args.folder += '/'

    # Validate IP address
    if not re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", args.ip):
        print('Invalid IP address!')
        return

    try:
        # Connect to console
        data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        data_sock.settimeout(3)
        data_sock.connect((args.ip, args.port))

        # Receive data_type of send bytes (file/directory/end)
        data_type = data_sock.recv(1).decode('UTF-8')

        current_directory = args.folder

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
                print("Something broke while communicating with the console")

            # Receive data_type of send bytes (file/directory/end)
            data_type = data_sock.recv(1).decode('UTF-8')

        # Close connection
        data_sock.close()

    except socket.error:
        print('Failed to connect to ' + args.ip + ' on port ' + str(args.port) + '!')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Receive a file over TCP.')
    parser.add_argument('-i', '--ip', required=True, help='The server IP address.')
    parser.add_argument('-p', '--port', type=int, default=9046, help='The server port number.')
    parser.add_argument('-f', '--folder', required=True, help='The target folder.')
    main(parser.parse_args())