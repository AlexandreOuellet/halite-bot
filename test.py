import pickle
import numpy as np
import os

# [distance, friendly, enemy, neutral, distanceSquared, health, NeutralCapacity, enemeyDockedShip, friendlyDockedShip]
planetWeights = np.random.rand(9)

# [distance, friendly, enemy, neutral, health, distanceSquared, docked, undocked]
shipWeights = np.random.rand(8)

LEARNING_RATE = 1

for i in range(0, len(planetWeights)):
    rand = ((random.random()-0.5)  * 2) * LEARNING_RATE
    planetWeights[i] = rand
for i in range(0, len(shipWeights)):
    rand = ((random.random()-0.5)  * 2) * LEARNING_RATE
    shipWeights[i] = rand


version = 0
dir = './v/{}/'.format(version)
    
if os.path.exists(dir) == False:
    os.makedirs(dir)
pickle.dump(planetWeights, open(dir+'planetWeights', 'wb'))
pickle.dump(shipWeights, open(dir+'shipWeights', 'wb'))

