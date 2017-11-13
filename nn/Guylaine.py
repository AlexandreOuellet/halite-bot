import tensorflow as tf 
import numpy as np 
import random
from collections import deque 
import nnutils
import logging
import nn.dqn as dqn
import nn.qlearning as ql

# Essentially the commander's NN that takes in the layers of the map, and outputs some "intents".
# CattleNN will then take Guylaine's output, take a ship's current state, and then select an action.
# Hopefully, through QLearning, CattleNN will be better able to control each ship, and interpret Guylaine's
# intent, and Guylaine's intent will become clearer to CattleNN
class Guylaine:

    def __init__(self, planetStates, shipStates, num_actions):
        self.actions = np.zeros(num_actions)
        self.planetsQLearn = [None] * len(planetStates)
        self.shipsQLearn = [None] * len(shipStates)

        logging.info("creating planets AI")
        for i in range(0, len(planetStates)):
        # for i in range(0, 1):
            logging.info("planetStates index:", i)
            self.planetsQLearn[i] = ql.QLearning(len(planetStates[i]), num_actions, "planets_" + str(i))

        logging.info("creating ships AI")
        for i in range(0, len(shipStates)):
        # for i in range(0, 1):
            logging.info("shipStates index:", i)
            self.shipsQLearn[i] = ql.QLearning(len(shipStates[i]), num_actions, "ships_" + str(i))
        
    def setPerception(self, planetStates, shipStates, action, reward, terminal):
        # for i in range(0, len(planetStates)):
        for i in range(0, 1):
            self.planetsQLearn[i].setPerception(planetStates[i], action, reward, terminal)

        # for i in range(0, len(shipStates)):
        for i in range(0, 1):
            self.shipsQLearn[i].setPerception(shipStates[i], action, reward, terminal)
        return None

    def getAction(self, planetStates, shipStates):
        actions = None

        for i in range(0, len(planetStates)):
        # for i in range(0, 1):
            logging.debug("planetStates : ", planetStates[i])
            estimatedActionIndex = int(self.planetsQLearn[i].getAction(planetStates[i]))
            localActions = np.zeros(len(self.actions))
            localActions[estimatedActionIndex] = 1
            if actions == None:
                actions = localActions
            else:
                actions = np.append(actions, localActions)

        for i in range(0, len(shipStates)):
        # for i in range(0, 1):
            logging.debug("shipStates : ", planetStates[i])
            estimatedActionIndex = int(self.shipsQLearn[i].getAction(shipStates[i]))
            localActions = np.zeros(len(self.actions))
            localActions[estimatedActionIndex] = 1
            if actions == None:
                actions = localActions
            else:
                actions = np.append(actions, localActions, axis=1)

        # actions = np.add.reduce(actions, 0)
        logging.info(actions)

        action_index = random.randrange(self.actions)
        actions[action_index] = 1

        return actions

    def setInitState(self, planetStates, shipStates):
        return
        # # for i in range(0, len(planetStates)):
        # for i in range(0, 1):
        #     self.planetsQLearn[i].setInitState(planetStates[i])

        # # for i in range(0, len(shipStates)):
        # for i in range(0, 1):
        #     self.shipsQLearn[i].setInitState(shipStates[i])