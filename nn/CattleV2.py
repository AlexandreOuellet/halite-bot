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
    np.set_printoptions(threshold=np.nan)


    from collections import deque

    import tensorflow as tf
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 


    import keras
    from keras.models import Sequential, Model
    from keras.layers import Dense, Input, Embedding, Conv2D, Flatten, Activation, MaxPooling2D, Dropout
    from keras.optimizers import Adam
    from keras.utils import to_categorical, plot_model
    from nn import starterBot
    import nnutils

    import pickle
    import os.path

    import time
    import logging
    from keras.callbacks import Callback

EPISODES = 1000
DROPOUT_RATE = 0.2

class Cattle:
    def __init__(self, input_shape, output_size, name):
        self.name = name
        self.input_shape = input_shape
        self.output_size = output_size
        self.memory = deque()
        self.gamma = 0.99    # discount rate
        self.epsilon = 1.0  # exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.model = self._build_model()
        self.old_state_by_id = {}

    def _build_model(self):
        # Neural Net for Deep-Q learning Model
        input = Input(shape=(self.input_shape), name='guylaine_input')
        guylaine = Dense(512, name='dense1', activation='relu')(input)
        guylaine = Dropout(DROPOUT_RATE)(guylaine)
        guylaine = Dense(512, name='dense2', activation='relu')(guylaine)
        guylaine = Dropout(DROPOUT_RATE)(guylaine)
        guylaine = Dense(512, name='dense3', activation='relu')(guylaine)
        guylaine = Dropout(DROPOUT_RATE)(guylaine)
        output = Dense(self.output_size, activation='relu', name='output')(guylaine)

        model = Model(inputs=input, outputs=output)

        model.compile(loss='mse', optimizer=Adam(lr=self.learning_rate))
        return model

    def rememberNextState(self, id, state, actions, reward):
        if id not in self.old_state_by_id:
            self.old_state_by_id[id] = (state)
        else:
            old_state = self.old_state_by_id[id]
            self.memory.append((id, state, actions, reward))
            self.old_state_by_id[id] = state

    def forcePredict(self,state):
        state = state.reshape(1, state.shape[0])

        act_values = self.model.predict(state)
        return act_values
        
    def predict(self, state, ship, game_map):
        if np.random.rand() <= self.epsilon:
            # starter bot
            # starter_action = starterBot.predictStarterBot(ship, game_map)
            # logging.debug("starter_action: %s", starter_action)
            # index = nnutils.parseCommandToActionIndex(starter_action)
            # logging.debug("index: %s", index)
            # actions = np.random.rand(self.output_size)
            # if index == None:
            #     actions[3] = 1
            # else:
            #     actions[index] = 1
            
            # random action
            actions = np.random.rand(self.output_size)

            # # Force docking
            for planet in game_map.all_planets():
                if ship.can_dock(planet) and planet.num_docking_spots > (planet.current_production / 6):
                    actions[0] = 1 # force dock if possible
                    logging.debug("Forced dock")

            action_index = np.argmax(actions)
            for i in range(0, len(actions)):
                actions[i] = 0

            actions[action_index] = 1

            # actions = to_categorical(actions, num_classes=self.output_size)
            # action_index = np.argmax(actions)

            logging.debug("Random action : %s", actions)
            logging.debug("Random action index : %d", action_index)
            return actions

        
        actions = self.forcePredict(state)
        action_index = np.argmax(actions)

        logging.debug("Predicted action : %s", actions)
        logging.debug("Predicted action index : %d", action_index)
        return actions

    def replay(self, batch_size, epoch, run_name):
        from keras.callbacks import TensorBoard
        print("Training")

        state_batch = []

        targets = np.zeros((len(self.memory), self.output_size))

        for i in reversed(range(0, len(self.memory))):
            print("Gathering data for batch i:%s", i)
            state, action_taken, reward, next_state, done = self.memory[i]

            state_batch.append(state)

            targets[i] = self.forcePredict(state)

            predicted_next_actions = self.forcePredict(next_state)
            predicted_next_best_reward = np.argmax(predicted_next_actions)

            target = reward + self.gamma *  predicted_next_best_reward
            targets[i][action_taken] = target

        print("Done gathering data for batch")
        if len(ship_state_batch) != 0:
            print("Fitting the model")
            # callbacks = [EarlyStop(monitor='loss', value=0.0021, verbose=1), TensorBoard(write_images=True, log_dir='./logs/'+strategy+'/'+filename]
            tensor_log_file = './data/logs/{}/{}'.format(self.name, run_name)
            callback = TensorBoard(write_images=True, log_dir=tensor_log_file)

            history = self.model.fit(np.array(state_batch), np.array(targets), batch_size=batch_size, verbose=1, epochs=epoch, callbacks=[callback])
            print("Done fitting the model, printing history")
            print(history)
            print(history.history)

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
            
        print("Training done.  epsilon: %s", self.epsilon)
        return history.history['loss']

    def load(self):
        dir = './{}/data/'.format(self.name)
        if os.path.exists(dir) == False:
            os.makedirs(dir)
        if os.path.isfile(dir+'model'):
            self.model.load_weights(dir+'model')
        if os.path.isfile(dir+'epsilon'):
            self.epsilon = pickle.load(open(dir+'epsilon', 'rb'))
        self.epsilon = 0

    def save(self):
        dir = './{}/data/'.format(self.name)
        if os.path.exists(dir) == False:
            os.makedirs(dir)
        self.model.save_weights(dir+'model')
        pickle.dump(self.epsilon, open(dir+'epsilon', 'wb'))

    def loadMemory(self, fileName):
        dir = './{}/memory/'.format(self.name)
        if os.path.exists(dir) == False:
            os.makedirs(dir)
        if os.path.isfile(fileName):
            self.memory = pickle.load(open(fileName, 'rb'))

    def saveMemory(self, fileName):
        dir = './{}/memory/'.format(self.name)
        if os.path.exists(dir) == False:
            os.makedirs(dir)
        logging.debug("Saving Memory of length %s in file %s", len(self.memory), dir )
        pickle.dump(self.memory, open(dir + fileName, 'wb'))