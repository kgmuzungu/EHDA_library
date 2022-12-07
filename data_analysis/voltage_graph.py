'''
	JSON Data flattening to pandas
	AUTHOR: 乔昂 - jueta
	DATE: 28/11/2022
'''

import pandas as pd
from pandas.io.json import json_normalize
import json
import matplotlib.pyplot as plt
from sklearn.utils import column_or_1d
import numpy as np
from scipy.signal import butter, lfilter



df = pd.read_pickle("exp7.pkl")

import seaborn as sns
sns.scatterplot('voltage', 'data [nA]', data=df, hue='spray mode.Sjaak')

plt.show()