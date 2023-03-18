#!/usr/bin/env python3
import argparse
import socket

MAGIC = 0x0000EA6E

def main(args):
    # Connect to console
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)
    sock.connect((args.ip, args.port))

    # Download file in chunks
    with open(args.folder + "PS-PSH-OUTPUT", 'wb') as f:
        while True:
            data = sock.recv(4096)

            if data == b'':
                f.close()
                break

            f.write(data)

    # Close connection
    sock.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Receive a file over TCP.')
    parser.add_argument('-i', '--ip', required=True, help='The server IP address.')
    parser.add_argument('-p', '--port', type=int, default=9045, help='The server port number.')
    parser.add_argument('-f', '--folder', required=True, help='The target folder.')
    main(parser.parse_args())