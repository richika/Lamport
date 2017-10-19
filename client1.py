# Python program to implement client side of chat room.
import socket
import select
import sys
import json
import re
from thread import *
from threading import Thread, Lock
import time

class LamportSystem:
    lamport_clock = 0
    process_id = 1
    req_number = 0
    numOfLikes = 0
    req_queue = []
    reply_dict = {}
    num_processes = 3
    mutex_rcv_req = Lock()
    mutex_rcv_rep = Lock()
    mutex_rcv_rel = Lock()
    mutex_send_req = Lock()

    def manage_lamport(self, clock_time):
        LamportSystem.lamport_clock = max(LamportSystem.lamport_clock, clock_time) + 1
        print 'Lamport clock:', LamportSystem.lamport_clock

    def process_likes(self, likes):
        LamportSystem.numOfLikes += int(likes)
        print 'Number of Likes:', LamportSystem.numOfLikes

    def add_to_queue(self, request):
        if bool(LamportSystem.req_queue):
            for index, req in enumerate(LamportSystem.req_queue):
                if req['clock'] > request['clock']:
                    LamportSystem.req_queue.insert(index, request)
                    break
                elif (req['clock'] == request['clock']) and (req['process_id'] > request['process_id']):
                    LamportSystem.req_queue.insert(index, request)
                    break
                else:
                    LamportSystem.req_queue.append(request)
                    break
        else:
            LamportSystem.req_queue.append(request)

        print LamportSystem.req_queue

    def send_message(self, message):
        server.send(message)
        print 'Message sent: ', message

    def send_request(self,likes):
        LamportSystem.mutex_send_req.acquire()
        self.manage_lamport(LamportSystem.lamport_clock)
        LamportSystem.req_number += 1
        req = {'process_id': LamportSystem.process_id, 'clock' : LamportSystem.lamport_clock, 'type' : 'REQ', 'req_number' : LamportSystem.req_number, 'num_likes': likes}
        self.add_to_queue(req)
        self.send_message(json.dumps(req))
        LamportSystem.mutex_send_req.release()

    def send_reply(self, message):
        self.manage_lamport(LamportSystem.lamport_clock)
        reply = {'req_process_id': message['process_id'], 'reply_process_id': LamportSystem.process_id, 'clock': LamportSystem.lamport_clock, 'type': 'REP',
               'req_number': message['req_number']}
        self.send_message(json.dumps(reply))

    def send_release(self, likes):
        self.manage_lamport(LamportSystem.lamport_clock)
        LamportSystem.req_queue.pop(0)   #check if process on top
        release = {'process_id': LamportSystem.process_id, 'clock': LamportSystem.lamport_clock, 'type': 'REL',
                    'req_number': LamportSystem.req_number, 'num_likes' : likes}
        self.send_message(json.dumps(release))

    def rcv_request(self,request):
        LamportSystem.mutex_rcv_req.acquire()
        self.manage_lamport(request['clock'])
        self.add_to_queue(request)
        self.send_reply(request)
        LamportSystem.mutex_rcv_req.release()

    def rcv_release(self,release):
        LamportSystem.mutex_rcv_rel.acquire()
        self.manage_lamport(release['clock'])
        self.process_likes(release['num_likes'])
        LamportSystem.req_queue.pop(0)   #check if process on top
        LamportSystem.mutex_rcv_rel.release()

    def rcv_reply(self,reply):
        LamportSystem.mutex_rcv_rep.acquire()
        self.manage_lamport(reply['clock'])
        if reply['req_number'] not in LamportSystem.reply_dict:
            LamportSystem.reply_dict[reply['req_number']] = []
        LamportSystem.reply_dict[reply['req_number']].append(reply['reply_process_id'])
        if len(LamportSystem.reply_dict[reply['req_number']]) == LamportSystem.num_processes:
            while LamportSystem.req_queue[0]['process_id'] != LamportSystem.process_id:
                continue
            self.process_likes(LamportSystem.req_queue[0]['num_likes'])
            self.send_release(LamportSystem.req_queue[0]['num_likes'])
        LamportSystem.mutex_rcv_rep.release()

    def process_message_from_server(self, message):
        message_type = message['type']
        if message_type == 'REQ':
            self.rcv_request(message)
        elif message_type == 'REL':
            self.rcv_release(message)
        elif message_type == 'REP':
            self.rcv_reply(message)

    def send_message_to_server(self,message):
        [int(likes) for likes in message.split() if likes.isdigit()]
        self.send_request(likes)


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = '127.0.0.1'
port = 8888

try:
    remote_ip = socket.gethostbyname(host)

except socket.gaierror:
    # could not resolve
    print 'Hostname could not be resolved. Exiting'
    sys.exit()

print 'Ip address of ' + host + ' is ' + remote_ip

# Connect to remote server
server.connect((remote_ip, port))

print 'Socket Connected to ' + host + ' on ip ' + remote_ip
server.send(json.dumps({'process_id' : 1, 'type':'CON'}))


lamport_object = LamportSystem()

while True:

    # maintains a list of possible input streams
    sockets_list = [sys.stdin, server]

    read_sockets, write_socket, error_socket = select.select(sockets_list, [], [])

    for socks in read_sockets:
        if socks == server:
            messages = socks.recv(2048)
            r = re.split('(\{.*?\})(?= *\{)', messages)
            for message in r:
                if message == '\n':
                    continue
                try:
                    message = json.loads(message)
                    print 'Message received: ', message
                    start_new_thread(lamport_object.process_message_from_server, (message,))
                except:
                    print message

        else:
            message = sys.stdin.readline()
            time.sleep(5)
            start_new_thread(lamport_object.send_message_to_server, (message,))
            sys.stdout.flush()

server.close()
