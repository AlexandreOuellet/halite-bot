import os
import sys


class RedirectStdStreams(object):
    def __init__(self, stdout=None, stderr=None):
        self._stdout = stdout or sys.stdout
        self._stderr = stderr or sys.stderr

    def __enter__(self):
        self.old_stdout, self.old_stderr = sys.stdout, sys.stderr
        self.old_stdout.flush(); self.old_stderr.flush()
        sys.stdout, sys.stderr = self._stdout, self._stderr

    def __exit__(self, exc_type, exc_value, traceback):
        self._stdout.flush(); self._stderr.flush()
        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr

devnull = open(os.devnull, 'w')

with RedirectStdStreams(stdout=devnull, stderr=devnull):
    import random
    import numpy as np
    from collections import deque

    import tensorflow as tf


    import keras
    from keras.models import Sequential, Model
    from keras.layers import Dense, Input, Embedding, Conv2D, Flatten, Activation, MaxPooling2D
    from keras.optimizers import Adam
    from keras.utils import to_categorical, plot_model
    from nn import starterBot
    import nnutils

    import pickle
    import os.path

    import time
    import logging
    from keras.callbacks import Callback

# class EarlyStop(Callback):
#     def __init__(self, monitor='loss', value=0.0021, verbose=1):
#         super(Callback, self).__init__()
#         self.monitor = monitor
#         self.value = value
#         self.verbose = verbose

#     def on_epoch_end(self, epoch, logs={}):
#         current = logs.get(self.monitor)
#         if current is None:
#             warnings.warn("Early stopping requires %s available!" % self.monitor, RuntimeWarning)

#         if current < self.value:
#             if self.verbose > 0:
#                 print("Epoch %05d: early stopping THR" % epoch)
#             self.model.stop_training = True

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

    def remember(self, game_state, ship_state, action, next_reward, next_game_state, next_ship_state, done):
        self.memory.append((game_state, ship_state, action, next_reward, next_game_state, next_ship_state, done))

    def forcePredict(self,game_state, ship_state):
        game_state = game_state.reshape(1, game_state.shape[0], game_state.shape[1], game_state.shape[2])
        ship_state = ship_state.reshape(1, ship_state.shape[0])

        act_values = self.model.predict({'guylaine_input': game_state, 'ship_input': ship_state})
        return act_values
        

    def predict(self, game_state, ship_state, ship, game_map):
        if np.random.rand() <= self.epsilon:
            # starter bot
            starter_action = starterBot.predict(ship, game_map)
            logging.debug("starter_action: %s", starter_action)
            index = nnutils.parseCommandToActionIndex(starter_action)
            logging.debug("index: %s", index)
            actions = np.random.rand(self.output_size)
            if index == None:
                actions[3] = 1
            else:
                actions[index] = 1
            
            # random action
            # actions = np.random.rand(self.output_size)

            # Force docking
            # for planet in game_map.all_planets():
            #     if ship.can_dock(planet) and planet.num_docking_spots > (planet.current_production / 6):
            #         actions[0] = 1 # force dock if possible
            #         logging.debug("Forced dock")
            action_index = np.argmax(actions)
            logging.debug("action_index: %s", action_index)
            for index in range(0, len(actions)):
                actions[index] = 0

            actions[action_index] = 1
            logging.debug("Random action")
            return actions

        
        actions = self.forcePredict(game_state, ship_state)
        action_index = np.argmax(actions)
        actions[0][action_index-1] = 1
        logging.debug("Predicted action : %s", actions)
        return actions

    def replay(self, batch_size, epoch):
        print("Training")

        guylaine_inputs = np.zeros(shape=(1, self.guylaine_input_shape[0], self.guylaine_input_shape[1], self.guylaine_input_shape[2]))
        ship_input = np.zeros(shape=(1, self.ship_input_shape[0]))

        game_state_batch = []
        ship_state_batch = []

        targets = np.zeros((len(self.memory), self.output_size))

        for i in range(0, len(self.memory)):
            print("Gathering data for batch i:%s", i)
            game_state, ship_state, action_taken, next_reward, next_game_state, next_ship_state, done = self.memory[i]

            game_state_batch.append(game_state)
            ship_state_batch.append(ship_state)

            targets[i] = self.forcePredict(game_state, ship_state)

            # First, predict the Q values of the next states. Note how we are passing ones as the mask.
            next_Q_values = self.forcePredict(next_game_state, next_ship_state)

            # The Q values of each start state is the reward + gamma * the max next state Q value
            targets[i][action_taken] = next_reward + self.gamma * np.max(next_Q_values)


        print("Done gathering data for batch")
        if len(ship_state_batch) != 0:            
            print("Fitting the model")
            # callbacks = [EarlyStop(monitor='loss', value=0.0021, verbose=1)]

            history = self.model.fit({'guylaine_input': np.array(game_state_batch), 'ship_input': np.array(ship_state_batch)}, np.array(targets), batch_size=batch_size, verbose=1, epochs=epoch)
            print("Done fitting the model, printing history")

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
            
        print("Training done.  epsilon: %s", self.epsilon)
        return history.history['loss']


    def load(self):
        if os.path.isfile('./data/model'):
            self.model.load_weights('./data/model')
        if os.path.isfile('./data/epsilon'):
            self.epsilon = pickle.load(open('./data/epsilon', 'rb'))
            # self.epsilon = 0

    def save(self):
        self.model.save_weights('./data/model')
        pickle.dump(self.epsilon, open('./data/epsilon', 'wb'))

    def loadMemory(self, fileName):
        if os.path.isfile(fileName):
            self.memory = pickle.load(open(fileName, 'rb'))


    def saveMemory(self, fileName):
        logging.debug("Saving Memory of length %s", len(self.memory))
        pickle.dump(self.memory, open('./data/memory/' + fileName, 'wb'))