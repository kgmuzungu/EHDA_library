import json
import os
import matplotlib.pyplot as plt
import numpy as np
import re

a = [[], []]
a[0].append("teste a")
a[0].append("teste b")
print(a[0])
a[1].append("teste c")
print(a)
A = np.array([[], []], dtype=object)
A[0] = 1
A[1] = 2

# Create an empty list
list_of_lists = [[]]
list_of_lists[0].append("1st position")
# Iterate over a sequence of numbers from 0 to 4
for i in range(5):
    # In each iteration, add an empty list to the main list
    list_of_lists.append([])


print('List of lists:')
print(list_of_lists)
list_of_lists[1].append("teste")
list_of_lists[1].append("teste2")
list_of_lists[1].append("teste3")
print((list_of_lists[1]))
print(len(list_of_lists[1]))
list_of_lists[3].append(4)
list_of_lists[4].append(5)
if list_of_lists[0][0] == "1st position":
    print("cu")
print('List of lists:')
print(list_of_lists)

name = [""]
name[0] = "nome position 0"
print(name[0])
name.append("position1")
print(name)

var_aux = [0]
var_aux[0] = 1
var_aux.append(2)
print(var_aux[0])
print(var_aux)
print(len(var_aux))