import sys
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from functools import reduce
from keras.models import Sequential
from keras.layers.core import Dense, Activation
from keras.layers.normalization import BatchNormalization
from keras.layers.recurrent import GRU
from keras.optimizers import Nadam
from keras.callbacks import Callback
from keras import backend as K

data_file = sys.argv[1]
item_name = sys.argv[2]
dest_file = sys.argv[3]

window_size = 5
epoch = 2500
batch_size = 52
n_num = 80
predict_size = 250
input_num = window_size + 2 - 1

df = pd.read_csv(data_file, encoding = 'Shift_JIS')

ds = df.groupby(['year', 'week'])[item_name].sum().astype('float')

def window_with_index(d, wsize):
    return [
        np.r_[
            d.index[i + wsize - 1][0], # year
            d.index[i + wsize - 1][1], # week
            d[i:(i + wsize)].values.flatten()
        ]
        for i in range(len(d) - wsize + 1)
    ]

dw = window_with_index(ds, window_size)

data = np.array([i[0:-1] for i in dw]).reshape(len(dw), input_num, 1)
labels = np.array([i[-1] for i in dw]).reshape(len(dw), 1)

# loss callback
class LossHistory(Callback):
    def on_train_begin(self, logs = {}):
        self.losses = []

    def on_batch_end(self, batch, logs = {}):
        self.losses.append(logs.get('loss'))

# RMSE
def root_mean_squared_error(act, pred):
    return K.sqrt(K.mean(K.square(pred - act), axis = 1))


model = Sequential()

model.add(BatchNormalization(axis = 1, input_shape = (input_num, 1)))

model.add(GRU(n_num, activation = 'relu'))

model.add(Dense(1))
model.add(Activation('linear'))

opt = Nadam()

model.compile(loss = root_mean_squared_error, optimizer = opt)

history = LossHistory()

model.fit(data, labels, epochs = epoch, batch_size = batch_size, 
          callbacks = [history])

pred1 = model.predict(data)

max_week = max(ds.index.levels[1])

def predict(a, b):
    r = model.predict(a[1])

    y = a[1][0, 0, 0]
    w = a[1][0, 1, 0] + 1

    if w > max_week:
        y += 1
        w = 1

    n = np.r_[ y, w, a[1][:, 3:].flatten(), r.flatten() ].reshape(1, input_num, 1)

    return (np.append(a[0], r), n)

fst_data = np.array(dw[0][0:-1]).reshape(1, input_num, 1)

pred2 = reduce(predict, range(predict_size), (np.array([]), fst_data))


fig, axes = plt.subplots(2, 1)

axes[0].plot(history.losses)

axes[1].set_xlim(0, predict_size)

axes[1].plot(ds.values, label = 'actual')

axes[1].plot(range(window_size - 1, len(ds)), pred1, label = 'predict1')
axes[1].plot(range(window_size - 1, predict_size + window_size - 1), pred2[0], label = 'predict2')

axes[1].legend()

plt.savefig(dest_file)
