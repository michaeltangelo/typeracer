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
import math
import select
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

class Game:
    start_time = 0
    prompt = ""
    player_progress = 0
    error_progress = 0
    all_progress = {}
    readyUp = False
    started = 0
    wpm = 0
    def __init__(self):
        pass

    def generate_stats(self):
        stats_str = ""
        for player in self.all_progress:
            stats_str += player + " - " + self.all_progress[player] + "%\n"
        return stats_str

game = Game()

def init_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((IP, PORT))
    client.setblocking(0)
    init_string = "txt pls|" + USERNAME
    client.send(init_string.encode())
    return client

def calc_wpm():
    game.wpm = math.ceil((game.player_progress/5) / ((time.time() - game.start_time) / 60))
    return game.wpm

def main(stdscr):
    init_curses(stdscr)

    curr_input = ""
    curr_input_wrong = ""
    debug = ""
    try:
        client = init_client()

        inputs = [sys.stdin, client]
        outputs = []
        message_queues = {}

        display = "Waiting for players... type 'ready' to ready up!"
        wpm = ""
        running = True

        while True:
            if game.started == 0: # LOBBY
                c = stdscr.getch()
                if c == curses.KEY_BACKSPACE or c == 127: # backspace
                    if len(curr_input) > 0:
                        curr_input = curr_input[:-1]
                if c == curses.KEY_ENTER or c == 10 or c == 13: # enter
                    if not game.readyUp:
                        if curr_input == "ready":
                            client.send("ready".encode())
                            game.readyUp = True
                        curr_input = ""
                    else:
                        client.send(curr_input.encode())
                        curr_input = ""
                elif c >= 0 and c < 127:
                    curr_input += chr(c)
                stdscr.clear()
                stdscr.addstr(display)
                stdscr.addstr("\n"+curr_input)
                stdscr.addstr("\nDebug: " + debug)
                while client in select.select([client], [], [], 0)[0]: # the server has sent us a message
                    request = client.recv(1024).decode()
                    request_split = request.split("|")
                    if request_split[0] == "prompt":
                        game.prompt = request_split[1]
                    elif request == "Starting game in 3!":
                        game.started = 1
                        display = "Starting game in 3!"
                    else:
                        display = request
                    debug += "\n" + request

            elif game.started == 1: # COUNTDOWN
                c = stdscr.getch()
                stdscr.clear()
                stdscr.addstr(display)
                while client in select.select([client], [], [], 0)[0]: # the server has sent us a message
                    request = client.recv(1024).decode()
                    display = request
                    if request == "GO!":
                        game.started = 2
                        game.start_time = time.time()
                    debug += "\n" + request

            elif game.started == 2: # LIVE
                wpm = calc_wpm()
                c = stdscr.getch()
                if c == curses.KEY_BACKSPACE or c == 127: # backspace
                    if game.error_progress > 1:
                        game.error_progress -= 1
                    elif game.error_progress == 1:
                        if game.prompt[game.player_progress + game.error_progress] == " ": # handles backspacing a space
                            game.error_progress -= 1
                            game.player_progress += 1
                        else:
                            game.error_progress -= 1
                if c == curses.KEY_ENTER or c == 10 or c == 13: # enter
                    pass
                elif c >= 0 and c < 127:
                    if game.error_progress == 0 and chr(c) == game.prompt[game.player_progress]:
                        game.player_progress += 1
                        if game.player_progress == len(game.prompt):
                            client.send("done".encode())
                            game.started = 3
                        else:
                            client.send(str(game.player_progress).encode())
                    else:
                        game.error_progress += 1
                stdscr.clear()

                correct = game.prompt[:game.player_progress]
                wrong = game.prompt[game.player_progress:game.player_progress + game.error_progress]
                regular = game.prompt[game.player_progress + game.error_progress:]

                stdscr.addstr(correct, curses.color_pair(3))
                stdscr.addstr(wrong, curses.color_pair(1))
                stdscr.addstr(regular)

                stdscr.addstr("\nWPM: " + str(wpm) + "\n")
                stdscr.addstr(game.generate_stats())
                stdscr.addstr("\n\n\n\nDebug: " + debug)
                stdscr.addstr("\nPlayer progress: " + str(game.player_progress))
                stdscr.addstr("\nError progress: " + str(game.error_progress))

                while client in select.select([client], [], [], 0)[0]: # the server has sent us a message
                    request = client.recv(1024).decode()
                    debug = "\n" + request + "\n" + str(game.all_progress)
                    request_split = request.split(":")
                    if request_split[0] == "progress":
                        players_split = request_split[1].split("|")
                        for player in players_split:
                            if not player:
                                continue
                            player_split = player.split("//")
                            username = player_split[0]
                            progress = player_split[1]
                            game.all_progress[username] = progress


            elif game.started == 3: # POST-GAME
                c = stdscr.getch()
                stdscr.clear()
                stdscr.addstr("Wow! 99.99% of people fail this test. You're exceptional! Your WPM is: " + str(game.wpm))
                pass

    except KeyboardInterrupt:
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
