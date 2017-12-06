"""
Michael Tan
Computer Networks
Professor Anirudh Sivaraman
Assignment 1 - Part 8
September 30, 2017
Server Code
"""

import socket
import string
import sys

NUM_TRANSMISSIONS=10
if (len(sys.argv) < 2):
  print("Usage: python3 " + sys.argv[0] + " server_port")
  sys.exit(1)
assert(len(sys.argv) == 2)
server_port=int(sys.argv[1])

HOST = "localhost"
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((HOST, server_port))

server.listen(NUM_TRANSMISSIONS)

conn, address = server.accept()

# Repeat NUM_TRANSMISSIONS times
for i in range(NUM_TRANSMISSIONS):
  data = conn.recv(1024)
  print("received data " + data.decode() + "; echoed it")
  conn.send(data)

conn.close()
server.close()
