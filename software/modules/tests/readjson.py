import numpy as np
import os
import json
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np

plt.style.use('seaborn-v0_8-colorblind')
plt.ion()


"""
df = pd.read_json('ethanol.json')
print(patients_df.head())"""

json_data = json.load(open('ethanol.json'))

jsonData = json_data["measurements"]
test = jsonData[0][0]
#print("[PRINT]" + str(test))
nowitworks = json.loads(test)
print("[PRINT]" + str(nowitworks["data"]))
a = float(nowitworks["data"])
i=0

for x in jsonData:
    print(x[i].split(' '))
    if "data" in x[i]:
        print("*")
    i = i + 1

"""
var result = strings.map(function(s) {
    return s.split(/\s+/).slice(1,3);
});
Now you can access each word like this:

console.log(result[1][0]);
https://stackoverflow.com/questions/16223043/get-second-and-third-words-from-string
"""

#patients_df = pd.read_json('ethanol.json')

json_aux = json.dumps(json_data, sort_keys=True, indent=4)

#data_frame = pd.DataFrame(json_data)
#print(data_frame)
print(type(json_data)) # dict

df = pd.json_normalize(json_data)
#print("df:")
print(type(df)) # dataframe
#print(df.info())

aux_series = df["measurements"]
print(type(aux_series))

print("--------")
aux_dataframe = df[["measurements"]]
print(type(aux_dataframe))
print(aux_dataframe['data'])
print("--------")
data1 = aux_dataframe.loc[:,["data"]]
print(data1)
"""plt.hist(aux_dataframe['data'])
plt.show()
plt.hist(aux_dataframe['data'])
plt.show()
df = pd.DataFrame(data)"""


df = pd.read_json('ethanol.json') # carregando os dados +1 vez, caso tenha alterado.
# YOUR CODE HERE


# print(aux.info())
# print(aux['data'])
# aux = (list(aux)[1])
# aux2 = aux['data']
# print(df["measurements"].values())



