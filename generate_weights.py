import pickle
import sys
import os
import random

LEARNING_RATE = 0.1

def randomize_weight(version):
    dir = './v/{}/'.format(version)
    if os.path.isfile(dir+'planetWeights'):
        planetWeights = pickle.load(open(dir+'planetWeights', 'rb'))
    if os.path.isfile(dir+'shipWeights'):
        shipWeights = pickle.load(open(dir+'shipWeights', 'rb'))


    for i in range(0, len(planetWeights)):
        rand = ((random.random()-0.5)  * 2) * LEARNING_RATE
        planetWeights[i] += rand
    for i in range(0, len(shipWeights)):
        rand = ((random.random()-0.5)  * 2) * LEARNING_RATE
        shipWeights[i] += rand

    version += 1
    dir = './v/{}/'.format(version)
        
    if os.path.exists(dir) == False:
        os.makedirs(dir)
    pickle.dump(planetWeights, open(dir+'planetWeights', 'wb'))
    pickle.dump(shipWeights, open(dir+'shipWeights', 'wb'))


if __name__ == "__main__":
  version = int(sys.argv[1])
  randomize_weight(version)
