
import pandas as pd
import json
import matplotlib.pyplot as plt
import numpy as np



data = pd.read_feather('../classified_data/data1.feather')



colors = {'Cone Jet':'red', 'Dripping':'green', 'Intermittent':'blue', 'Multi Jet':'purple', 'Undefined':'black', 'Corona':'cyan'}
data.info()


size = 50000
last_value = 0

for sample in data.index:
    if data['class'][sample] == 'Dripping':
        plt.plot(np.arange(last_value, last_value + size), data['data'][sample], c='green', label='Dripping')
    elif data['class'][sample] == 'Intermittent':
        plt.plot(np.arange(last_value, last_value + size), data['data'][sample], c='blue', label='Intermittent')
    elif data['class'][sample] == 'Cone Jet':
        plt.plot(np.arange(last_value, last_value + size), data['data'][sample], c='red', label='Cone Jet')
    elif data['class'][sample] == 'Multi Jet':
        plt.plot(np.arange(last_value, last_value + size), data['data'][sample], c='purple', label='Multi Jet')
    elif data['class'][sample] == 'Undefined':
        plt.plot(np.arange(last_value, last_value + size), data['data'][sample], c='black', label='Undefined')
    elif data['class'][sample] == 'Corona':
        plt.plot(np.arange(last_value, last_value + size), data['data'][sample], c='cyan', label='Corona')
    last_value += size

plt.show()