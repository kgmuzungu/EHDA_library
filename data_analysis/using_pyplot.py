import plotly.express as px
import pandas as pd
import json
import numpy as np


# df = pd.read_pickle("exp5.pkl")
# df = px.data.gapminder().query("country=='Canada'")
# fig = px.scatter(df, x="index", y="data [nA]", title='Life expectancy in Canada')

experiment_name = "exp5"

with open("joaoData/experiments_05_12/" + experiment_name + ".json", 'r') as data_file:    
    data = json.loads(data_file.read())  

data_measurements = pd.json_normalize(data, record_path=['measurements'])
data_processing = pd.json_normalize(data, record_path=['processing'])
df = pd.concat([data_measurements, data_processing], axis=1)

data = pd.concat([df['mean'], df['spray mode.Sjaak']])
print(data.head())  
# fig.show()