import logging

import numpy as np

import keras
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.layers import Embedding
from keras import optimizers

from keras.layers import Dense, Activation

learning_rate = 0.001
starting_explore_prob = 0.05
num_games_to_play = 50

class QLearning:

    def __init__(self, num_inputs, num_actions, weight_filename):
        self.gameX = np.zeros(shape=(1,num_inputs+num_actions))
        self.gameY = np.zeros(shape=(1,1))

        self.weight_filename = weight_filename
        self.num_actions = num_actions
        self.num_inputs = num_inputs
        self.num_steps = 0

        self.possible_actions = np.arange(0, num_actions)

        # self.actions_1_hot = np.zeros((self.num_inputs, num_actions))
        # logging.info(self.possible_actions.shape)
        # logging.info(self.actions_1_hot.shape)
        # self.actions_1_hot[np.arange(self.num_inputs), self.possible_actions] = 1

        #Initialize training data array 
        total_steps = 0
        dataX = np.zeros(shape=(1,self.num_inputs + self.num_actions))
        dataY = np.zeros(shape=(1,1))

        #Initialize Memory Array data array 
        memoryX = np.zeros(shape=(1,self.num_inputs + self.num_actions))
        memoryY = np.zeros(shape=(1,1))

        self.model = Sequential()
        #model.add(Dense(num_env_variables+num_env_actions, activation='tanh', input_dim=dataX.shape[1]))
        self.model.add(Dense(512, activation='relu', input_dim=dataX.shape[1]))
        self.model.add(Dense(dataY.shape[1]))

        opt = optimizers.adam(lr=learning_rate)

        self.model.compile(loss='mse', optimizer=opt, metrics=['accuracy'])


    def getAction(self, state):
        #Calculate probability to take deterministic action vs random action (epsilon)
        prob = np.random.rand(1)
        explore_prob = starting_explore_prob-(starting_explore_prob/num_games_to_play)*self.num_steps
        utility_possible_actions = np.zeros(shape=(self.num_actions))

        self.num_steps += 1
        #Chose between prediction and chance
        if prob < explore_prob:
            #take a random action
            return np.random.rand() * len(utility_possible_actions)
            #print("taking random action",a, "at total_steps" , total_steps)
            #print("prob ", prob, "explore_prob", explore_prob)
        else:
            for i in range(0, self.num_actions):
                utility_possible_actions[i] = self.predictTotalRewards(state, i)

            return np.argmax(utility_possible_actions)


    #This function predicts the reward that will result from taking an "action" at a state "qstate"
    def predictTotalRewards(self, qstate, action):
        # potentialActions = np.zeros(shape=(self.num_actions))
        # logging.info("potentialActions : %s", potentialActions)
        # qs_a = np.concatenate((qstate, potentialActions), axis=0)
        # logging.info("qs_a : %s", qs_a)
        # predX = np.zeros(shape=(1, self.num_actions + self.num_inputs))
        # logging.debug("predX : %s", predX)
        
        # predX[0] = qs_a

        # #print("trying to predict reward at qs_a", predX[0])
        # pred = self.model.predict(predX[0].reshape(1,predX.shape[1]))
        # remembered_total_reward = pred[0][0]
        return 0

    def setPerception(self, state, action, reward, terminal):
        # self.gameX = np.vstack((self.gameX,qs_a))
        # self.gameY = np.vstack((self.gameY,np.array([reward])))

        return None

    def saveWeight(self):
        #Save model
        print("Saving weights")
        self.model.save_weights(self.weight_filename)
