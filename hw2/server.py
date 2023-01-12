#!/usr/bin/python3
import socket
import threading
import sys
import sqlite3
from datetime import datetime

host = '127.0.0.1'
port = int(sys.argv[1])
post = []  # [[sn0, boardname0, title0, content0, author0, date0], ...]
post_set = set()    # store sn in post
post_sn = 1
mutex_post = threading.Lock()
comment = []   # [[sn0, user0, comment0], ...]
mutex_comment = threading.Lock()

# thread's job
def job(c_tcp, c_addr_tcp):
    global post, post_sn, mutex_post, post_set, comment, mutex_comment
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

        elif (cmd_list[0] == 'create-board'):
            boardname = cmd_list[1]
            sql = 'select boardname from board where boardname = \'' + boardname + '\';'
            result = sql_conn.execute(sql)
            result = result.fetchall()  # result from cursor_object to list
            
            if (len(result) == 0):
                #print('*')
                sql = '''insert into board (boardname, moderator) 
                values(\''''+ boardname + '\', \'' + login_user + '\');'
                sql_conn.execute(sql)
                sql_conn.commit()
                c_tcp.send(b'Create board successfully.')
                #print('*')
            else:
                #print('#')
                c_tcp.send(b'Board already exists.')
                #print('#')
        elif (cmd_list[0] == 'list-board'):
            response = 'Index Name Moderator\n'
            sql = 'select boardname, moderator from board;'
            result = sql_conn.execute(sql)
            id = 1
            for row in result:
                response = response + str(id) + ' ' + row[0] + ' ' + row[1] + '\n'
                id = id + 1
            c_tcp.send(response.encode())
        elif (cmd_list[0] == 'create-post'):
            boardname = cmd_list[1]
            title = ''
            content = ''
            i = 3
            for j in range(3, len(cmd_list)):
                if (cmd_list[j] == '--content'):
                    i = j + 1
                    title = title[0:len(title) - 1]
                    break
                title = title + cmd_list[j] + ' '
            for j in range(i, len(cmd_list)):
                content = content + cmd_list[j]
                if (j != len(cmd_list) - 1):
                    content = content + ' '
            #print(title + content)
            #print(content + title)

            sql = 'select boardname from board where boardname = \'' + boardname + '\';'
            result = sql_conn.execute(sql)
            result = result.fetchall()  # result from cursor_object to list
            if (len(result) == 0):
                c_tcp.send(b'Board does not exist.')
            else:
                mutex_post.acquire()
                date=str(datetime.now().month)+'/'+str(datetime.now().day)
                post.append([post_sn, boardname, title, content, login_user, date])
                post_set.add(post_sn)
                post_sn = post_sn + 1
                mutex_post.release()
                c_tcp.send(b'Create post successfully.')

        elif (cmd_list[0] == 'list-post'):
            boardname = cmd_list[1]

            sql = 'select boardname from board where boardname = \'' + boardname + '\';'
            result = sql_conn.execute(sql)
            result = result.fetchall()  # result from cursor_object to list
            if (len(result) == 0):
                c_tcp.send(b'Board does not exist.')
            else:
                mutex_post.acquire()
                response = 'S/N Title Author Date\n'
                for i in range(0, len(post)):
                    if (post[i][1] == boardname):
                        response = response + ' ' + str(post[i][0]) + ' ' + post[i][2] + ' ' + \
                        post[i][4] + ' ' + post[i][5] + '\n'
                mutex_post.release()

                c_tcp.send(response.encode())
        elif (cmd_list[0] == 'read'):
            sn = int(cmd_list[1])
            mutex_post.acquire()
            for i in range(0, len(post)):
                if (post[i][0] == sn):
                    response = 'Author: ' + post[i][4] + '\n'
                    response = response + 'Title: ' + post[i][2] + '\n'
                    response = response + 'Date: ' + post[i][5] + '\n'
                    response = response + '--\n'

                    post_content = post[i][3].split('<br>')
                    for j in range(0, len(post_content)):
                        response = response + post_content[j] + '\n'
                    response = response + '--\n'

                    mutex_comment.acquire()
                    for j in range(0, len(comment)):
                        if (comment[j][0] == sn):
                            response = response + comment[j][1] + ': ' + comment[j][2] + '\n'
                    mutex_comment.release()
                    break

                if (i == len(post) - 1):
                    response = 'Post does not exist.'
            mutex_post.release()       
            c_tcp.send(response.encode())
        elif (cmd_list[0] == 'delete-post'):
            sn = int(cmd_list[1])
            if (login == False):
                c_tcp.send(b'Please login first.')
            else:
                mutex_post.acquire()
                if (sn in post_set):
                    for i in range(0, len(post)):
                        if (post[i][0] == sn):
                            if (post[i][4] == login_user):
                                post_set.remove(sn)
                                post.pop(i)
                                c_tcp.send(b'Delete successfully.')
                            else:
                                c_tcp.send(b'Not the post owner.')
                            break
                else:
                    c_tcp.send(b'Post does not exist.')
                mutex_post.release()
        elif (cmd_list[0] == 'update-post'):
            sn = int(cmd_list[1])
            op = cmd_list[2]

            new = ''
            for i in range(3, len(cmd_list)):
                new = new + cmd_list[i] + ' '
            new = new[0:len(new) - 1]

            if (login == False):
                c_tcp.send(b'Please login first.')
            else:
                mutex_post.acquire()
                if (sn in post_set):
                    for i in range(0, len(post)):
                        if (post[i][0] == sn):
                            if (post[i][4] == login_user):
                                if (op == '--title'):
                                    post[i][2] = new
                                else:
                                    post[i][3] = new
                                c_tcp.send(b'Update successfully.')
                            else:
                                c_tcp.send(b'Not the post owner.')
                            break
                else:
                    c_tcp.send(b'Post does not exist.')
                mutex_post.release()
        
        elif (cmd_list[0] == 'comment'):
            sn = int(cmd_list[1])
            comment_content = cmd_list[2]

            comment_content = ''
            for i in range(2, len(cmd_list)):
                comment_content = comment_content + cmd_list[i] + ' '
            comment_content = comment_content[0:len(comment_content) - 1]

            if (login == False):
                c_tcp.send(b'Please login first.')
            else:
                mutex_post.acquire()
                if (sn in post_set):
                    mutex_comment.acquire()
                    comment.append([sn, login_user, comment_content])
                    mutex_comment.release()
                    c_tcp.send(b'Comment successfully.')
                else:
                    c_tcp.send(b'Post does not exist.')
                mutex_post.release()
            

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


sql_conn.execute('''create table if not exists user
       ( username text primary key  not null,
       email    text not null,
       password text not null); ''')

sql_conn.execute('''create table if not exists key
       ( id integer primary key autoincrement,
       username text not null); ''')

sql_conn.execute('''create table if not exists board
       ( boardname text primary key not null,
       moderator text not null); ''')

sql_conn.execute('''create table if not exists post
       ( id integer primary key autoincrement,
        boardname text not null,
        title text not null,
        content text not null,
        author text not null,
        date text not null); ''')
      
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
