"""This is to be executed after there are some data within ./data/memory/."""

import os
import nn.Cattle as Cattle
import nnutils
import matplotlib.pyplot as plt
import pylab
import pickle

# os.environ['CUDA_VISIBLE_DEVICES'] = '-1' 

SHIP_INPUT_SIZE = 4
GUYLAINE_OUTPUT_SIZE = 100
CATTLE_OUTPUT_SIZE = 3 + nnutils.nbAngleStep * nnutils.nbSpeedStep # dock/undock/nothing
# guylaine = GuylaineV2.GuylainpeV2(nnutils.tileWidth, nnutils.tileHeight, len(state), guylaine_output_size, 'data/GuylaineV2' + sys.argv[1])
CATTLE = Cattle.Cattle((14, nnutils.tileWidth, nnutils.tileHeight), (SHIP_INPUT_SIZE,), CATTLE_OUTPUT_SIZE, 'data/CattleG1')
# guylaine_output = guylaine.act(state)

# guylaine.load()
history_losses = []

if os.path.isfile('./data/loss_historyv2'):
    history_losses = pickle.load(open('./data/loss_historyv2', 'rb'))

for file in os.listdir("./data/memory/"):
    fullFile = os.path.join("./data/memory/", file)
    print("Opening file %s", fullFile)
    CATTLE.load()

    CATTLE.loadMemory(fullFile)
    losses = (CATTLE.replay(128, 25))
    for loss in losses:
        history_losses.append(loss)

    CATTLE.save()
    pickle.dump(history_losses, open('./data/loss_historyv2', 'wb'))

    # os.remove(fullFile)

# plt.plot(history_losses)
# plt.title('model loss')
# plt.ylabel('loss')
# plt.xlabel('epoch')
# plt.show()