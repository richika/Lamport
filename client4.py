# Python program to implement client side of chat room.
import socket
import select
import sys
import json

class LamportSystem:
    lamport_clock = 0
    process_id = 1
    req_number = 0
    numOfLikes = 0
    req_queue = []
    reply_dict = {}
    num_processes = 3

    def manage_lamport(clock_time):
        LamportSystem.lamport_clock = max(LamportSystem.lamport_clock, clock_time) + 1

    def process_likes(likes):
        LamportSystem.numOfLikes += likes

    def add_to_queue(request):
        for index, req in enumerate(LamportSystem.req_queue):
            if req['clock'] > request['clock']:
                LamportSystem.req_queue.insert(index, request)
            elif (req['clock'] == request['clock']) and (req['process_id'] > request['process_id']):
                LamportSystem.req_queue.insert(index, request)
            else:
                LamportSystem.req_queue.append(request)

    def send_message(message):
        server.send(message)

    def send_request(self,likes):
        self.manage_lamport(LamportSystem.lamport_clock)
        LamportSystem.req_number += LamportSystem.req_number
        req = {'process_id': LamportSystem.process_id, 'clock' : LamportSystem.lamport_clock, 'type' : 'REQ', 'req_number' : LamportSystem.req_number, 'num_likes': likes}
        self.add_to_queue(req)
        self.send_message(json.dumps(req))

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
        request = json.loads(request)
        self.manage_lamport(request['clock'])
        self.add_to_queue(request)
        self.send_reply(self, request)

    def rcv_release(self,release):
        release = json.loads(release)
        self.manage_lamport(release['clock'])
        self.process_likes(release['likes'])
        LamportSystem.req_queue.pop(0)   #check if process on top

    def rcv_reply(self,reply):
        reply = json.loads(reply)
        self.manage_lamport(reply['clock'])
        if reply['req_number'] not in LamportSystem.reply_dict:
            LamportSystem.reply_dict[reply['req_number']] = []
        LamportSystem.reply_dict[reply['req_number']].append(reply['reply_process_id'])
        if len(LamportSystem.reply_dict[reply['req_number']]) == LamportSystem.num_processes:
            if LamportSystem.req_queue[0]['process_id'] == LamportSystem.process_id:
                self.process_likes(LamportSystem.req_queue[0]['num_likes'])
                self.send_release(LamportSystem.req_queue[0]['num_likes'])


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

while True:

    # maintains a list of possible input streams
    sockets_list = [sys.stdin, server]

    read_sockets, write_socket, error_socket = select.select(sockets_list, [], [])

    for socks in read_sockets:
        if socks == server:
            message = socks.recv(2048)
            print message
        else:
            message = sys.stdin.readline()
            server.send(message)
            sys.stdout.write("<You>")
            sys.stdout.write(message)
            sys.stdout.flush()

server.close()