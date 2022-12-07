'''
	Pandas DataFrame creation and saving
	AUTHOR: 乔昂 - jueta
	DATE: 28/11/2022
'''

import pandas as pd
import json
import numpy as np

# warnings.filterwarnings('ignore')
sampling_frequency = 1e5

experiment_name = "exp5"

with open("joaoData/experiments_05_12/" + experiment_name + ".json", 'r') as data_file:    
    data = json.loads(data_file.read())  

data_measurements = pd.json_normalize(data, record_path=['measurements'])
data_processing = pd.json_normalize(data, record_path=['processing'])
df = pd.concat([data_measurements, data_processing], axis=1)

df = df.reset_index()
df = df.explode('data [nA]', ignore_index=True)
print(df)
df.to_pickle(experiment_name + ".pkl")

