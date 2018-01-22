import os
import sys
import operator
from hlt import entity as ntt


# class RedirectStdStreams(object):
#     def __init__(self, stdout=None, stderr=None):
#         self._stdout = stdout or sys.stdout
#         self._stderr = stderr or sys.stderr

#     def __enter__(self):
#         self.old_stdout, self.old_stderr = sys.stdout, sys.stderr
#         self.old_stdout.flush(); self.old_stderr.flush()
#         sys.stdout, sys.stderr = self._stdout, self._stderr

#     def __exit__(self, exc_type, exc_value, traceback):
#         self._stdout.flush(); self._stderr.flush()
#         sys.stdout = self.old_stdout
#         sys.stderr = self.old_stderr

# devnull = open(os.devnull, 'w')

# with RedirectStdStreams(stdout=devnull, stderr=devnull):
import random
import numpy as np
np.set_printoptions(threshold=np.nan)

import nnutils

import pickle
import os.path

import time
import logging

LEARNING_RATE = 0.01

class Guylaine:
    def __init__(self, version, planetWeights=[], shipWeights=[]):
        if len(planetWeights) == 0:
            planetWeights = np.random.rand(9)
        self.planetWeights = planetWeights # [distance, friendly, enemy, neutral, distanceSquared, health, availableDockingSpot, enemeyDockedShip, friendlyDockedShip]
        if len(shipWeights) == 0:
            shipWeights = np.random.rand(8)
        self.shipWeights = shipWeights # [distance, friendly, enemy, neutral, health, distanceSquared, docked, undocked]
        self.version = int(version)
        
    def predict(self, ship, game_map):
        myId = game_map.get_me().id

        allEntities = game_map.nearby_entities_by_distance(ship)
        keysByDistance = sorted(allEntities.keys(), reverse=False)

        entityIdByValue = {}
        for k in keysByDistance:
            for entity in [entity for entity in allEntities[k] if type(entity) is ntt.Planet]:
                planetState = []
                planetState.append(k)
                if entity.owner == None:
                    planetState.append(0)
                    planetState.append(0)
                    planetState.append(1)
                    planetState.append(1/(k*k))
                    planetState.append(entity.health)
                    planetState.append(entity.num_docking_spots)
                    planetState.append(0)
                    planetState.append(0)
                elif entity.owner.id == myId:
                    planetState.append(1)
                    planetState.append(0)
                    planetState.append(0)
                    planetState.append(1/(k*k))
                    planetState.append(entity.health)
                    planetState.append(entity.num_docking_spots)
                    planetState.append(0)
                    planetState.append(len(entity.all_docked_ships()))
                else:
                    planetState.append(0)
                    planetState.append(1)
                    planetState.append(0)
                    planetState.append(1/(k*k))
                    planetState.append(entity.health)
                    planetState.append(entity.num_docking_spots)
                    planetState.append(len(entity.all_docked_ships()))
                    planetState.append(0)


                assert len(self.planetWeights) == len(planetState)

                value = 0
                
                for i in range(0, len(self.planetWeights)):
                    coef = self.planetWeights[i]
                    value += planetState[i] * coef

                entityIdByValue[value] = entity
        
        ships = []
        for k in keysByDistance:
            for entity in [entity for entity in allEntities[k] if type(entity) is ntt.Ship]:
                if entity.id == ship.id:
                    continue
                shipState = []
                shipState.append(k)
                if entity.owner.id == myId:
                    shipState.append(1)
                    shipState.append(0)
                    shipState.append(0)
                    shipState.append(entity.health)
                    shipState.append(1/(k*k))
                    if (entity.DockingStatus == ntt.Ship.DockingStatus.DOCKED):
                        shipState.append(1)
                        shipState.append(0)
                    else:
                        shipState.append(0)
                        shipState.append(1)
                else:
                    shipState.append(0)
                    shipState.append(1)
                    shipState.append(0)
                    shipState.append(entity.health)
                    shipState.append(1/(k*k))
                    if (entity.DockingStatus == ntt.Ship.DockingStatus.DOCKED):
                        shipState.append(1)
                        shipState.append(0)
                    else:
                        shipState.append(0)
                        shipState.append(1)

                # logging.debug("shipWeights :%s", self.shipWeights)
                # logging.debug("shipState :%s", shipState)
                assert len(self.shipWeights) == len(shipState)

                value = 0
                
                for i in range(0, len(self.shipWeights)):
                    coef = self.shipWeights[i]
                    value += shipState[i] * coef

                entityIdByValue[value] = entity
    

        keysByValue = sorted(entityIdByValue.keys(), reverse=True)
        entity = entityIdByValue[keysByValue[0]]

        # target = sorted_x[0]
        # entity = game_map.get_ship(target)
        # if (entity == None):
        #     entity = game_map.get_planet(target)

        assert entity != None
        return entity


    def load(self, randomize=True):
        dir = './v/{}/'.format(self.version)
        if os.path.exists(dir) == False:
            os.makedirs(dir)
        if os.path.isfile(dir+'planetWeights'):
            self.planetWeights = pickle.load(open(dir+'planetWeights', 'rb'))
        if os.path.isfile(dir+'shipWeights'):
            self.shipWeights = pickle.load(open(dir+'shipWeights', 'rb'))

        if randomize:
            for i in range(0, len(self.planetWeights)):
                rand = ((random.random()-0.5)  * 2) * LEARNING_RATE
                self.planetWeights[i] += rand
            for i in range(0, len(self.shipWeights)):
                rand = ((random.random()-0.5)  * 2) * LEARNING_RATE
                self.shipWeights[i] += rand

    def save(self, newVersion):
        if newVersion:
            self.version += 1
        dir = './v/{}/'.format(self.version)
        
        if os.path.exists(dir) == False:
            os.makedirs(dir)
        pickle.dump(self.planetWeights, open(dir+'planetWeights', 'wb'))
        pickle.dump(self.shipWeights, open(dir+'shipWeights', 'wb'))