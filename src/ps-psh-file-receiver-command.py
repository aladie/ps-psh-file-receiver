#!/usr/bin/env python3
import argparse
import os.path
import socket
import re

MAGIC = 0x0000EA6E

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
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        sock.connect((args.ip, args.port))

        # Receive filename
        file = args.folder + sock.recv(128).decode('UTF-8')

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
    except socket.error:
        print('Failed to connect to ' + args.ip + ' on port ' + str(args.port) + '!')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Receive a file over TCP.')
    parser.add_argument('-i', '--ip', required=True, help='The server IP address.')
    parser.add_argument('-p', '--port', type=int, default=9045, help='The server port number.')
    parser.add_argument('-f', '--folder', required=True, help='The target folder.')
    main(parser.parse_args())