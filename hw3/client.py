#!/usr/bin/python3
import select
import socket
import time
import threading
import sys
from datetime import datetime
import queue



host = sys.argv[1]
port = int(sys.argv[2])
select_input = []
socket_list=[]
parse_thread_exit = False
accept_thread_exit = False
create_accept_thread = True
create_parse_thread = False
mutex_chat_record = threading.Lock()
record = queue.Queue(maxsize=3)
leave_chatroom = False
detach = False




def server_accept(room_port, chatroom_tcp):

    global record, socket_list, select_input, mutex_chat_record
    #global record
    while (accept_thread_exit == False):
        # using client_socket, new created socket to communicate with the client
        r, w, x = select.select([chatroom_tcp], [], [], 0.1)
        for i in r:
            c_tcp, c_addr_tcp = i.accept()
            #c_tcp, c_addr_tcp = chatroom_tcp.accept()
            select_input.append(c_tcp)
            socket_list.append(c_tcp)

            mutex_chat_record.acquire()
            temp1 = []
            result=''
            for i in range(0, record.qsize()):
                temp2 = record.get()
                temp1.append(temp2)
                result = result + temp2 + '\n'
            c_tcp.send(result.encode())

            for i in range(0, len(temp1)):
                record.put(temp1[i])


            mutex_chat_record.release()
    #print('accept thread exit!')  
        
def server_parse():
    global record, mutex_chat_record, select_input, socket_list, parse_thread_exit
    parse_thread_exit = False
    
    while (parse_thread_exit == False):
        #print('parse_thread_exit: '+str(parse_thread_exit))
        r, w, x = select.select(select_input, [], [], 0.1)
        for sck in r:
            #client
            message = sck.recv(1024).decode()
            msg_list = message.split()

            if (len(msg_list) != 0):
                
                if (msg_list[0] == 'leave-chatroom'):
                    leave_user = msg_list[1]
                    message = 'sys[' + str(datetime.now().hour) + ':' + str(datetime.now().minute) + ']: ' + leave_user + ' leave us.'
                    
                    socket_list.remove(sck)
                    select_input.remove(sck)
                    #print(message)
                    for i in socket_list:
                        if (i != sck):
                            i.send(message.encode())
                else:
                    if (len(msg_list[0]) >= 3):
                        if (msg_list[0][0:3] != 'sys'):
                            mutex_chat_record.acquire()
                            if (record.empty()):
                                record.put(message)
                            elif (record.qsize() == 3):
                                record.get()
                                record.put(message)
                            else:
                                record.put(message)
                            mutex_chat_record.release()

                    for i in socket_list:
                        if (i != sck):
                            i.send(message.encode())

    #print('parse thread exit!')           



def chatroom(room_port, login_user):

    global record, mutex_chat_record, leave_chatroom, select_input, socket_list, parse_thread_exit
    
    if (create_accept_thread):
        #create a TCP socket
        chatroom_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        chatroom_tcp.bind((host, room_port))
        chatroom_tcp.listen()
        t = threading.Thread(target=server_accept, args=(room_port, chatroom_tcp))  #create thread
        t.start()

    print('*********************************\n')
    print('*** Welecome to the chatroom. ***\n')
    print('*********************************\n')
    #print('login user: '+ login_user)

    # get the last three records for chatroom owner
    if (create_accept_thread == False):
        mutex_chat_record.acquire()
        temp1 = []
        result=''
        for i in range(0, record.qsize()):
            temp2 = record.get()
            temp1.append(temp2)
            result = result + temp2 + '\n'
        print(result)

        for i in range(0, len(temp1)):
            record.put(temp1[i])

        mutex_chat_record.release()

    leave_chatroom = False
    detach = False
    select_input.append(sys.stdin)
       
    while (leave_chatroom == False and detach == False):
        r, w, x = select.select(select_input, [], [], 0.1)
        for sck in r:
            if (sck == sys.stdin):
                #server 
                message = sys.stdin.readline()
                # the last char is '\n'
                message=message[0: len(message)-1]
                msg_list = message.split()

                if (len(msg_list) != 0):
                    '''
                    print('****')
                    print('msg: ' + message)
                    print('msg[0]: ' + msg_list[0])
                    print('msg_len: ' + str(len(msg_list)))
                    print('****')'''
                    if (msg_list[0] == 'leave-chatroom' and len(msg_list) == 1):
                        leave_chatroom = True
            
                        for i in socket_list:
                            result='sys[' + str(datetime.now().hour) + ':' + str(datetime.now().minute) + ']: The chatroom is close.'
                            i.send(result.encode())

                        select_input = []
                        socket_list = []
                        
                        break
                    elif (msg_list[0] == 'detach' and len(msg_list) == 1):
                        select_input.remove(sys.stdin)
                        detach = True
                        t = threading.Thread(target=server_parse)  #create thread
                        t.start()

                        break
                    else:

                        result = login_user + '[' + str(datetime.now().hour) + ':' + str(datetime.now().minute) + ']: ' + message

                        mutex_chat_record.acquire()
                        if (record.empty()):
                            record.put(result)
                        elif (record.qsize() == 3):
                            record.get()
                            record.put(result)
                        else:
                            record.put(result)
                        mutex_chat_record.release()

                        # send message to other
                        for i in socket_list:
                            i.send(result.encode())
            else:
                #client
                message = sck.recv(1024).decode()
                msg_list = message.split()

                '''print('&&&')
                print('msg: ' + message)
                print('msg[0]: ' + msg_list[0])
                print('&&&')'''
                if (len(msg_list) != 0):
                    
                    if (msg_list[0] == 'leave-chatroom'):
                        #print('^')
                        leave_user = msg_list[1]
                        message = 'sys[' + str(datetime.now().hour) + ':' + str(datetime.now().minute) + ']: ' + leave_user + ' leave us.'
                        
                        socket_list.remove(sck)
                        select_input.remove(sck)
                        print(message)
                        for i in socket_list:
                            if (i != sck):
                                i.send(message.encode())
                    else:
                        #print('%')
                        if (len(msg_list[0]) >= 3):
                            if (msg_list[0][0:3] != 'sys'):
                                mutex_chat_record.acquire()
                                if (record.empty()):
                                    record.put(message)
                                elif (record.qsize() == 3):
                                    record.get()
                                    record.put(message)
                                else:
                                    record.put(message)
                                mutex_chat_record.release()

                        print(message)
                        for i in socket_list:
                            if (i != sck):
                                i.send(message.encode())
                    
                    
            
                            
                

