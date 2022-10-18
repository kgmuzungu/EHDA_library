import matplotlib.pyplot as plt
import numpy as np

length = 100
start = 0
step = 1
x = np.arange(start, length, step)
test_array = x
# test_array = 1/x
y = np.cumsum(test_array)

fig, ax = plt.subplots(2)
ax[0].plot(x, test_array)
ax[1].plot(x, y)
plt.show()