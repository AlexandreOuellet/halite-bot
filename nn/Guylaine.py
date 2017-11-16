import tensorflow as tf 
import numpy as np 
import random
from collections import deque 
import nnutils
import logging
import nn.dqn as dqn
import nn.qlearning as ql
from nn import dqnAgent

# Essentially the commander's NN that takes in the layers of the map, and outputs some "intents".
# CattleNN will then take Guylaine's output, take a ship's current state, and then select an action.
# Hopefully, through QLearning, CattleNN will be better able to control each ship, and interpret Guylaine's
# intent, and Guylaine's intent will become clearer to CattleNN
class Guylaine:

    def __init__(self, planetStates, shipStates, num_actions):
        self.actions = np.zeros(num_actions)
        self.planetsQLearn = [None] * len(planetStates)
        self.shipsQLearn = [None] * len(shipStates)

        for i in range(0, len(planetStates)):
        # for i in range(0, 1):
            self.planetsQLearn[i] = dqnAgent.DQNAgent(len(planetStates[i]), num_actions, "planets_" + str(i))

        for i in range(0, len(shipStates)):
        # for i in range(0, 1):
            self.shipsQLearn[i] = dqnAgent.DQNAgent(len(shipStates[i]), num_actions, "ships_" + str(i))
        
    def setPerception(self, planetStates, shipStates, actions, reward, nextPlanetStates, nextShipStates, terminal):
        for i in range(0, len(nextPlanetStates)):
        # for i in range(0, 1):
            self.planetsQLearn[i].remember(planetStates[i], actions, reward, nextPlanetStates[i], terminal)

        for i in range(0, len(nextShipStates)):
        # for i in range(0, 1):
            self.shipsQLearn[i].remember(shipStates[i], actions, reward, nextShipStates[i], terminal)

    def getAction(self, planetStates, shipStates):
        actions = []

        for i in range(0, len(planetStates)):
        # for i in range(0, 1):
            estimatedActionIndex = int(self.planetsQLearn[i].act(planetStates[i]))
            localActions = np.zeros(len(self.actions))
            localActions[estimatedActionIndex] = 1
            # if actions == None:
            #     actions = localActions
            # else:
            actions = np.append(actions, localActions)

        for i in range(0, len(shipStates)):
        # for i in range(0, 1):
            estimatedActionIndex = int(self.shipsQLearn[i].act(shipStates[i]))
            localActions = np.zeros(len(self.actions))
            localActions[estimatedActionIndex] = 1
            # if actions == None:
            #     actions = localActions
            # else:
            actions = np.append(actions, localActions, axis=0)

        reshapedActions = np.reshape(actions, (-1, len(self.actions)))
        actions = np.add.reduce(reshapedActions, 0)

        action_index = np.argmax(actions)

        return action_index

    def setInitState(self, planetStates, shipStates):
        return
        # # for i in range(0, len(planetStates)):
        # for i in range(0, 1):
        #     self.planetsQLearn[i].setInitState(planetStates[i])

        # # for i in range(0, len(shipStates)):
        # for i in range(0, 1):
        #     self.shipsQLearn[i].setInitState(shipStates[i])
        return None
    def save(self):
        for agent in self.planetsQLearn:
            agent.save()
        for agent in self.shipsQLearn:
            agent.save()

    def load(self):
        for agent in self.planetsQLearn:
            agent.load()
        for agent in self.shipsQLearn:
            agent.load()

    def replay(self, batch_size):
        logging.debug("Replaying match")
        for agent in self.planetsQLearn:
            agent.replay(batch_size)
        for agent in self.shipsQLearn:
            agent.replay(batch_size)