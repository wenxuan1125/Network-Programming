#!/usr/bin/python3
import socket
import threading
import sys
import sqlite3

host = '127.0.0.1'
port = int(sys.argv[1])

# thread's job
def job(c_tcp, c_addr_tcp):
    print('New connection.')
    login = False
    login_user=''

    while True:
        cmd = c_tcp.recv(1024).decode()  # receive command from client 
        cmd_list = cmd.split()
        #print( cmd_list)
        if (cmd_list[0] == 'login'):
            if (login == True):
                c_tcp.send(b'Please logout first.')
            else:
                username = cmd_list[1]
                password = cmd_list[2]
                sql = 'select username from user where username = \'' + username + '\' and password = \'' + password + '\';'
                result = sql_conn.execute(sql)
                result = result.fetchone() # result from cursor_object to list
                if ((result) == None):
                    c_tcp.send(b'Login failed.')
                else:
                    login = True
                    login_user = username
                    sql_conn.execute('''insert into key (username) 
                        values(\''''+ username + '\'); ')
                    sql_conn.commit()
                    sql='select max(id) from key where username = \'' + username + '\';'
                    result = sql_conn.execute(sql)
                    result=result.fetchone()  # result from cursor_object to tuple(id, )
                    #result = result.fetchall() # result from cursor_object to list
                    random_key = result[0]
                    #print(random_key)
                    response='Welecome, ' + username + '. ' + str(random_key)
                    c_tcp.send(response.encode())
                    #c_tcp.send(str(random_key).encode())
                    

                
        elif (cmd_list[0] == 'logout'):
            if (login == False):
                c_tcp.send(b'Please login first.')
            else:
                login = False
                response='Bye, ' + login_user + '.'
                c_tcp.send(response.encode())
        elif (cmd_list[0] == 'list-user'):
            response = 'Name Email\n'
            sql = 'select username, email from user;'
            result = sql_conn.execute(sql)
            for row in result:
                response = response + row[0] + ' ' + row[1] + '\n'
            c_tcp.send(response.encode())
        elif (cmd_list[0] == 'exit'):
            c_tcp.close()
            break


def udp_job():
    #sql_conn = sqlite3.connect('server.db')
    #create an UDP socket
    s_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s_udp.bind((host, port))

    while True:
        cmd, addr = s_udp.recvfrom(1024)
        cmd = cmd.decode()
        cmd_list = cmd.split()

        if (cmd_list[0] == 'register'):
            username = cmd_list[1]
            email = cmd_list[2]
            password = cmd_list[3]
            sql = 'select username from user where username = \'' + username + '\';'
            result = sql_conn.execute(sql)
            result = result.fetchall()  # result from cursor_object to list
            
            if (len(result) == 0):
                sql = '''insert into user (username, email, password) 
                values(\''''+ username + '\', \'' + email + '\', \'' + password + '\');'
                sql_conn.execute(sql)
                sql_conn.commit()
                s_udp.sendto(b'Register successfully.', addr)
            else:
                s_udp.sendto(b'Username is already used.', addr)
        elif (cmd_list[0] == 'whoami'):
            random_key, addr = s_udp.recvfrom(1024)
            random_key = random_key.decode()
            
            sql = 'select username from key where id = ' + random_key + ';'
            result = sql_conn.execute(sql)
            result = result.fetchone()  # result from cursor_object to tuple( username, )
            username = result[0]
            s_udp.sendto(username.encode(), addr)


sql_conn = sqlite3.connect('server.db', check_same_thread=False)
try: 
    sql_conn.execute('drop table user;')
    sql_conn.execute('''create table user
       ( username text primary key  not null,
       email    text not null,
       password text not null); ''')
except:
    sql_conn.execute('''create table user
       ( username text primary key  not null,
       email    text not null,
       password text not null); ''')

try: 
    sql_conn.execute('drop table key;')
    sql_conn.execute('''create table key
       ( id integer primary key autoincrement,
       username text not null); ''')
except:
    sql_conn.execute('''create table key
       ( id integer primary key autoincrement,
       username text not null); ''')
      
#sql_conn.execute('''insert into user (username, email, password) 
#                values( 'amy', 'wenxuan1125', 881125 );''')
sql_conn.commit()


udp = threading.Thread(target=udp_job)     #create thread
udp.start()

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
