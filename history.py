import os
import matplotlib.pyplot as plt
import pickle

skip=10000
history_losses = []

if os.path.isfile('./G1/loss_historyv2'):
    history_losses = pickle.load(open('./G1/loss_historyv2', 'rb'))

proper_history_losses = []
for i in range(skip, len(history_losses)):
    proper_history_losses.append(history_losses[i])

plt.plot(proper_history_losses)
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.show()