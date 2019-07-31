from environment import Environment
import time
env = Environment("test_dqn")
env.create_sockets_server()
print(env.reset())
print(env.step(0),' 0')
print(env.step(1),' 1')
print(env.step(2),' 2')
time.sleep(1)
print(env.step(0),' 0')
time.sleep(2)
print(env.step(1),' 1')
time.sleep(3)
print(env.step(2),' 2')