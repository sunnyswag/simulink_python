import socket
import time
import json

sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)#IPV4,TCP协议
sock.bind(('127.0.0.1', 54320))#绑定ip和端口，bind接受的是一个元组
sock.listen(5)#设置监听，其值阻塞队列长度，一共可以有5+1个客户端和服务器连接

print("start server")
connection, address = sock.accept()#等待客户请求
print("client ip is:",address)#打印客户端地址

s = bytes("start", encoding = "utf8")#输入start，开始
connection.send(s)
print(s)

while True:
    buf = connection.recv(1000)#接收数据
    print(buf)
    buf_l = json.loads(buf)
    control_signal=buf_l[0]*1
    # s=str(control_signal)
    connection.send(bytes(str(control_signal), encoding = "utf8"))
    #connection.close()#关闭连接
    time.sleep(1)
sock.close()#关闭服务器
