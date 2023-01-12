#!/usr/bin/python3

import socket
import sys
import time


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

login = False
id = -1
while True:
    print('% ', end='')    
    cmd = input('')
    cmd_list = cmd.split()

    if (cmd_list[0] == 'register'):
        if (len(cmd_list) != 4):
            print('Usage: register <username> <email> <password>')
        else:
            s_udp.sendto(cmd.encode(), (host, port))
            data, addr = s_udp.recvfrom(1024)
            print(data.decode())
    elif (cmd_list[0] == 'login'):
        if (len(cmd_list) != 3):
            print('Usage: login <username> <password>')
        else:
            s_tcp.send(cmd.encode())
            result = s_tcp.recv(1024).decode()
            #print(result)
            if (result[0] == 'W'):
                login = True
                result = result.split()
                
                id = int(result[2])
                print(result[0], result[1])
            else:
                print(result)
                
            #print(id)
            #print(type(id))
    elif (cmd_list[0] == 'logout'):
        if (len(cmd_list) != 1):
            print('Usage: logout')
        else:
            s_tcp.send(cmd.encode())
            result = s_tcp.recv(1024).decode()
            print(result)
            if (result[0] == 'B'):
                login = False
    elif (cmd_list[0] == 'whoami'):
        if (len(cmd_list) != 1):
            print('Usage: whoami')
        else:
            if (login == False):
                print('Please login first.')
            else:
                s_udp.sendto(cmd.encode(), (host, port))
                s_udp.sendto(str(id).encode(), (host, port))
                data, addr = s_udp.recvfrom(1024)
                print(data.decode())

    elif (cmd_list[0] == 'list-user'):
        if (len(cmd_list) != 1):
            print('Usage: list-user')
        else:
            s_tcp.send(cmd.encode())
            print(s_tcp.recv(1024).decode())

    elif (cmd_list[0] == 'create-board'):
        if (len(cmd_list) != 2):
            print('Usage: create-board <name>')
        else:
            if (login == False):
                print('Please login first.')
            else:
                s_tcp.send(cmd.encode())
                result = s_tcp.recv(1024).decode()
                print(result)
    elif (cmd_list[0] == 'list-board'):
        if (len(cmd_list) != 1):
            print('Usage: list-board')
        else:
            s_tcp.send(cmd.encode())
            print(s_tcp.recv(1024).decode())
            
    elif (cmd_list[0] == 'create-post'):
        if (len(cmd_list) < 6):
            print('Usage: create-post <board-name> --title <title> --content <content>')
        else:
            if (login == False):
                print('Please login first.')
            else:
                s_tcp.send(cmd.encode())
                result = s_tcp.recv(1024).decode()
                print(result)
    elif (cmd_list[0] == 'list-post'):
        if (len(cmd_list) != 2):
            print('Usage: list-board <boardname>')
        else:
            s_tcp.send(cmd.encode())
            print(s_tcp.recv(1024).decode())
    elif (cmd_list[0] == 'read'):
        if (len(cmd_list) != 2):
            print('Usage: read <post-S/N>')
        else:
            s_tcp.send(cmd.encode())
            print(s_tcp.recv(1024).decode())
    elif (cmd_list[0] == 'delete-post'):
        if (len(cmd_list) != 2):
            print('Usage: delete-post <post-S/N>')
        else:
            s_tcp.send(cmd.encode())
            print(s_tcp.recv(1024).decode())
    elif (cmd_list[0] == 'update-post'):
        if (len(cmd_list) < 4):
            print('Usage: update-post <post-S/N> --title/content <new>')
        else:
            s_tcp.send(cmd.encode())
            print(s_tcp.recv(1024).decode())

    elif (cmd_list[0] == 'comment'):
        if (len(cmd_list) < 3):
            print('Usage: comment <post-S/N> <comment>')
        else:
            s_tcp.send(cmd.encode())
            print(s_tcp.recv(1024).decode())
    
    elif (cmd_list[0] == 'exit'):
        if (len(cmd_list) != 1):
            print('Usage: exit')
        else:
            s_tcp.send(cmd.encode())
            s_tcp.close()
            s_udp.close()
            break
    else:
        print('Usage:\nregister <username> <email> <password>\n'\
            'login <username> <password>\nlogout\nwhoami\nlist-user\nexit')

    #time.sleep( 0.5 )
    
#ln -s client.py client