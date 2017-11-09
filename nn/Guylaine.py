import tensorflow as tf 
import numpy as np 
import random
from collections import deque 
import nnutils
import logging
import nn.dqn as dqn

# Essentially the commander's NN that takes in the layers of the map, and outputs some "intents".
# CattleNN will then take Guylaine's output, take a ship's current state, and then select an action.
# Hopefully, through QLearning, CattleNN will be better able to control each ship, and interpret Guylaine's
# intent, and Guylaine's intent will become clearer to CattleNN
class Guylaine:

    def __init__(self, planetStates, shipStates, actions):
        self.actions = actions
        self.planetsDQN = [None] * len(planetStates)
        self.shipsDQN = [None] * len(shipStates)

        logging.info("creating planets DQN")
        # for i in range(0, len(planetStates)):
        for i in range(0, 1):
            logging.info("planetStates index:", i)
            self.planetsDQN[i] = dqn.DQN(actions)

        logging.info("creating ships DQN")
        # for i in range(0, len(shipStates)):
        for i in range(0, 1):
            logging.info("shipStates index:", i)
            self.shipsDQN[i] = dqn.DQN(actions)
        
    def setPerception(self, planetStates, shipStates, action, reward, terminal):
        # for i in range(0, len(planetStates)):
        for i in range(0, 1):
            self.planetsDQN[i].setPerception(planetStates[i], action, reward, terminal)

        # for i in range(0, len(shipStates)):
        for i in range(0, 1):
            self.shipsDQN[i].setPerception(shipStates[i], action, reward, terminal)
        return None

    def getAction(self):
        actions = np.zeros([self.actions, len(self.planetsDQN) + len(self.shipsDQN)])

        # for i in range(0, len(self.planetsDQN)):
        for i in range(0, 1):
            np.append(actions, self.planetsDQN[i].getAction(), axis=0)

        # for i in range(0, len(self.shipsDQN)):
        for i in range(0, 1):
            np.append(actions, self.shipsDQN[i].getAction(), axis=0)

        # actions = np.add.reduce(actions, 0)

        action_index = random.randrange(self.actions)
        actions[action_index] = 1

        return actions

    def setInitState(self, planetStates, shipStates):
        # for i in range(0, len(planetStates)):
        for i in range(0, 1):
            self.planetsDQN[i].setInitState(planetStates[i])

        # for i in range(0, len(shipStates)):
        for i in range(0, 1):
            self.shipsDQN[i].setInitState(shipStates[i])