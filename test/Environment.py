import socket
import sys
import struct
import array
import time

class Environment:
    def __init__(self, env_name):
        self.env_name = env_name
        self.sendConn = 0 # socket 发送端对象
        self.send_and_recv_host = 'localhost'
        self.sendPort = 50000
        self.recvConn = 0 # socket 接收数据的对象
        self.recvPort = 50001

        self.current_state = [0,0,0,0,0,0]

    # 创建socket服务
    def create_sockets_server(self):

        # 创建发送端socket服务
        sockets_server_send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sockets_server_send.bind((self.send_and_recv_host, self.sendPort))
        print('服务端端口绑定成功')

        sockets_server_send.listen(1)
        print("等待25秒,客户端向服务端 %d 发来的回应" %(self.sendPort))
        sockets_server_send.settimeout(25)
        
        try:
            self.sendConn, addr = sockets_server_send.accept()
        except socket.timeout:
            print("连接超时")
            sys.exit()
        print("服务端建立连接成功！地址 :%d ,发送端端口号 :%d" % (addr, self.sendPort))

        # 创建接收端socket服务
        sockets_server_recv = socket(socket.AF_INET, socket.SOCK_STREAM)
        sockets_server_recv.bind((self.send_and_recv_host, self.recvPort))
        print("接收端端口绑定成功")
        
        sockets_server_recv.listen(1)
        self.recvConn, addr = sockets_server_recv.accept()
        print("接收端连接成功！地址 :%d ,接收端端口号 :%d" % (addr, self.recvPort))

    # 发送动作值simulink
    def send_action(self, action):
        action = struct.pack("I", action)
        self.sendConn.sendall(action)

    # 接收来自simulink的状态信息
    def receive_state(self):
        data = self.recvConn.recv(2048)
        data = array.array('d', data)
        return data

    def step(self, action):
        self.send_action(action)

    def reset(self):
#可修改
        self.send_action(0)
        time.sleep(0.1)
        env_values = self.receive_state()
        if env_values is not None:
            self.current_state = env_values
            print("当前状态为 :T1:%d,T2:%d,T3:%d,T4:%d,T5:%d,T6:%d," % (self.current_state[0],
                    self.current_state[1],self.current_state[2],self.current_state[3],self.current_state[4],self.current_state[5]))
        return self.current_state
            
        