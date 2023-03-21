
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_feather('Data/map_23-03-02.feather')


df = df.loc[df['flow_rate'] == 0.7]

df.reset_index(drop=True).head()

size = 50000
last_value = 0

# Plot raw data
plt.figure(1)
for sample in df.index:
    if df['spray_mode'][sample] == 'Dripping':
        plt.plot(np.arange(last_value, last_value + size)/1e5, df['current'][sample], c='blue')  #green', label='Dripping')
    elif df['spray_mode'][sample] == 'Intermittent':
        plt.plot(np.arange(last_value, last_value + size)/1e5, df['current'][sample], c='blue')  #blue', label='Intermittent')
    elif df['spray_mode'][sample] == 'Cone Jet':
        plt.plot(np.arange(last_value, last_value + size)/1e5, df['current'][sample], c='blue')  #red', label='Cone Jet')
    elif df['spray_mode'][sample] == 'Multi Jet':
        plt.plot(np.arange(last_value, last_value + size)/1e5, df['current'][sample], c='blue')  #purple', label='Multi Jet')
    elif df['spray_mode'][sample] == 'Undefined':
        plt.plot(np.arange(last_value, last_value + size)/1e5, df['current'][sample], c='blue')  #black', label='Undefined')
    elif df['spray_mode'][sample] == 'Corona':
        plt.plot(np.arange(last_value, last_value + size)/1e5, df['current'][sample], c='blue')  #cyan', label='Corona')
    last_value += size

plt.ylim(-50, 250)
plt.ylabel('current [nA]')
plt.xlabel('time [s]')
plt.xlim(right=113)


# Plot voltage

plt.figure(2)
plt.xlim(right=113)
plt.ylabel('Voltage [V]')
plt.xlabel('time [s]')
plt.plot(np.arange(len(df['voltage']))/2, df['voltage'])
plt.show()