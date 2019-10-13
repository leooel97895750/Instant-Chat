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
            try:
                data = self.sock.recv(BUFSIZE).decode('UTF-8')
                if data == EOF:
                    self.sock.sendall(EOF.encode('UTF-8'))
                    break
                else:
                    print(data)
            except:
                pass

# 送出data的thread
class Mysend(threading.Thread):
    def __init__(self, sock):
        threading.Thread.__init__(self)
        self.sock = sock
    def run(self):
        global EOF
        while True:
            try:
                msg = input()
                self.sock.sendall(msg.encode('UTF-8'))
            except:
                self.sock.sendall(EOF.encode('UTF-8'))
        
def server(host, port):
    # 將port綁定，並且連接registrar提供暱稱、IP、Port
    localhost = '127.0.0.1'
    serverName = input('please enter your name: ')
    serverPort = port
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect( (host, 10529) )
    print('Connected to registrar', sock.getpeername() )
    if serverPort == 0:
        sock.sendall(('register '+serverName+' '+localhost+' randomPort').encode('UTF-8'))
        serverPort = int(sock.recv(BUFSIZE).decode('UTF-8'))
    else:
        sock.sendall(('register '+serverName+' '+localhost+' '+str(port)).encode('UTF-8'))
    sock.close()
    
    # 開啟listeningSock等待連線
    listeningSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listeningSock.bind((localhost, serverPort))
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
    try:
        myrec.join()
    except:
        pass
    
    #server對registrar發出un-register
    sock2.close()
    sock3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock3.connect( (host, 10529) )
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
    #print(userList)
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
    try:
        myrec.join()
    except:
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
        identity = sock.recv(BUFSIZE).decode('UTF-8').split()
        if identity[0] == 'client':
            sock.sendall(json.dumps(userDict).encode('UTF-8'))
        elif identity[0] == 'server':
            delip = userDict[identity[1]]
            del userDict[identity[1]]
            print('un-register', identity[1], delip)
        else: 
            #print(sockname)
            #print(type(sockname))
            if identity[3] == 'randomPort':
                userDict[identity[1]] = sockname
                print(sockname, sockname[1])
                sock.sendall(str(sockname[1]).encode('UTF-8'))
            else:
                userDict[identity[1]] = (identity[2], int(identity[3]))
            print('register', identity[1], userDict[identity[1]])
        
        listeningSock.close()
        sock.close()

if __name__ == '__main__':
    choices = {'client': client, 'server': server, 'registrar': registrar}
    parser = argparse.ArgumentParser(description='Chat over TCP')
    parser.add_argument('role', choices=choices, help='which role to play')
    parser.add_argument('host', help='interface the server listens at; host the client sends to')
    parser.add_argument('-p', metavar='PORT', type=int, default=10529, help='TCP port (default 10529)')
    args = parser.parse_args()
    function = choices[args.role]
    function(args.host, args.p)