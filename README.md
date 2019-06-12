# simulink_python

使用simulink进行环境的模拟，使用python编写强化学习代码

## 快速开始

## 项目简介

* ##### tcp通信模块测试

  matlab与python之间使用tcp协议进行本地阻塞式通信，matlab接收python端信息后，才能使用simulink进行模拟（目前未解决模拟步长问题）。

  尝试将matlab和python分别作为客户端和服务端进行测试。其中，matlab作为客户端模拟100步时间为20s，python作为客户端模拟100步时间为2min。测试代码在[这里](./tcp_connection_attempt)。

  ![image](./assets/demo.png)

* ##### rl模块测试

  使用的是经典的[CartPole](./some_simulink_model/rlCartPoleSimscapeModel.slx)模型





### 参考链接

* [UDP&TCP通信测试](<https://blog.csdn.net/tiancai13579/article/details/53039437?locationNum=5&fps=1>)
* [调用simulink&通信](<https://github.com/sherrysherryli/simulink-python-communication>)
* [Create Simulink Environments for Reinforcement Learning](<https://www.mathworks.com/help/reinforcement-learning/ug/create-simulink-environments-for-reinforcement-learning.html>)
* [Load Predefined Simulink Environments](<https://www.mathworks.com/help/reinforcement-learning/ug/create-predefined-simulink-environments.html>)
* [Train DDPG Agent to Swing Up and Balance Cart-Pole System](<https://www.mathworks.com/help/reinforcement-learning/ug/train-ddpg-agent-to-swing-up-and-balance-cart-pole-system.html>)

