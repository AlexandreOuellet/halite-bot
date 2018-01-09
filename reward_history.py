import os
import matplotlib.pyplot as plt
import pickle

skip=0
reward_history = []


for file in os.listdir("./data/"):
    if "_totalRewards" not in file:
        continue
    
    fullFile = os.path.join("./data/", file)
    reward_history = pickle.load(open(fullFile, 'rb'))
    plt.plot(reward_history)

plt.title('reward history')
plt.ylabel('reward')
plt.xlabel('turns')
plt.show()