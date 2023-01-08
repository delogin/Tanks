from itertools import count
import socket
import threading
from time import sleep, time
from tracemalloc import start
id = 0
cons = []
started = 0
timeleft = 360
def timer():
    global timeleft, started
    while True:
        if started == 1:
            sleep(1)
            timeleft-=1
            a = 'timeleft;' + str(timeleft) 
            while len(a)<20:
                a+='|'
            for i in range(len(cons)):
                cons[i].send(bytes(a, encoding="UTF-8"))
                if timeleft <0:
                    cons[i].close()
def sending(conn, id):
    global started
    while True:
        if len(cons)>1:
            if started == 0:
                print("start game")
                sleep(5)
                started = 1
                number_player = id+1
                pnum = 'start;'+str(number_player)+'|||||||||||||'
                conn.send(bytes(pnum, encoding="UTF-8"))
            else:
                data=conn.recv(20)  
                if data != b'':
                    print(data)
                othsock = 0
                if id == 0:
                    othsock = 1
                elif id == 1:
                    othsock = 0
                cons[othsock].send(data)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('127.0.0.1', 18000))
s.listen(10)
print('Сервер запустился и готов к работе')
th1 = threading.Thread(target=timer)
th1.start()
while True:
    conn, addr_client = s.accept()
    print(addr_client, conn)
    cons.append(conn)
    th=threading.Thread(target=sending, args=[conn, id])
    th.start()
    print('started')
    id += 1
    if id > 2:
        conn.close()


# a = '123123123'

# while len(a) < 20:
#     a += '|'

# print('123123123')
# print(a)
# print(a.replace('|', ''))
