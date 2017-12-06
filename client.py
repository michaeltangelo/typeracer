"""
Michael Tan
Computer Networks
Professor Anirudh Sivaraman
Assignment 1 - Part 8
September 30, 2017
Client Code
"""

import os
import random
import socket
import string
import sys

# Random alphanumeric string of length l
def rand_str(l):
  ret = ''
  for i in range(l):
    ret += random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits)
  return ret

NUM_TRANSMISSIONS=10
if (len(sys.argv) < 2):
  print("Usage: python3 "  + sys.argv[0] + " server_port")
  sys.exit(1)
assert(len(sys.argv) == 2)
server_port=int(sys.argv[1])

HOST = "localhost"
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect((HOST, server_port))

# Transmit NUM_TRANSMISSIONS number of times
for i in range(NUM_TRANSMISSIONS):
  # Generate a random string
  data=rand_str(10)

  client.send(data.encode())

  # Print data for debugging
  print("sent: " + data)

  data = client.recv(1024)

  # Print received data for debugging
  print("received echo: " + data.decode())
  print()

client.close()
