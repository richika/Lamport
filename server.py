import socket
import sys
from thread import *

HOST = ''  # Symbolic name meaning all available interfaces
PORT = 8888  # Arbitrary non-privileged port

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print 'Socket created'

# Bind socket to local host and port
try:
    s.bind((HOST, PORT))
except socket.error, msg:
    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()

print 'Socket bind complete'

# Start listening on socket
s.listen(10)
print 'Socket now listening'

list_of_clients = []

# Function for handling connections. This will be used to create threads
def clientthread(conn):

    while True:
        try:
            message = conn.recv(2048)
            if message:
                print "Received from client < " + addr[0] + "> " + message

                # Calls broadcast function to send message to all
                message_to_send = "<" + addr[0] + "> " + message
                broadcast(message_to_send, conn)

            else:
                """message may have no content if the connection
                is broken, in this case we remove the connection"""
                remove(conn)

        except:
            continue

def broadcast(message, connection):
            for client in list_of_clients:
                if client != connection:
                    try:
                        client.send(message)
                    except:
                        client.close()

                        # if the link is broken, we remove the client
                        remove(clients)

def remove(connection):
            if connection in list_of_clients:
                list_of_clients.remove(connection)

# now keep talking with the client
while 1:
    # wait to accept a connection - blocking call
    conn, addr = s.accept()
    list_of_clients.append(conn)
    print 'Connected with ' + addr[0] + ':' + str(addr[1])

    # start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
    start_new_thread(clientthread, (conn))

s.close()