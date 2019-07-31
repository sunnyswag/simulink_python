import socket
import sys
import struct
import array
import time
import random
import numpy as np

class Environment:
    def __init__(self, env_name):
        self.env_name = env_name
        self.sendConn = 0 # socket 发送端对象
        self.send_and_recv_host = 'localhost'
        self.sendPort = 50000
        self.recvConn = 0 # socket 接收数据的对象
        self.recvPort = 50001

        self.current_state = [0,0,0]

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
        # 将返回的多次state信息求平均
        data = np.array(data).reshape(-1,3)
        data = list(data.mean(axis=0))
        data = [round(i, 2) for i in data]
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
        if Tmix < Tmix_LL or Tmix > Tmix_UL :
            if distance >= 7 :
                reward = -1 * distance * 0.1 
            else :
                reward = -1
        else :
            if distance >= 7 :
                reward = -1 * distance * 0.1
            elif 5 < distance < 7:
                reward = (7 - distance) * 0.2
            elif 1 < distance <= 5:
                reward = (7 - distance) * 0.5
            elif 0 <= distance <= 1:
                reward = 7 - distance

        return round(reward, 3)

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

    def reset(self):
        self._send_action(random.randint(0,2))
        time.sleep(0.1)
        env_values = self._receive_state()
        if env_values is not None:
            self.current_state = env_values
            print("current state T1: {} ,Tmix: {} ,Treturn: {} ".format(self.current_state[0],self.current_state[1],self.current_state[2]))
        return self.current_state
            
        