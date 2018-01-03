"""This is to be executed after there are some data within ./data/memory/."""

import os
import nn.Cattle as Cattle
import nnutils

SHIP_INPUT_SIZE = 4
GUYLAINE_OUTPUT_SIZE = 100
CATTLE_OUTPUT_SIZE = 3 + nnutils.nbAngleStep * nnutils.nbSpeedStep # dock/undock/nothing
# guylaine = GuylaineV2.GuylainpeV2(nnutils.tileWidth, nnutils.tileHeight, len(state), guylaine_output_size, 'data/GuylaineV2' + sys.argv[1])
CATTLE = Cattle.Cattle((13, nnutils.tileWidth, nnutils.tileHeight), (SHIP_INPUT_SIZE,), CATTLE_OUTPUT_SIZE, 'data/CattleG1')
# guylaine_output = guylaine.act(state)

# guylaine.load()
CATTLE.load()

for file in os.listdir("./data/memory/"):
    fullFile = os.path.join("./data/memory/", file)

    CATTLE.loadMemory(fullFile)
    CATTLE.replay(5)
    CATTLE.save()
    os.remove(fullFile)
