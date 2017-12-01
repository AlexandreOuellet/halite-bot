import random
import numpy as np
from collections import deque

# import keras
from keras.models import Sequential, Model
from keras.layers import Dense, Input, Embedding, Conv2D, Flatten, Activation, MaxPooling2D
from keras.optimizers import Adam
from keras.utils import to_categorical, plot_model

import nnutils

import logging
import pickle
import os.path

import time


EPISODES = 1000


class Cattle:
    def __init__(self, guylaine_input_shape, ship_input_shape, output_size, name):
        self.name = name
        self.guylaine_input_shape = guylaine_input_shape
        self.ship_input_shape = ship_input_shape
        self.output_size = output_size
        self.memory = deque(maxlen=2000)
        self.gamma = 0.95    # discount rate
        self.epsilon = 1.0  # exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.model = self._build_model()

    def _build_model(self):
        # Neural Net for Deep-Q learning Model
        guylaine_input = Input(shape=(self.guylaine_input_shape[0], self.guylaine_input_shape[1], self.guylaine_input_shape[2]), name='guylaine_input')
        guylaine = Conv2D(32, (3, 3), name='guylaine_conv1', activation='relu')(guylaine_input)
        guylaine = MaxPooling2D(pool_size=(2, 2), name='guylaine_maxpool1')(guylaine)

        guylaine = Conv2D(32, (3, 3), name='guylaine_conv2', activation='relu')(guylaine)
        guylaine = MaxPooling2D(pool_size=(2, 2), name='guylaine_maxpool2')(guylaine)

        # model.add(Convolution2D(64, (3, 3), name='conv3', data_format="channels_last"))
        # model.add(Activation('relu'))
        # model.add(MaxPooling2D(pool_size=(2, 2), name='maxpool3', data_format="channels_last"))

        guylaine = Flatten()(guylaine)

        guylaine = Dense(512, name='guylaine_dense1', activation='relu')(guylaine)

        guylaine_output = Dense(100, name='output', activation='sigmoid')(guylaine)

        ship_input = Input(shape=self.ship_input_shape, name='ship_input')
        
        cattle = keras.layers.concatenate([guylaine_output, ship_input])

        cattle = Dense(64, activation='relu', name='cattle_dense1')(cattle)
        cattle = Dense(64, activation='relu', name='cattle_dense2')(cattle)
        cattle = Dense(64, activation='relu', name='cattle_dense3')(cattle)
        ship_output = Dense(self.output_size, activation='sigmoid', name='cattle_output')(cattle)

        model = Model(inputs=[guylaine_input, ship_input], outputs=ship_output)

        model.compile(loss='mse', optimizer=Adam(lr=self.learning_rate))
        return model

    def remember(self, game_state, ship_state, action, reward, next_game_state, next_ship_state, done):
        self.memory.append((game_state, ship_state, action, reward, next_game_state, next_ship_state, done))

    def predict(self, game_state, ship_state, force_predict = False):
        if np.random.rand() <= self.epsilon and force_predict == False:
            return np.random.rand(self.output_size)

        game_state = game_state.reshape(1, game_state.shape[0], game_state.shape[1], game_state.shape[2])
        ship_state = ship_state.reshape(1, ship_state.shape[0])

        act_values = self.model.predict({'guylaine_input': game_state, 'ship_input': ship_state})
        return act_values

    def replay(self, batch_size):
        logging.debug("Training")

        minBatchSize = batch_size
        if (len(self.memory) < batch_size):
            minBatchSize = len(self.memory)

        guylaine_inputs = np.zeros(shape=(1, self.guylaine_input_shape[0], self.guylaine_input_shape[1], self.guylaine_input_shape[2]))
        ship_input = np.zeros(shape=(1, self.ship_input_shape[0]))

        minibatch = random.sample(self.memory, minBatchSize)

        game_state_batch = []
        ship_state_batch = []

        targets = np.zeros((len(minibatch), self.output_size))

        for i in range(0, len(minibatch)):
            logging.debug("Gathering data for batch i:%s", i)
            game_state, ship_state, action_taken, reward, next_game_state, next_ship_state, done = minibatch[i]

            game_state_batch.append(game_state)
            ship_state_batch.append(ship_state)
            targets[i] = self.predict(game_state, ship_state, True)
            targets[i][action_taken] = reward

            if not done:
                Q_sa = self.predict(next_game_state, next_ship_state, True)
                estimated_reward = np.max(Q_sa)
                targets[i][action_taken] = (reward + self.gamma * estimated_reward)
                
            # y_batch.append(target)

        logging.debug("Done gathering data for batch")
        if len(ship_state_batch) != 0:
            
            logging.debug("Fitting the model")
            self.model.fit({'guylaine_input': np.array(game_state_batch), 'ship_input': np.array(ship_state_batch)}, np.array(targets), batch_size=len(ship_state_batch), verbose=0)
            logging.debug("Done fitting the model")

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
            
        logging.debug("Training done.  epsilon: %s", self.epsilon)


    def load(self):
        if os.path.isfile('data/model'):
            self.model.load_weights('data/model')
        # if os.path.isfile(self.name + '_memory'):
        #     self.memory = pickle.load(open(self.name + '_memory', 'rb'))
        if os.path.isfile('data/epsilon'):
            self.epsilon = pickle.load(open('data/epsilon', 'rb'))

    def save(self):
        self.model.save_weights('data/model')
        pickle.dump(self.epsilon, open('data/epsilon', 'wb'))

    def loadMemory(self, fileName):
        if os.path.isfile(fileName):
            self.memory = pickle.load(open(fileName, 'rb'))


    def saveMemory(self):
        millis = int(round(time.time() * 1000))
        pickle.dump(self.memory, open('data/memory/' + str(millis), 'wb'))


