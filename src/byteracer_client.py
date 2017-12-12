"""
Michael Tan
Computer Networks
Professor Anirudh Sivaraman
Assignment 5 - TypeRacer
December 5th, 2017
Client Code
"""
import curses
import uuid
import argparse
from curses import wrapper
import time
import os
import random
import socket
import string
import sys
import threading

# TODO: find a way to make text easier to type along with prompt
# TODO: add "ready" feature
# TODO: add "game over" feature with score
# TODO: add "analytics" feature at game over screen

# Command Line Arguments
parser = argparse.ArgumentParser(description='A terminal based networked typeracing game.')
parser.add_argument('--ip', '-ip', action='store', default="localhost", help='IP Address of Server')
parser.add_argument('--port', '-p', action='store', type=int, default=8000, help='Port number of server')
parser.add_argument('--username', '-u', action='store', help='Username of player')

args = parser.parse_args()

# IP field
IP = args.ip
PORT = args.port
if not args.username:
    USERNAME = uuid.uuid4()
else:
    USERNAME = args.username

def listen_worker(client, game):
    # HOST = socket.gethostbyname(socket.gethostname())
    debug = "initializatedded!!!"
    while True:
        game['debug'] = debug
        update = client.recv(1024).decode()
        game['debug'] = "GOT PASSED FIRST BLOCK"
        # game['debug'] += str(update) + "\n"
        if command == "start":
            game['debug'] = "POOP"
            sys.exit()
            game['started'] = True
            continue
        update_split = update.split("|")
        game['debug'] = str(update_split)
        command = update_split[0]
        user = update_split[1]
        count = update_split[2]
        client.send("OK").encode()

def init_countdown(stdscr, game, client):
    while True:
        c = stdscr.getch()
        request = client.recv(1024).decode()
        game['status'] = request
        game['debug'] = request
        if request == "GO!":
            break
        stdscr.clear()
        stdscr.addstr(request)

def main(stdscr):
    init_curses(stdscr)

    client = socket.socket( socket.AF_INET, socket.SOCK_STREAM)
    client.connect(( IP, PORT ))
    init_string = "txt pls|" + USERNAME
    client.send(init_string.encode())
    debug_main = ""
    raw_prompt = client.recv(1024).decode()
    raw_words = raw_prompt.split(" ")
    total_characters = len(raw_prompt)
    character_progress_idx = 0
    word_progress_idx = 0
    curr_word = raw_words[word_progress_idx]
    curr_input = ""
    curr_input_wrong = ""
    game = {}
    game["localhost"] = 0
    game['debug'] = ""
    game['started'] = False
    game['status'] = "Waiting to Players..."

    try:
        while not game['started']:
            # game['debug'] = str(game['started'])
            c = stdscr.getch()
            if c == curses.KEY_ENTER or c == 10 or c == 13: # enter
                if curr_input == "ready":
                    client.send("ready".encode())
                    game['debug'] = "entering while true"
                    init_countdown(stdscr, game, client)
                    game['debug'] = "left while true"
                curr_input = ""
            elif c >= 0 and c < 127:
                curr_input += chr(c)
            stdscr.clear()
            stdscr.addstr("Currently waiting for players...")
            stdscr.addstr("Type 'ready' to ready up!\n")
            stdscr.addstr(curr_input + "\n")
            stdscr.addstr("DEBUG: " + game['debug'] + "\n")
            stdscr.addstr("debug main: " + debug_main + "\n")

        print("game is started!")
        # create worker thread to listen for progress updates from server
        listener_thread = threading.Thread(target=listen_worker, args=(client,game))
        listener_thread.start()
        """
        while True:
            c = stdscr.getch()
            if c == 127: # backspace (on mac)
                if len(curr_input_wrong) > 0:
                    curr_input_wrong = curr_input_wrong[:-1]
            elif c >= 0 and c < 127:
                if c == 32: # space
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
            stdscr.addstr("progress: " + str(progress) + "\n")
            stdscr.addstr("username: " + str(USERNAME))
            """
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
