#!/usr/bin/env python3
'''
A telemetry program for NASSP
'''

import sys
import argparse
import socket


class TelemetryReader:
    sock = None

    def __init__(self, host, port):
        self.sock = socket.socket()
        self.sock.connect((host, port))

    def dump(self):
        try:
            while True:
                data = self.sock.recv(1024)
                if len(data) == 0:
                    break

                print(data)

        except KeyboardInterrupt:
            pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Monitor NASSP telemetry stream.")
    parser.add_argument("-i", "--host", dest='host', default='127.0.0.1')
    parser.add_argument("-p", "--port", dest='port', default='14242', type=int)
    args = parser.parse_args()

    print("Connecting to {0}:{1}".format(args.host, args.port))
    try:
        reader = TelemetryReader(args.host, args.port)
        reader.dump()
        print("Shutting down")
    except KeyboardInterrupt:
        pass # Close

