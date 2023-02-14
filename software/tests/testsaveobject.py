# save numpy array as csv file
from numpy import asarray
from numpy import savetxt
import csv
import json
import os
import matplotlib.pyplot as plt
import numpy as np
import re
import pandas as pd
from pandas.io.json import json_normalize
from functools import reduce
from IPython.display import display, HTML

class Dog:

    teste_var: int
    tricks = []             # mistaken use of a class variable

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return (json.dumps((self.name) + " " + str(self.teste_var)))

    def test_self(self):
        self.teste_var = 666

    def get_teste_var(self):
        return self.teste_var

    def add_trick(self, trick):
        self.tricks.append(trick)

    def get_dog_name(self):
        return self.name

    def save_new(self):
        """save class as self.name.txt"""
        data = []
        txt_file = open("E:/"+self.name+'.txt','w')
        json_file = open("E:/"+self.name+'.json','w')
        csv_file = open("E:/"+self.name+'.csv','w')
        csv_file.write('Sample')
        json_file.write('Sample')
        dictionary = {
            "name": "sathiyajith",
            "rollno": 56,
            "cgpa": 8.6,
            "phonenumber": "9976770500",
            "tricks": self.tricks
        }
        """
        for i in self.tricks:
            csv_file.write(';'+str(i))
            data.append(i)

        dictionary["data"] = data"""
        json_object = json.dumps(dictionary, indent=5)
        json_file.write(json_object)
        txt_file.write(str(dictionary))

    def load_setup(self, filename, dictionary):

        with open(filename, 'r+') as file:
            # First we load existing data into a dict.
            file_data = json.load(file)
            # Join new_data with file_data inside emp_details
            file_data["liquid"].append(dictionary)
            # Sets file's current position at offset.
            file.seek(0)
            # convert back to json.
            json.dump(file_data, file, indent=4)

    def close_setup(self):
        self.jsonFile.close()

class Food:
    def __init__(self, object):
        self.name = object.name

    def print_food(self):
        print(self.name)







def pretty_json(data):
    return json.dumps(json.loads(data), sort_keys=False)


filename = "ethyleneglycolHNO3.json"
listdir = os.listdir()
j = 0
plt.style.use('seaborn-colorblind')
plt.ion()

for i in listdir:
    res = re.search("json", i)
    if res == None:
        continue
    else:
        print(filename)
        print("*******")
        with open(filename) as jsonFile:
            # data1 = jsonFile.read()
            # data = json.loads(data1)
            jsonObject = json.load(jsonFile)
            print(type(jsonObject))
            # df = pandas.io.json.json_normalize(json_data)

            jsonData = jsonObject["measurements"]
            print(jsonData)

            #rev_df = pd.DataFrame.from_dict(json_normalize(jsonData), orient='columns')
            #print(rev_df)
            print(type(jsonData))
            found_values = []

            for index, value in enumerate(jsonData):
                # print(index, value)
                print(type(value))

                result = re.search("""data": "[ (.*)  ]", "flow_rate":""", str(value))
                print(result)

                print(value)
                """for data in set().union(*value):
                    if ("data" in item[1]):
                        print(item[2])"""
                print("*******")


            #print(jsonObject.get('data', {}))
            #s = pretty_json(str(jsonData))



            #print(s)
            #if "data" in s:
                # print("aquiiiiiiiii")
            """
                        for x in jsonData:
                    keys = x.keys()
                    print(keys)
                    values = x.values()
                    print(values)
    
                jsonFile.close()
                
            s = len(jsonObject['measurements']) - 1
            for i in jsonObject['measurements'][s]:
                print(i)
                print("**")
                print(i["data"])
                aux = json.dumps(i)
                if "data" in aux:
                    print(aux['data'])
            """


dog_obj = Dog("teste1")
dog_obj.add_trick("trick")
dog_obj.add_trick("loka")
dog_obj.save_new()
print(dog_obj.name)
dog_obj.test_self()
print("aqui")
print(repr(dog_obj))

food_obj = Food(dog_obj)
food_obj.print_food()

dictionary = {
            "name": 2,
            "variance": 1
        }

dog_obj.load_setup("sample.json", dictionary)
# dog_obj.append_json()
# dog_obj.close_setup()


datapoints = [7.0 -5.0 -19.9]
res = ' '.join([str(item) for item in datapoints])
print(res)
# res = (format(datapoints, ', d'))

# printing result



"""
dog_obj2 = Dog ("teste2")
dog_obj2.add_trick("lokona")
dog_obj2.add_trick("123")
dog_obj2.save_new()
"""

