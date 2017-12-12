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
import string
import sys
import threading
import random

# TODO add support for arguments (prod/debug, port, num_clients, num_words)
# TODO username
# TODO implement "ready" feature for when all clients connect
# TODO implement timer (server side) to track winner
# TODO start two threads per connection, one for client receive and one for client send

# Command Line Arguments
parser = argparse.ArgumentParser(description='A terminal based networked typeracing game.')
parser.add_argument('--debug', '-d', action='store_true', default=False, help='Displays debug text for development')
parser.add_argument('--port', '-p', action='store', type=int, default=8000, help='Port number for server')
parser.add_argument('--num_clients', '-c', action='store', type=int, default=5, help='Number of clients to support')
parser.add_argument('--num_words', '-w', action='store', type=int, default=50, help='How many random words to generate for the game')

args = parser.parse_args()

print(args)

# IP field
if args.debug:
    IP = "localhost"
else:
    IP = socket.gethostbyname(socket.gethostname())

PORT = args.port
NUM_CLIENTS = args.num_clients
NUM_WORDS = args.num_words

def send_progress(game):
    while True:
        progress = gen_progress_string(game)

def update_thread(game):
    while True:
        if game['numReady'] >= game['numUsers']:
            print("setting game started to 2")
            print("WE HE")
            game['started'] = 2
        # for user in game['users'].keys():
        #     socket = game['users'][user]['socket']


def handle_client(client_socket, addr, game):
    try:
        while True:
            if game['started'] == 0:
                print("Blocked waiting for recv")
                raw_request = client_socket.recv(1024)
                request = raw_request.decode()
                print("Server received: " + str(request) + " from " + str(addr))
                request_split = request.split("|")
                if request_split[0] == "txt pls":
                    username = request_split[1]
                    game['portToUserMap'][str(addr[1])] = username
                    new_user = {}
                    new_user['username'] = username
                    new_user['progress'] = 0
                    new_user['socket'] = client_socket
                    new_user['ready'] = False
                    game['users'][username] = new_user
                    response = game['prompt']
                    print("Mapping port: " + str(addr[1]) + " to user: " + username)
                elif request == "ready":
                    username = game['portToUserMap'][str(addr[1])]
                    is_user_already_ready = game['users'][username]['ready']
                    if not is_user_already_ready:
                        game['users'][username]['ready'] = True
                        game['numReady'] += 1
                    response = "Currently waiting for players...\n" + str(game['numReady']) + "/" + str(game['numUsers']) + " players are ready."
                print("Sending back: " + response)
                client_socket.send(response.encode())
                # client_socket.send("additional".encode())
                # game['users'][username]['socket'].send("TAJPWEOTJAPWEOTJAPWOETJ".encode())
                if game['numReady'] >= game['numUsers']:
                    print("setting game started to 2")
                    print("WE HE")
                    game['started'] = 2
                    start_game(game)
            elif game['started'] == 2:
                # start_game(game)
                print("new recv req.")
                raw_request = client_socket.recv(1024)
                print("got passed new recv req")
                request = raw_request.decode()
                print("in started two")
                client_socket.send(response.encode())
                client_socket.send("start".encode())
                # for user in game['users'].keys():
                #     socket = game['users'][user]['socket']
                #     print(socket)
                #     socket.send("awepofjapwoefjpawoefjpwaoejfpaweofjapweofjapweofjwapeofj".encode())
            elif game['started'] == 1:
                print("here")
                raw_request = client_socket.recv(1024)
                request = raw_request.decode()
                response = gen_progress_string(progress)
                if request == "txt pls":
                    response = game['prompt']
                elif request.isdigit():
                    # print("Updating progress at: " + str(addr) + " to be: " + request)
                    print(progress)
                    progress[addr] = int(request)
                # print ("[*] Received: " + request)
                print("Sending back: " + response)
                client_socket.send(response.encode())
    except Exception as e:
        print(e)
        print("Closing connection to: " + str(addr))
        progress.pop(addr, None)
        client_socket.close()
        sys.exit()

def start_game(game):
    start_time = time()
    game['startTime'] = start_time
    curr_time = time()
    countdown = 3
    sent_3 = False
    sent_2 = False
    sent_1 = False
    while curr_time - start_time < 3:
        the_time = curr_time - start_time
        if the_time < 1 and not sent_3:
            message_all_clients("Starting game in 3!", game)
            print("Starting game in 3!")
            sent_3 = True
        elif the_time > 1 and the_time < 2 and not sent_2:
            message_all_clients("Starting game in 2!", game)
            print("Starting game in 2!")
            sent_2 = True
        elif the_time > 2 and the_time < 3 and not sent_1:
            message_all_clients("Starting game in 1!", game)
            print("Starting game in 1!")
            sent_1 = True
        curr_time = time()
    message_all_clients("GO!", game)
    game['started'] = 1

def message_all_clients(message, game):
    for user in game['users'].keys():
        socket = game['users'][user]['socket']
        socket.send(message.encode())

def tcp_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # get Private IP (unreliable)
    # IP = socket.gethostbyname(socket.gethostname())
    server.bind((IP, PORT))
    server.listen(NUM_CLIENTS) # supports 5 concurrent hosts
    game = {} # state of game
    prompt = generate_prompt(NUM_WORDS)
    game['startTime'] = 0
    game['prompt'] = prompt
    game['numUsers'] = 0
    game['numReady'] = 0
    game['users'] = {}
    game['started'] = 0
    game['numCharacters'] = len(prompt)
    game['winner'] = ""
    game['portToUserMap'] = {}

    print ("[*] Listening on %s:%d" % (IP, PORT))

    # thread_updater = threading.Thread(target=update_thread, args=(game,))
    # thread_updater.start()

    while True:
        client, addr = server.accept()
        print ("[*] Accepted connection from: %s:%d" %(addr[0], addr[1]))
        game['numUsers'] += 1
        client_handler = threading.Thread(target=handle_client, args=(client,addr,game))
        client_handler.setDaemon(True)
        client_handler.start()

def generate_prompt(num_words):
    file_object  = open("words.txt", "r")
    all_text = file_object.read()
    words = all_text.split(",")
    prompt = []
    for i in range(num_words):
        prompt.append(random.choice(words))
    return " ".join(prompt)

def gen_progress_string(game):
    print(d)
    progress_string = ""
    for user, data in game['users'].items():
        print(str(user))
    # for addr, count in d.items():
    #     print(addr)
    #     print(count)
    #     user_progress = str(addr[0]) + "|" + str(count) + ","
    #     progress_string += str(user_progress)
    return progress_string

if __name__ == '__main__':
    tcp_server()
