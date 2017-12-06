"""
Michael Tan
Computer Networks
Professor Anirudh Sivaraman
Assignment 5 - TypeRacer
December 5th, 2017
Server Code
"""
from datetime import datetime
import socket
import string
import sys
import threading
import random

# TODO add support for arguments (prod/debug, port, num_clients, num_words)
# TODO send progress data back to clients
# TODO implement "ready" feature for when all clients connect
# TODO implement timer (server side) to track winner

IP = "localhost"
PORT = 8000
NUM_WORDS = 50

def handle_client(client_socket, addr, prompt, progress):
    try:
        while True:
            raw_request = client_socket.recv(1024)
            request = raw_request.decode()
            response = gen_progress_string(progress)
            if request == "txt pls":
                response = prompt
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

def tcp_server():
    server = socket.socket( socket.AF_INET, socket.SOCK_STREAM)
    # get Private IP (unreliable)
    # IP = socket.gethostbyname(socket.gethostname())
    server.bind((IP, PORT))
    server.listen(5) # supports 5 concurrent hosts
    prompt = generate_prompt(NUM_WORDS)
    progress = {}

    print ("[*] Listening on %s:%d" % (IP, PORT))

    while True:
        client, addr = server.accept()
        progress[addr] = 0
        print ("[*] Accepted connection from: %s:%d" %(addr[0], addr[1]))
        client_handler = threading.Thread(target=handle_client, args=(client,addr,prompt,progress,))
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

def gen_progress_string(d):
    print(d)
    progress_string = ""
    if not d:
        return "EMPTY"
    for addr, count in d.items():
        print(addr)
        print(count)
        user_progress = str(addr[0]) + "|" + str(count) + ","
        progress_string += str(user_progress)
    return progress_string

if __name__ == '__main__':
    tcp_server()
