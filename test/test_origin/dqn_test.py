from environment import Environment
import os
import matplotlib.pyplot as plt
import numpy as np
import random
import torch
import torch.nn as nn
import torch.optim as optim
from torch.nn.utils import clip_grad_norm_


class ReplayBuffer:
    def __init__(self, column, max_size, batch_size):
        self.current_state = np.zeros((max_size, column), dtype=np.float32)
        self.next_state = np.zeros((max_size, column), dtype=np.float32)
        self.action = np.zeros(max_size, dtype=np.float32)
        self.reward = np.zeros(max_size, dtype=np.float32)
        self.done = np.zeros(max_size,dtype=np.float32)
        self.max_size, self.batch_size = max_size, batch_size
        self.size, self.current_index = 0, 0
    
    def store(self, current_state, action, next_state, reward, done):
        self.current_state[self.current_index] = current_state
        self.action[self.current_index] = action
        self.next_state[self.current_index] = next_state
        self.reward[self.current_index] = reward
        self.done[self.current_index] = done
        self.current_index = (self.current_index + 1) % self.max_size
        self.size = min(self.size + 1, self.max_size)
    
    def sample_batch(self):
        ptr = np.random.choice(self.size, self.batch_size)
        return dict(current_state=self.current_state[ptr],
                    next_state=self.next_state[ptr],
                    action=self.action[ptr],
                    reward=self.reward[ptr],
                    done=self.done[ptr]
        )

    def __len__(self):
        return self.size


class Network(nn.Module):
    def __init__(self, in_dim, out_dim):
        super(Network, self).__init__()
        
        self.layers = nn.Sequential(
            nn.Linear(in_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, out_dim)
        )
    def forward(self,x):
        return self.layers(x)


min_epsilon = 0.05
max_epsilon = 1
epsilon_decay = 80
epsilon_episode = lambda episode : min_epsilon + np.exp(-episode / epsilon_decay)*0.95


env = Environment("test_you")
state_space = 3
action_space = 3

batch_size = 32
max_size = 1000
memory = ReplayBuffer(state_space, max_size, batch_size)

device = torch.device("cuda:1" if torch.cuda.is_available() else "cpu")

network = Network(state_space,action_space).to(device)
target_network = Network(state_space,action_space).to(device)
target_network.load_state_dict(network.state_dict())
target_network.eval()

optimizer = optim.Adam(network.parameters())

gamma = 0.99
target_update = 200


def select_action(episode, state):
    if np.random.random_sample() > epsilon_episode(episode):
        selected_action = network(torch.FloatTensor(state).to(device)).argmax().detach().item()
    else:
        selected_action = random.randint(0,2)
    return selected_action


def train():
    samples = memory.sample_batch()
    state = torch.FloatTensor(samples["current_state"]).to(device).to(device)
    next_state = torch.FloatTensor(samples["next_state"]).to(device)
    action = torch.LongTensor(samples["action"].reshape(-1, 1)).to(device)
    reward = torch.FloatTensor(samples["reward"].reshape(-1, 1)).to(device)
    done = torch.FloatTensor(samples["done"].reshape(-1, 1)).to(device)
    
    current_Q_value = network(state).gather(1, action)
    next_Q_value = target_network(next_state).max(dim=1,keepdim=True)[0].detach()
    target = (reward + gamma*next_Q_value*(1 - done)).to(device)
    loss = ((target - current_Q_value).pow(2)).mean()
    optimizer.zero_grad()
    loss.backward()
    clip_grad_norm_(network.parameters(),1.0,norm_type=1) # Gradient clipping(增加稳定性)
    optimizer.step()
    return loss.item()


def plot_and_save(frame_idx, rewards, losses):
    rewards_factor = 10
    losses_smooth_x = np.arange(len(losses))
    losses_smooth = [np.mean(losses[i:i+rewards_factor]) if i > rewards_factor else np.mean(losses[0:i+1])
                     for i in range(len(losses))]
    rewards_smooth_x = np.arange(len(rewards))
    rewards_smooth = [np.mean(rewards[i:i+rewards_factor]) if i > rewards_factor else np.mean(rewards[0:i+1])
                      for i in range(len(rewards))]
    
    for i in range(len(losses)//3000):
        losses_smooth = losses_smooth[::2]
        losses_smooth_x = losses_smooth_x[::2]
    for i in range(len(rewards)//200):
        rewards_smooth = rewards_smooth[::2]
        rewards_smooth_x = rewards_smooth_x[::2]
        
    plt.figure(figsize=(18,10))   
    plt.subplot(211)
    plt.xlabel("episode")
    plt.ylabel("episode_rewards")
    plt.title('episode %s. rewards: %s' % (frame_idx, rewards[-1]))
    plt.plot(rewards, label="Rewards",color='lightsteelblue',linewidth='1')
    plt.plot(rewards_smooth_x, rewards_smooth, 
             label="Smoothed_Rewards",color='darkorange',linewidth='3')
    plt.legend(loc='best')
    
    plt.subplot(212)
    plt.title('loss')
    plt.plot(losses,label="Losses",color='lightsteelblue',linewidth='1')
    plt.plot(losses_smooth_x, losses_smooth, 
             label="Smoothed_Losses",color='darkorange',linewidth='3')
    plt.legend(loc='best')
    
    plt.savefig("dqn_test.png")

all_rewards = []
losses = []
update_count = 0

env.create_sockets_server()
state = env.reset()
for episode in range(200):
    rewards = 0
    for i in range(100):
        action = select_action(episode, state)
        next_state, reward, done, _ = env.step(action)
        print("episode:",episode,"state:",next_state,"reward:", reward,"action:",action )
        memory.store(state, action, next_state, reward, done)
        state = next_state
        rewards += reward
        #if done:
            #break
        if len(memory) > batch_size:
            loss = train()
            update_count += 1
            losses.append(loss)
            if update_count % target_update == 0:
                target_network.load_state_dict(network.state_dict())     
    all_rewards.append(rewards)
    plot_and_save(episode , [round(all_rewards[i], 3) for i in range(len(all_rewards))], losses)