import os
import matplotlib.pyplot as plt
import pickle

skip=0
history_losses = []

if os.path.isfile('./data/loss_historyv2'):
    history_losses = pickle.load(open('./data/loss_historyv2', 'rb'))

proper_history_losses = []
for i in range(skip, len(history_losses)):
    proper_history_losses.append(history_losses[i])

plt.plot(proper_history_losses)
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.show()