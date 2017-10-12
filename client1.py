# Python program to implement client side of chat room.
import socket
import select
import sys

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

server.send("Message from client 1")

socket = [server]
read_socket, write_socket, error_socket = select.select(socket, [], [])

while True:
    for sock in read_socket:
        message = server.recv(2048)
        print "Received : " + message

server.close()