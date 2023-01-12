#!/usr/bin/python3
import socket
import socket
import sys
import select
import time
import os

host = '127.0.0.1'
port = int(sys.argv[1])
timeout = 3

s_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s_udp.bind((host, port))


while True:
    cmd, addr = s_udp.recvfrom(1024)
    cmd = cmd.decode()
    cmd_list = cmd.split()

    if (cmd_list[0] == 'get-file'):
        i=1
        while(1):
            if( i==len(cmd_list)):
                break

            file_name = cmd_list[i]

            f = open(file_name, 'rb')
            s_udp.sendto(file_name.encode(), addr)  #send file name
            time.sleep(0.02)

            data = f.read(1024)
            while (data):
                if (s_udp.sendto(data, addr)):  #binary file reads bytes from file, so use 'data' is ok
                    data = f.read(1024)
                    time.sleep(0.02) # Give receiver a bit time to save  
            f.close()
            i=i+1

            time.sleep(2)


    elif (cmd_list[0] == 'get-file-list'):
        file_list=os.listdir(path='.')
        response='Files: '
        i=0
        while(1):
            if( i==len( file_list)):
                break
            response=response+file_list[i]+' '
            i=i+1
        s_udp.sendto(response.encode(), addr)
        
    



        
    
   