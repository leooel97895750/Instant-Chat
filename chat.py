# -*- coding: utf-8 -*-
"""
Created on Wed Oct  2 18:31:24 2019

@author: leooe
"""
import argparse, socket
import threading
import json
BUFSIZE = 65536
EOF = 'oo'
# 接收data的thread
class Myrec(threading.Thread):
    def __init__(self, sock):
        threading.Thread.__init__(self)
        self.sock = sock
    def run(self):
        global StopChat
        global EOF
        while True:
            data = self.sock.recv(BUFSIZE).decode('UTF-8')
            if data == EOF:
                self.sock.sendall(EOF.encode('UTF-8'))
                break
            else:
                print(data)

# 送出data的thread
class Mysend(threading.Thread):
    def __init__(self, sock):
        threading.Thread.__init__(self)
        self.sock = sock
    def run(self):
        while True:
            msg = input()
            self.sock.sendall(msg.encode('UTF-8'))
        
def server(host, port):
    # 將port綁定，並且連接registrar提供暱稱、IP、Port
    serverName = input('please enter your name: ')
    serverPort = input('please enter your port number: ')
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind( ('127.0.0.1', int(serverPort)) )
    sock.connect( (host, port) )
    print('Connected to registrar', sock.getpeername() )
    sock.sendall(serverName.encode('UTF-8'))
    sock.close()
    
    # 開啟listeningSock等待連線
    listeningSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listeningSock.bind(('127.0.0.1', int(serverPort)))
    listeningSock.listen(1)
    sock2, sockname = listeningSock.accept()
    print('Connected to', sockname, 'start chatting!')
    
    #創造接收、送出的thread、開始聊天
    myrec = Myrec(sock2)
    mysend = Mysend(sock2)
    myrec.daemon = True
    mysend.daemon = True
    try:
        myrec.start()
        mysend.start()
        myrec.join()
    except KeyboardInterrupt:
        pass
    
    #server對registrar發出un-register
    sock3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock3.bind( ('127.0.0.1', int(serverPort)) )
    sock3.connect( (host, port) )
    sock3.sendall(("server").encode('UTF-8'))
    sock3.close()
    
    print('press key to exit')
    sock2.close()

def client(host, port):
    # 連接registrar取得server連線資料表
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect( (host, port) )
    print('Connected to', sock.getpeername() )
    sock.sendall('client'.encode('UTF-8'))
    userDict = json.loads(sock.recv(BUFSIZE).decode('UTF-8'))
    userList = [(k,v) for k,v in userDict.items()]
    for i in range(len(userList)):
        print(str(i+1)+'.', userList[i][0], str(userList[i][1]).replace('[', '(').replace(']', ')'))
    sock.close()
    
    # 輸入連線對象，並創造sock連線至server
    serverNum = int(input('choose one of the numbers: '))
    serverIp = userList[serverNum-1][1][0]
    serverPort = userList[serverNum-1][1][1]
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect( (serverIp, serverPort) )
    print('Connected to', sock.getpeername(), 'start chatting!')
    
    #創造接收、送出的thread
    myrec = Myrec(sock)
    mysend = Mysend(sock)
    myrec.daemon = True
    mysend.daemon = True
    try:
        myrec.start()
        mysend.start()
        myrec.join()
    except KeyboardInterrupt:
        pass
    
    print('press key to exit')
    sock.close()

def registrar(host, port):
    # 記錄註冊的連線資訊
    userDict = {}
    
    # 不斷接收連線，並判斷是client或server
    while True:
        listeningSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listeningSock.bind((host, port))
        listeningSock.listen(1)
        sock, sockname = listeningSock.accept()
        identity = sock.recv(BUFSIZE).decode('UTF-8')
        if identity == 'client':
            sock.sendall(json.dumps(userDict).encode('UTF-8'))
        elif identity == 'server':
            username = list(userDict.keys())[list(userDict.values()).index(sockname)]
            del userDict[username]
            print('un-register', username, sockname)
        else: 
            userDict[identity] = sockname
            print('register', identity, sockname)
        
        listeningSock.close()
        sock.close()

if __name__ == '__main__':
    choices = {'client': client, 'server': server, 'registrar': registrar}
    parser = argparse.ArgumentParser(description='Chat over TCP')
    parser.add_argument('role', choices=choices, help='which role to play')
    parser.add_argument('host', help='interface the server listens at; host the client sends to')
    parser.add_argument('-p', metavar='PORT', type=int, default=1060, help='TCP port (default 1060)')
    args = parser.parse_args()
    function = choices[args.role]
    function(args.host, args.p)