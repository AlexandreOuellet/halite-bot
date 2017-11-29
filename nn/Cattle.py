import random
import numpy as np
from collections import deque

import keras
from keras.models import Sequential, Model
from keras.layers import Dense, Input, Embedding, Conv2D, Flatten, Activation, MaxPooling2D
from keras.optimizers import Adam
from keras.utils import to_categorical

import logging
import pickle
import os.path

EPISODES = 1000


class Cattle:
    def __init__(self, guylaine_input_size, ship_input_size, output_size, name):
        self.name = name
        self.guylaine_input_size = guylaine_input_size
        self.ship_input_size = ship_input_size
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
        # inputs = Input(shape=(self.state_size,self.state_channels),name='states_input')
        # x = Dense(24, input_dim=self.state_size, activation='relu')(inputs)
        # x = Dense(24, activation='relu')(x)

        # guylaine_input = Input(shape=(784,))

        guylaine_input = Input(shape=(self.guylaine_input_size,), name='ship_guylaine_input')

        ship_input = Input(shape=(self.ship_input_size,), name='ship_input')
        
        x = keras.layers.concatenate([guylaine_input, ship_input])

        x = Dense(64, activation='relu')(x)
        x = Dense(64, activation='relu')(x)
        x = Dense(64, activation='relu')(x)
        ship_output = Dense(self.output_size, activation='sigmoid', name='cattle_output')(x)

        model = Model(inputs=[guylaine_input, ship_input], outputs=ship_output)

        model.compile(loss='mse',
                      optimizer=Adam(lr=self.learning_rate))
        return model

    def remember(self, guylaine_output, ship_state, action, reward, next_guylaine_output, next_ship_state, done):
        self.memory.append(guylaine_output, ship_state, action, reward, next_guylaine_output, next_ship_state, done)

    def act(self, guylaine_output, ship_input, force_predict = False):
        if np.random.rand() <= self.epsilon and force_predict == False:
            return random.randrange(self.output_size)

        t = ship_input.reshape(1, ship_input.shape[0])
        act_values = self.model.predict({'ship_guylaine_input': guylaine_output, 'ship_input': t})
        return np.argmax(act_values)

    # def replay(self, batch_size):
    #     minBatchSize = batch_size
    #     if (len(self.memory) < batch_size):
    #         minBatchSize = len(self.memory)

    #     minibatch = random.sample(self.memory, minBatchSize)
    #     for guylaine_output, ship_state, action, reward, next_guylaine_output, next_ship_state in minibatch:
    #         target = reward

    #         if not done:
    #                 target = (reward + self.gamma * self.act(next_guylaine_output, next_ship_state, True))

    #         target_f = self.act(guylaine_output, ship_state, True)
            
    #         action_index = np.argmax(action)

    #         target_f[0][action_index] = target
    #         self.model.fit(state, target_f, epochs=1, verbose=0)
    #     if self.epsilon > self.epsilon_min:
    #         self.epsilon *= self.epsilon_decay

    def load(self):
        if os.path.isfile(self.name):
            self.model.load_weights(self.name)
        if os.path.isfile(self.name + '_memory'):
            self.memory = pickle.load(open(self.name + '_memory', 'rb'))
        if os.path.isfile(self.name + '_epsilon'):
            self.epsilon = pickle.load(open(self.name + '_epsilon', 'rb'))

    def save(self):
        self.model.save_weights(self.name)
        pickle.dump(self.memory, open(self.name + '_memory', 'wb'))
        pickle.dump(self.epsilon, open(self.name + '_epsilon', 'wb'))