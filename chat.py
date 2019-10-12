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
        try:
            while True:
                msg = input()
                self.sock.sendall(msg.encode('UTF-8'))
        except KeyboardInterrupt:
            self.sock.sendall('oo'.encode('UTF-8'))
        
def server(host, port):
    # 將port綁定，並且連接registrar提供暱稱、IP、Port
    localhost = '127.0.0.1'
    serverName = input('please enter your name: ')
    serverPort = input('please enter your port number: ')
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind( (localhost, int(serverPort)) )
    sock.connect( (host, port) )
    print('Connected to registrar', sock.getpeername() )
    sock.sendall(serverName.encode('UTF-8'))
    sock.close()
    
    # 開啟listeningSock等待連線
    listeningSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listeningSock.bind((localhost, int(serverPort)))
    listeningSock.listen(1)
    sock2, sockname = listeningSock.accept()
    print('Connected to', sockname, 'start chatting!')
    
    #創造接收、送出的thread、開始聊天
    myrec = Myrec(sock2)
    mysend = Mysend(sock2)
    myrec.daemon = True
    mysend.daemon = True
    myrec.start()
    mysend.start()
    myrec.join()
    
    #server對registrar發出un-register
    sock2.close()
    sock3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock3.connect( (host, port) )
    sock3.sendall(("server "+serverName).encode('UTF-8'))
    sock3.close()
    
    print('press key to exit')
    

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
    myrec.start()
    mysend.start()
    myrec.join()
    
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
        identity = sock.recv(BUFSIZE).decode('UTF-8').split()
        if identity[0] == 'client':
            sock.sendall(json.dumps(userDict).encode('UTF-8'))
        elif identity[0] == 'server':
            delip = userDict[identity[1]]
            del userDict[identity[1]]
            print('un-register', identity[1], delip)
        else: 
            userDict[identity[0]] = sockname
            print('register', identity[0], sockname)
        
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