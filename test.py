import numpy as np
# import keras

rand = np.random.randint(10, size=(100, 1))
# y_train = keras.utils.to_categorical(, num_classes=10)
print(rand)

import keras
y_train = keras.utils.to_categorical(rand, num_classes=10)
print(y_train)