import os
import matplotlib.pyplot as plt
import pickle
import numpy

skip=0
reward_history = []
all_reward_history = []


for file in os.listdir("./data/"):
    if "_totalRewards" not in file:
        continue
    
    fullFile = os.path.join("./data/", file)
    reward_history = pickle.load(open(fullFile, 'rb'))
    plt.plot(reward_history)
    all_reward_history.append(numpy.sum(reward_history))

plt.title('reward history')
plt.ylabel('reward')
plt.xlabel('turns')
plt.show()


plt.plot(all_reward_history)
plt.title('total rewards per games')
plt.ylabel('total reward')
plt.xlabel('game')
plt.show()
