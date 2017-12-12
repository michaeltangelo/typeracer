"""
Michael Tan
Computer Networks
Professor Anirudh Sivaraman
Assignment 5 - TypeRacer
December 5th, 2017
Server Code
"""
from datetime import datetime
import argparse
from time import time
import socket
import select
import string
import sys
import threading
import random
from multiprocessing import Queue

# TODO add support for arguments (prod/debug, port, num_clients, num_words)
# TODO username
# TODO implement "ready" feature for when all clients connect
# TODO implement timer (server side) to track winner

# Command Line Arguments
parser = argparse.ArgumentParser(description='A terminal based networked typeracing game.')
parser.add_argument('--debug', '-d', action='store_true', default=False, help='Displays debug text for development')
parser.add_argument('--ip', '-ip', action='store', default="localhost", help='IP address for server')
parser.add_argument('--port', '-p', action='store', type=int, default=8000, help='Port number for server')
parser.add_argument('--num_clients', '-c', action='store', type=int, default=5, help='Number of clients to support')
parser.add_argument('--num_words', '-w', action='store', type=int, default=50, help='How many random words to generate for the game')

args = parser.parse_args()

print(args)

# IP field
if args.debug:
    IP = "localhost"
else:
    try:
        IP = socket.gethostbyname(socket.gethostname())
    except:
        IP = "localhost"

if args.ip:
    IP = args.ip

PORT = args.port
NUM_CLIENTS = args.num_clients
NUM_WORDS = args.num_words

class Game:
    startTime = 0
    players = []
    startTime = 0
    prompt = ""
    promptLength = 0
    numPlayers = 0
    numReady = 0
    started = 0
    winner = ""

    def __init__(self):
        # generate prompt
        file_object  = open("words.txt", "r")
        all_text = file_object.read()
        words = all_text.split(",")
        prompt = []
        for i in range(NUM_WORDS):
            prompt.append(random.choice(words))
        self.prompt = " ".join(prompt)
        self.promptLength = len(self.prompt)

    def get_player_by_peer_name(self, peer_name):
        for player in self.players:
            if player.peer_name == peer_name:
                return player

    def add_player(self, player):
        self.players.append(player)
        self.numPlayers += 1

    def message_all_clients(self, message):
        for player in self.players:
            player.socket.send(message.encode())

    def start(self):
        start_time = time()
        self.startTime = start_time
        curr_time = time()
        countdown = 3
        sent_3 = False
        sent_2 = False
        sent_1 = False
        while curr_time - start_time < 3:
            the_time = curr_time - start_time
            if the_time < 1 and not sent_3:
                self.message_all_clients("Starting game in 3!")
                print("Starting game in 3!")
                sent_3 = True
            elif the_time > 1 and the_time < 2 and not sent_2:
                self.message_all_clients("Starting game in 2!")
                print("Starting game in 2!")
                sent_2 = True
            elif the_time > 2 and the_time < 3 and not sent_1:
                self.message_all_clients("Starting game in 1!")
                print("Starting game in 1!")
                sent_1 = True
            curr_time = time()
        self.message_all_clients("GO!")
        game.started = 1

    def ready_up(self, player):
        player.ready = True
        self.numReady += 1

    def generate_progress_str(self):
        progress_str = "progress:"
        for player in self.players:
            percent = "%.2f" % ((player.curr_progress / self.promptLength) * 100)
            progress_str += player.username + "//"+percent+"|"
        return progress_str

class Player:
    curr_progress = 0
    ready = False
    addr = 0
    socket = None
    peer_name = ""
    username = ""

    def __init__(self, socket, addr, peer_name, username):
        self.username = username
        self.peer_name = peer_name
        self.socket = socket
        self.addr = addr

    def update_progress(self, progress):
        self.curr_progress = progress

game = Game()

def handle_request(request, conn_sock, addr, peer_name):
    request_split = request.split("|")
    if request_split[0] == "txt pls":
        print("Got a new user. Setting user up")
        username = request_split[1]
        new_player = Player(conn_sock, addr, peer_name, username)
        game.add_player(new_player)
        response = "prompt|" + game.prompt
        return response
    elif request == "ready":
        player = game.get_player_by_peer_name(peer_name)
        game.ready_up(player)
        if game.numReady >= game.numPlayers:
            game.start()
        else:
            response = "Waiting for players... " + str(game.numReady) + "/" + str(game.numPlayers) + " players are ready."
            game.message_all_clients(response)
            return ""
    elif request.isdigit():
        player = game.get_player_by_peer_name(peer_name)
        player.update_progress(int(request))
        percent = "%.2f" % ((player.curr_progress / game.promptLength) * 100)
        print("Player (", player.username, ") is now at:", percent)
        game.message_all_clients(game.generate_progress_str())
    elif request == "done":
        game.winner = game.get_player_by_peer_name(peer_name)
    else:
        print("Server unable to handle request: " + request)


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setblocking(0)
    server.bind((IP, PORT))
    server.listen(NUM_CLIENTS) # supports 5 concurrent hosts

    print ("[*] Listening on %s:%d" % (IP, PORT))

    inputs = [server]
    outputs = []
    message_queues = {}

    while inputs:
        # Wait for at least one of the sockets to be ready for processing
        readable, writable, exceptional = select.select(inputs, outputs, inputs)

        # Handle inputs
        for s in readable:
            if s is server:
                # A "readable" server socket is ready to accept a connection
                connection, addr = s.accept()
                print ("[*] Accepted connection from: %s:%d" %(addr[0], addr[1]))
                connection.setblocking(0)
                inputs.append(connection)

                # Give the connection a queue for data we want to send
                message_queues[connection] = Queue()

            else: # client
                request = s.recv(1024).decode()
                if request:
                    # A readable client socket has data
                    print('received "%s" from %s' % (request, s.getpeername()))
                    response = handle_request(request, connection, addr, s.getpeername())
                    if response:
                        s.send(response.encode())
                        print("Responding with: " + str(response))

                    message_queues[s].put(request)
                    # Add output channel for response
                    if s not in outputs:
                        outputs.append(s)
                else:
                    # Interpret empty result as closed connection
                    print("Closing", addr, "after receiving empty data")
                    # Stop listening for input on the connection
                    if s in outputs:
                        outputs.remove(s)
                    inputs.remove(s)
                    s.close()

                    # Remove message queue
                    del message_queues[s]

if __name__ == '__main__':
    main()