def connect_chatroom(room_port, login_user):                   
    #create a TCP socket
    client_chatroom = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_chatroom.connect((host, room_port))

    print('*********************************\n')
    print('*** Welecome to the chatroom. ***\n')
    print('*********************************\n')
    #print('login user: '+ login_user)
    time.sleep(0.3)

    message = 'sys[' + str(datetime.now().hour) + ':' + str(datetime.now().minute) + ']: ' + login_user + ' join us.'
    client_chatroom.send(message.encode())

    leave = False
    
    while (leave != True):
        
        r, w, x = select.select([sys.stdin, client_chatroom], [], [], 0.1)
        for sck in r:
            if (sck == sys.stdin):
                message = sys.stdin.readline()
                # the last char is '\n'
                message=message[0: len(message)-1]
                if (message == 'leave-chatroom'):
                    #print('^^^^^')
                    result = message + ' ' + login_user
                    client_chatroom.send(result.encode())
                    leave = True
                    client_chatroom.close()
                    break
                else:
                    '''print('^^^^^')
                    print(message)
                    if (message[len(message) - 2] == '\n'):
                        print('$')
                    if (message[len(message) - 2] == '\r'):
                        print('#')
                    print('^^^^^')'''
                    result = login_user + '[' + str(datetime.now().hour) + ':' + str(datetime.now().minute) + ']: ' + message
                    client_chatroom.send(result.encode())
                
                
            else:
                result = sck.recv(1024).decode()
                result_list = result.split()
                print(result)

                if (result_list[0][0:3] == 'sys'):
                    temp=''
                    for i in range(1, len(result_list)):
                        temp = temp + result_list[i] + ' '
                    temp = temp[0: len(temp) - 1]
                    
                    if(temp == 'The chatroom is close.'):
                        client_chatroom.close()
                        leave = True
                        break
                    
                    
            
    




    

        

#create a TCP socket
s_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s_tcp.connect((host, port))
#create an UDP socket
s_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print('*********************************\n')
print('** Welecome to the BBS server. **\n')
print('*********************************\n')

login = False
login_user = ''
chatroom_port = 0
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
                login_user = result[1]
                login_user=login_user[0:len(login_user)-1]
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

    elif (cmd_list[0] == 'create-chatroom'):
        if (len(cmd_list) != 2):
            print('Usage: create-chatroom <port>')
        else:
            s_tcp.send(cmd.encode())
            result = s_tcp.recv(1024).decode()
            print(result)
            if (result[0] == 'S'):
                chatroom_port = int(cmd_list[1])
                chatroom(int(chatroom_port), login_user)

                if (leave_chatroom):
                    s_tcp.send(b'leave-chatroom')
                print('Welecome back to BBS.')
    
                
    elif (cmd_list[0] == 'join-chatroom'):
        if (len(cmd_list) != 2):
            print('Usage: join-chatroom <chatroom_name>')
        else:
            s_tcp.send(cmd.encode())
            result = s_tcp.recv(1024).decode()

            if (result[0] == 'A'):
                result = result.split()
                #print(result[0], result[1], result[2], result[3], result[4])
                #print(int(result[5]))
                connect_chatroom(int(result[5]), login_user)
                print('Welecome back to BBS.')
            else:
                print(result)
    elif (cmd_list[0] == 'restart-chatroom'):
        if (len(cmd_list) != 1):
            print('Usage: restart-chatroom')
        else:
            s_tcp.send(cmd.encode())
            result = s_tcp.recv(1024).decode()
            print(result)
            if (result[0] == 'S'):
                create_accept_thread = False
                chatroom(chatroom_port, login_user)

                if (leave_chatroom):
                    s_tcp.send(b'leave-chatroom')
                print('Welecome back to BBS.')

    elif (cmd_list[0] == 'attach'):
        if (len(cmd_list) != 1):
            print('Usage: attach')
        else:
            s_tcp.send(cmd.encode())
            result = s_tcp.recv(1024).decode()
            if (result[0] != 'W'):
                print(result)

            if (result[0] == 'W'):
                create_accept_thread = False
                parse_thread_exit = True
                #print('parse_thread_exit: '+str(parse_thread_exit))
                chatroom(chatroom_port, login_user)

                if (leave_chatroom):
                    s_tcp.send(b'leave-chatroom')
                print('Welecome back to BBS.')            

    elif (cmd_list[0] == 'list-chatroom'):
        if (len(cmd_list) != 1):
            print('Usage: list-chatroom')
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
            parse_thread_exit = True
            accept_thread_exit = True
            #time.sleep( 0.3 )
            break
    else:
        print('Usage:\nregister <username> <email> <password>\n'\
            'login <username> <password>\nlogout\nwhoami\nlist-user\nexit')

    #time.sleep( 0.5 )
    
#ln -s client.py client