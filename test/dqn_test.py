from environment import Environment
env = Environment("test_dqn")
env.create_sockets_server()
print(env.reset())
print(env.step(0),' 0')
print(env.step(1),' 1')
print(env.step(2),' 2')