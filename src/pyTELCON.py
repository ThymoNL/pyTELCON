#!/usr/bin/env python3
'''
A telemetry program for NASSP

Copyright (C) 2020 Thymo van Beers

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or (at
your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
USA.
'''

import sys
import argparse
import socket
from enum import Enum


class TelemetryLock(Enum):
	SYNC0		= 0
	SYNC1		= 1
	SYNC2		= 2
	LBRSYNC1	= 3
	LBRSYNC2	= 4
	LBRSYNC3	= 5
	HBRSYNC1	= 6
	HBRSYNC2	= 7
	HBRSYNC3	= 8
	LBR			= 9
	HBR			= 10


class TelemetryReader:
	sock = None
	lock = TelemetryLock.SYNC0
	wordc = 0

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
			print("Stopping dump")

	def sync(self):
		try:
			while True:
				data = self.sock.recv(1024)
				if len(data) == 0:
					break

				for word in data:
					if self.lock == TelemetryLock.SYNC0:
						if word == 0o5:
							print("SYNC0")
							self.lock = TelemetryLock.SYNC1
					elif self.lock == TelemetryLock.SYNC1:
						if word == 0o171:
							print("SYNC1")
							self.lock = TelemetryLock.SYNC2
						else:
							self.lock = TelemetryLock.SYNC0
					elif self.lock == TelemetryLock.SYNC2:
						if word == 0o267:
							print("SYNC2")
							self.lock = TelemetryLock.LBRSYNC1
							wordc = 3
						else:
							self.lock = TelemetryLock.SYNC0
					elif self.lock == TelemetryLock.LBRSYNC1:
						if wordc == 40:
							if word == 0o5:
								print("LBRSYNC1")
								self.lock = TelemetryLock.LBRSYNC2
							else:
								print("Possbile HBR during LBRSYNC1. Restart.")
								self.lock = TelemetryLock.SYNC0
						elif wordc > 100: # Lost lock, start over
							print("Lost during LBRSYNC1")
							self.lock = TelemetryLock.SYNC0
						wordc += 1
					elif self.lock == TelemetryLock.LBRSYNC2:
						if word == 0o171:
							print("LBRSYNC2")
							self.lock = TelemetryLock.LBRSYNC3
						else:
							print("Possible HBR during LBRSYNC2. Restart.")
							self.lock = TelemetryLock.SYNC0
						wordc += 1
					elif self.lock == TelemetryLock.LBRSYNC3:
						if word == 0o267:
							print("LBRSYNC3")
							self.lock = TelemetryLock.LBR # Locked
							wordc = 3
							print("Locked on LBR")
						else:
							print("Possible HBR during LBRSYNC3. Restart.")
							self.lock = TelemetryLock.SYNC0
						wordc += 1
					elif self.lock == TelemetryLock.LBR:
						#TODO: Parse data
						wordc += 1
						if wordc > 39:
							wordc = 0
							print("Next frame")

		except KeyboardInterrupt:
			print("Stopping sync")

	def close(self):
		self.sock.close()


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="Monitor NASSP telemetry stream.")
	parser.add_argument("-i", "--host", dest='host', default='127.0.0.1')
	parser.add_argument("-p", "--port", dest='port', default='14242', type=int)
	args = parser.parse_args()

	print("Connecting to {0}:{1}".format(args.host, args.port))
	try:
		reader = TelemetryReader(args.host, args.port)
		reader.sync()
	except KeyboardInterrupt:
		reader.close()

