#!/usr/bin/python3

import socket
import sys
import time
from datetime import datetime

host = sys.argv[1]
port = int(sys.argv[2])

#create a TCP socket
s_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s_tcp.connect((host, port))
#create an UDP socket
s_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print('*********************************\n')
print('** Welecome to the BBS server. **\n')
print('*********************************\n')

print(s_tcp.recv(1024).decode())

login = False
id = -1
while True:
    print('% ', end='')    
    cmd = input('')
    cmd_list = cmd.split()

    
    if (cmd_list[0] == 'list-users'):
        if (len(cmd_list) != 1):
            print('Usage: list-users')
        else:
            s_tcp.send(cmd.encode())
            print(s_tcp.recv(1024).decode())
    elif (cmd_list[0] == 'get-ip'):
        if (len(cmd_list) != 1):
            print('Usage: get-ip')
        else:
            s_tcp.send(cmd.encode())
            print(s_tcp.recv(1024).decode())       
    elif (cmd_list[0] == 'exit'):
        if (len(cmd_list) != 1):
            print('Usage: exit')
        else:
            s_tcp.send(cmd.encode())
            print(s_tcp.recv(1024).decode()) 
            s_tcp.close()
            s_udp.close()
            break
    else:
        print('Usage:\nregister <username> <email> <password>\n'\
            'login <username> <password>\nlogout\nwhoami\nlist-user\nexit')

    #time.sleep( 0.5 )
    
#ln -s client.py client