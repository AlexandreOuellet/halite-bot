"""This is to be executed after there are some data within ./data/memory/."""

import os
import nn.CattleV2 as Cattle
import nnutils
import matplotlib.pyplot as plt
import pylab
import pickle

# os.environ['CUDA_VISIBLE_DEVICES'] = '-1' 
name = 'G1'
CATTLE = cattle = Cattle.Cattle((nnutils.input_size,), nnutils.output_size, name)

# guylaine.load()
history_losses = []

dir = "./{}/".format(name)
if os.path.isfile(dir + 'loss_historyv2'):
    history_losses = pickle.load(open(dir + 'loss_historyv2', 'rb'))

for file in os.listdir(dir + 'memory/'):
    fullFile = os.path.join(dir + "memory/", file)
    print("Opening file %s", file)
    CATTLE.load()

    CATTLE.loadMemory(file)
    losses = CATTLE.replay(32, 200, file)
    for loss in losses:
        history_losses.append(loss)

    CATTLE.save()
    pickle.dump(history_losses, open(dir + 'loss_historyv2', 'wb'))

    os.remove(fullFile)

# plt.plot(history_losses)
# plt.title('model loss')
# plt.ylabel('loss')
# plt.xlabel('epoch')
# plt.show()