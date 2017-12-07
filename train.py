import nn.Cattle as Cattle
import os
import nnutils

ship_input_size = 4
guylaine_output_size = 100
cattle_output_size = 3 + nnutils.nbAngleStep * nnutils.nbSpeedStep # dock/undock/nothing
# guylaine = GuylaineV2.GuylaineV2(nnutils.tileWidth, nnutils.tileHeight, len(state), guylaine_output_size, 'data/GuylaineV2' + sys.argv[1])
cattle = Cattle.Cattle((14, nnutils.tileWidth, nnutils.tileHeight), (ship_input_size,), cattle_output_size, 'data/CattleG1')
# guylaine_output = guylaine.act(state)

# guylaine.load()
cattle.load()

for file in os.listdir("data/memory/"):
    fullFile = os.path.join("data/memory/", file)

    cattle.loadMemory(fullFile)
    cattle.replay(25)
    cattle.save()
    os.remove(fullFile)
