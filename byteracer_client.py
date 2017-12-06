"""
Michael Tan
Computer Networks
Professor Anirudh Sivaraman
Assignment 5 - TypeRacer
December 5th, 2017
Client Code
"""
import curses
from curses import wrapper
import time
import os
import random
import socket
import string
import sys

IP = "172.16.178.21"
PORT = 8000

def main(stdscr):
    init_curses(stdscr)

    client = socket.socket( socket.AF_INET, socket.SOCK_STREAM)
    client.connect(( IP, PORT ))
    client.send("txt pls".encode())
    raw_prompt = client.recv(4096).decode()

    # raw_prompt = "more and got sea come story soon other must book stop end under"
    raw_words = raw_prompt.split(" ")
    total_characters = len(raw_prompt)
    character_progress_idx = 0
    word_progress_idx = 0
    curr_word = raw_words[word_progress_idx]
    curr_input = ""
    curr_input_wrong = ""
    try:
        while True:
            c = stdscr.getch()
            if c == 127:
                if len(curr_input_wrong) > 0:
                    curr_input_wrong = curr_input_wrong[:-1]
            elif c >= 0 and c < 127:
                if c == 32:
                    if curr_input == curr_word:
                        character_progress_idx += 1
                        client.send(str(character_progress_idx).encode())
                        word_progress_idx += 1
                        curr_word = raw_words[word_progress_idx]
                        curr_input = ""
                        continue

                if chr(c) != raw_prompt[character_progress_idx] or curr_input_wrong:
                    curr_input_wrong += chr(c)
                else:
                    curr_input += chr(c)
                    character_progress_idx += 1
                    client.send(str(character_progress_idx).encode())
            # Clear out anything else the user has typed in
            # curses.flushinp()
            stdscr.clear()
            stdscr.addstr(raw_prompt)
            stdscr.addstr("\n")
            # stdscr.addstr(" ".join(raw_words[:word_progress_idx]), curses.color_pair(3)) # words completed
            stdscr.addstr(raw_prompt[:character_progress_idx], curses.color_pair(3))
            # stdscr.addstr(curr_input, curses.color_pair(2))
            stdscr.addstr(curr_input_wrong, curses.color_pair(1))
            stdscr.addstr("\nDEBUG\n")
            stdscr.addstr("curr_input: " + curr_input + "\n")
            stdscr.addstr("curr_wrong: " + curr_input_wrong + "\n")
            stdscr.addstr("curr_word: " + curr_word + "\n")
    except KeyboardInterrupt:
        # client.shutdown(1)
        client.close()

def init_curses(stdscr):
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)
    # Make stdscr.getch non-blocking
    stdscr.nodelay(True)
    stdscr.clear()


if __name__ == "__main__":
    wrapper(main)

# import socket
# import string
# import sys
#
# NUM_TRANSMISSIONS=10
# if (len(sys.argv) < 2):
#   print("Usage: python3 " + sys.argv[0] + " server_port")
#   sys.exit(1)
# assert(len(sys.argv) == 2)
# server_port=int(sys.argv[1])
#
# HOST = "localhost"
# server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#
# server.bind((HOST, server_port))
#
# server.listen(NUM_TRANSMISSIONS)
#
# conn, address = server.accept()
#
# # Repeat NUM_TRANSMISSIONS times
# for i in range(NUM_TRANSMISSIONS):
#   data = conn.recv(1024)
#   print("received data " + data.decode() + "; echoed it")
#   conn.send(data)
#
# conn.close()
# server.close()
