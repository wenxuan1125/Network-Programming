import socket
import sys
import time
import select

host = sys.argv[1]
port = int(sys.argv[2])
timeout = 1


#create an UDP socket
s_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
    print('% ', end='')    
    cmd = input('')
    cmd_list = cmd.split()

    if (cmd_list[0] == 'get-file-list'):
        s_udp.sendto(cmd.encode(), (host, port))
        data, addr = s_udp.recvfrom(1024)
        print(data.decode())

    elif (cmd_list[0] == 'get-file'):
        s_udp.sendto(cmd.encode(), (host, port))
        i=1
        while(1):
            if( i==len(cmd_list)):
                break
            file_name, addr = s_udp.recvfrom(1024)  #get file name
            file_name=file_name.decode()

            f = open(file_name, 'wb')
            while True:
                ready = select.select([s_udp], [], [], timeout)
                if ready[0]:
                    data, addr = s_udp.recvfrom(1024)
                    f.write(data)

                else:
                    f.close()
                    break
            i=i+1
        
            
    elif (cmd_list[0] == 'exit'):
        s_udp.sendto(cmd.encode(), (host, port))
        s_udp.close()
        break
    
        
