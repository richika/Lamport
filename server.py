import socket
import sys
from thread import *
import json

class MessagePassServer:
    list_of_clients = {}
    HOST = ''
    PORT = 8888

    def client_thread(self, conn):
        while True:
            try:
                message = conn.recv(2048)
                parsed_message = json.loads(message)

                if parsed_message:

                    if parsed_message['type'] == 'CON':
                        process_id = parsed_message['process_id']
                        self.list_of_clients[process_id] = conn

                    elif parsed_message['type'] == 'REQ' or parsed_message['type'] == 'REL':
                        # Calls broadcast function to send message to all other clients
                        self.broadcast(message, conn)

                    elif parsed_message['type'] == 'REP':
                        # Calls function to send message to requesting client
                        self.send_ok(parsed_message)
                else:
                    self.remove(conn)

            except:
                continue

    def send_ok(self, parsed_message):
        print 'check in send ok'
        req_process_id = parsed_message['req_process_id']
        client = self.list_of_clients[req_process_id]
        print self.list_of_clients

        try:
            print 'in try'
            print 'sending to client ' + req_process_id + 'message ' + parsed_message
            client.send(parsed_message)

        except:
            print 'in exception --- ' + sys.exc_info()[0]
            client.close()

    def broadcast(self, message, connection):
        print 'in broadcast'
        for client in self.list_of_clients:
            if self.list_of_clients[client] != connection:
                try:
                    print 'sending to client ' + client + 'message ' + message
                    print self.list_of_clients
                    self.list_of_clients[client].send(message)
                except:
                    print 'in 57' + sys.exc_info()[0]
                    self.list_of_clients[client].close()

    def initialiseConnection(self):

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            s.bind((self.HOST, self.PORT))
        except socket.error, msg:
            print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            sys.exit()

        print 'Socket bind complete'

        s.listen(10)
        print 'Socket now listening'

        while 1:
            conn, addr = s.accept()
            print 'Connected with ' + addr[0] + ':' + str(addr[1])

            start_new_thread(self.client_thread, (conn,))

        s.close()


Server = MessagePassServer()
Server.initialiseConnection()
