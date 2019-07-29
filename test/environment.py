import socket
import sys
import struct
import array
import time
import random

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
        print('bind server port success')

        sockets_server_send.listen(1)
        print("Wait 20 seconds for a response from client to server {} ".format (self.sendPort))
        sockets_server_send.settimeout(20)
        
        try:
            self.sendConn, addr = sockets_server_send.accept()
        except socket.timeout:
            print("connection timeout")
            sys.exit()
        print("Server connnection success ! Address :{} , port :{}".format(addr, self.sendPort))

        # 创建接收端socket服务
        sockets_server_recv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sockets_server_recv.bind((self.send_and_recv_host, self.recvPort))
        print("The receiver port binding success")
        
        sockets_server_recv.listen(1)
        self.recvConn, addr = sockets_server_recv.accept()
        print("receiving connect success！Address :{} ,port :{}".format(addr, self.recvPort))

    # 发送动作值simulink
    def _send_action(self, action):
        action = struct.pack("I", action)
        self.sendConn.sendall(action)

    # 接收来自simulink的状态信息
    def _receive_state(self):
        data = self.recvConn.recv(2048)
        data = array.array('d', data)
        return data

    # 计算奖励值
    def _calculate_reward(self):
        T1, Tmix, Treturn = self.current_state[0],self.current_state[1],self.current_state[2]
        room_goal = 22 # 房间一的标准温度
        room_LL = 15 # lower limit
        room_UL = 29 # Upper limit
        Tmix_LL = 15 # Lower limit
        Tmix_UL = 44 # Upper limit

        distance = abs(room_goal - T1)
        if distance > 7 or Tmix < Tmix_LL or Tmix > Tmix_UL:
            reward = -1
        elif 0.5 < distance <= 7:
            reward = (7 - distance) * 0.5
        else:
            reward = 7 - distance

        return reward

    def step(self, action):
        self._send_action(action)
        time.sleep(0.1)
        env_values = self._receive_state()
        if env_values is not None:
            self.current_state = env_values
        reward = self._calculate_reward()
        done = False
        info = "normal"
        return self.current_state, reward, done, info
        # [self.current_state[0],self.current_state[1],self.current_state[2]]

    def reset(self):
        self._send_action(random.randint(0,2))
        time.sleep(0.1)
        env_values = self._receive_state()
        if env_values is not None:
            self.current_state = env_values
            print("current state T1: {} ,Tmix: {} ,Treturn: {} ".format(self.current_state[0],self.current_state[1],self.current_state[2]))
        return self.current_state
            
        