import json
import os
import matplotlib.pyplot as plt
import numpy as np
import re
path = 'C:/Users/hvvhl/PycharmProjects/EHDA/jsonfiles'

directory_contents = os.listdir(path)

print(directory_contents)


for i in directory_contents:
    res = re.search("cone jet", i)
    if res == None:
        continue
    else:
        print(i)

        """print("*******")
        with open(filename) as jsonFile:
            # data1 = jsonFile.read()
            # data = json.loads(data1)
            jsonObject = json.load(jsonFile)
            print(type(jsonObject))"""