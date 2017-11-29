import random
import numpy as np
from collections import deque
from keras.models import Sequential, Model
from keras.layers import Dense, Input, Conv2D, Flatten, Activation, MaxPooling2D
from keras.optimizers import Adam

import logging
import pickle
import os.path

EPISODES = 1000
action_size = 10


class GuylaineV2:
    def __init__(self, state_width, state_height, state_channels, output_size, name):
        self.name = name
        self.state_width = state_width
        self.state_height = state_height
        self.state_channels = state_channels
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
        model = Sequential()
        
        model.add(Conv2D(32, (3, 3), data_format="channels_last",
            input_shape=(self.state_channels, self.state_width, self.state_height), name='conv1'))
        model.add(Activation('relu'))
        model.add(MaxPooling2D(pool_size=(2, 2), name='maxpool1', data_format="channels_last"))

        model.add(Conv2D(32, (3, 3), name='conv2', data_format="channels_last"))
        model.add(Activation('relu'))
        model.add(MaxPooling2D(pool_size=(2, 2), name='maxpool2', data_format="channels_last"))

        # model.add(Convolution2D(64, (3, 3), name='conv3', data_format="channels_last"))
        # model.add(Activation('relu'))
        # model.add(MaxPooling2D(pool_size=(2, 2), name='maxpool3', data_format="channels_last"))

        model.add(Flatten())

        model.add(Dense(512, name='dense1'))
        model.add(Activation('relu'))

        model.add(Dense(self.output_size, name='output'))
        model.add(Activation('sigmoid'))

        model.compile(loss='mse',
                      optimizer=Adam(lr=self.learning_rate))
        return model

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state):
        if np.random.rand() <= self.epsilon:
            return np.random.rand(self.output_size)
        
        state = state.reshape(1, state.shape[0], state.shape[1], state.shape[2])
        act_values = self.model.predict(state)
        return act_values

    def replay(self, batch_size):
        minBatchSize = batch_size
        if (len(self.memory) < batch_size):
            minBatchSize = len(self.memory)

        minibatch = random.sample(self.memory, minBatchSize)
        for state, action, reward, next_state, done in minibatch:
            target = reward

            if not done:
                    target = (reward + self.gamma *
                          np.amax(self.model.predict(next_state)[0]))
            target_f = self.model.predict(state)
            
            action_index = np.argmax(action)

            target_f[0][action_index] = target
            self.model.fit(state, target_f, epochs=1, verbose=0)

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

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