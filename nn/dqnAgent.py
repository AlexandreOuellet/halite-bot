import random
import numpy as np
from collections import deque
from keras.models import Sequential, Model
from keras.layers import Dense, Input
from keras.optimizers import Adam
import logging

EPISODES = 1000


class DQNAgent:
    def __init__(self, state_size, action_size, name):
        self.name = name
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=2000)
        self.gamma = 0.95    # discount rate
        self.epsilon = 1.0  # exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.model = self._build_model()

    def _build_model(self):
        # Neural Net for Deep-Q learning Model
        logging.debug("state_size : %s", self.state_size)
        inputs = Input(shape=(self.state_size,))
        x = Dense(24, input_dim=self.state_size, activation='relu')(inputs)
        x = Dense(24, activation='relu')(x)
        predictions = Dense(self.action_size, activation='linear')(x)

        model = Model(inputs=inputs, outputs=predictions)
        model.compile(loss='mse',
                      optimizer=Adam(lr=self.learning_rate))
        return model

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state):
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        act_values = self.model.predict(state)
        return np.argmax(act_values[0])  # returns action

    def replay(self, batch_size):
        state = []
        minBatchSize = batch_size
        if (len(self.memory) < batch_size):
            minBatchSize = len(self.memory)

        minibatch = random.sample(self.memory, minBatchSize)
        logging.debug("minibatch[0] : %s", minibatch[0])
        for state, action, reward, next_state, done in minibatch:
            target = reward
            # for i in range(0, self.action_size):
            #     state = np.append(state, next_state, axis=1)

            logging.debug("next_state: %s", next_state)

            test = np.reshape(next_state, (1, len(next_state)))
            test = [next_state]
            logging.debug("test : %s", test)

            if not done:
                target = (reward + self.gamma *
                          np.amax(self.model.predict(test)[0]))
            target_f = self.model.predict(state)
            target_f[0][action] = target
            self.model.fit(state, target_f, epochs=1, verbose=0)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def load(self):
        self.model.load_weights(self.name)

    def save(self):
        self.model.save_weights(self.name)
