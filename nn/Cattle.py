import random
import numpy as np
from collections import deque

import keras
from keras.models import Sequential, Model
from keras.layers import Dense, Input, Embedding, Conv2D, Flatten, Activation, MaxPooling2D
from keras.optimizers import Adam
from keras.utils import to_categorical, plot_model

import nnutils

import logging
import pickle
import os.path

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
        guylaine_input = Input(shape=(self.guylaine_input_shape[0], self.guylaine_input_shape[1], self.guylaine_input_shape[2]))
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
            return random.randrange(self.output_size)

        # t = ship_input.reshape(1, ship_input.shape[0])
        act_values = self.model.predict({'guylaine_input': game_state, 'ship_input': ship_state})
        return act_values

    def replay(self, batch_size):
        logging.debug("Training")

        minBatchSize = batch_size
        if (len(self.memory) < batch_size):
            minBatchSize = len(self.memory)

        # guylaine_inputs = np.zeros((self.guylaine_input_size,))
        # ship_input = np.zeros((self.ship_input_size,))

        minibatch = random.sample(self.memory, minBatchSize)
        for i in range(0, len(minibatch)):
            game_state, ship_state, action, reward, next_game_state, next_ship_state, done = minibatch[i]

            guylaine_inputs[i:i+1] = np.expand_dims(game_state, axis=0)
            ship_input[i:i+1] = np.ship_state(ship_state, axis=0)

            targets[i] = self.predict(guylaine_output, ship_input, True)
            Q_sa = self.predict(next_guylaine_output, next_ship_state, True)

            if done:
                targets[i, action] = reward
            else:
                estimated_reward = self.q_model.predict({'ship_guylaine_input': guylaine_output, 'ship_input': ship_state, 'action_input': action})
                target = (reward + self.gamma * estimated_reward)

                targets[i, action] = reward + target

            self.model.train_on_batch({'ship_guylaine_input': guylaine_output, 'ship_input': ship_state}, targets)

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def load(self):
        if os.path.isfile(self.name + '_model'):
            self.model.load_weights(self.name + '_model')
        # if os.path.isfile(self.name + '_memory'):
        #     self.memory = pickle.load(open(self.name + '_memory', 'rb'))
        if os.path.isfile(self.name + '_epsilon'):
            self.epsilon = pickle.load(open(self.name + '_epsilon', 'rb'))

    def save(self):
        self.model.save_weights(self.name + '_model')
        # pickle.dump(self.memory, open(self.name + '_memory', 'wb'))
        pickle.dump(self.epsilon, open(self.name + '_epsilon', 'wb'))