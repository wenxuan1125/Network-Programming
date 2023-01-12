#!/usr/bin/python3
import socket
import threading
import sys
import sqlite3

host = '127.0.0.1'
port = int(sys.argv[1])

# thread's job
def job(c_tcp, c_addr_tcp):
    sql_conn.execute('''insert into user (ip, port, online) 
                values(\''''+ c_addr_tcp[0] + '\', \'' + str(c_addr_tcp[1]) + '\' , 1 );')
    sql_conn.commit()
    sql='select max(id) from user where ip = \'' + c_addr_tcp[0] +  '\' and port = \'' + str(c_addr_tcp[1]) + '\';'
    result = sql_conn.execute(sql)
    result=result.fetchone()
    id = str(result[0])

    print('New connection from ' +c_addr_tcp[0] + ' : '+ str(c_addr_tcp[1])+ ' user'+ id)

    response='Welecome, you are user' + id + '. ' 
    c_tcp.send(response.encode())

    while True:
        cmd = c_tcp.recv(1024).decode()  # receive command from client 
        cmd_list = cmd.split()
        #print( cmd_list)

        if (cmd_list[0] == 'get-ip'):
            response='IP: '+c_addr_tcp[0] + ': '+ str(c_addr_tcp[1])
            c_tcp.send(response.encode())
                
        elif (cmd_list[0] == 'list-users'):
            response = ''
            sql = 'select id from user where online = 1;'
            result = sql_conn.execute(sql)
            for row in result:
                response = response + 'user' + str(row[0]) + '\n'
            #print(response)
            c_tcp.send(response.encode())

        elif (cmd_list[0] == 'exit'):
            sql = 'update user set online = 0 where port = \'' + str(c_addr_tcp[1]) + '\';'
            sql_conn.execute(sql)
            sql_conn.commit()
            response='Bye, user' + id + '.'
            c_tcp.send(response.encode())
            c_tcp.close()
            print('user'+ id+' '+c_addr_tcp[0] + ': '+ str(c_addr_tcp[1]) +' disconnected')
            break


sql_conn = sqlite3.connect('server.db', check_same_thread=False)
try: 
    sql_conn.execute('drop table user;')
    sql_conn.execute('''create table user
       ( id integer primary key autoincrement,
        ip text not null, 
        port text not null,
        online ineger not null); ''')
except:
    sql_conn.execute('''create table user
       ( id integer primary key autoincrement,
        ip text not null, 
        port text not null,
        online ineger not null); ''')

sql_conn.commit()



#create a TCP socket
s_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s_tcp.bind((host, port))
s_tcp.listen()

while True:
    # using client_socket, new created socket to communicate with the client
    c_tcp, c_addr_tcp = s_tcp.accept()
    t = threading.Thread(target=job, args=(c_tcp, c_addr_tcp))     #create thread
    t.start()   #start the thread
    #threads.append(threading.Thread(target = job, args = (i,)))

sql_conn.close()

#ln -s server.py server
