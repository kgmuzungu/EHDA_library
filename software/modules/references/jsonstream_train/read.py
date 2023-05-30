import pandas as pd
import json
  

df = pd.read_json("experiment/data.json", orient='index')

print(df.head())
print(df.info())


