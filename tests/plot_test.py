import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm

#x = np.arange(20)
ys = [i for i in range(20)]

colors = cm.rainbow(np.linspace(0, 1, len(ys)))
# for y, c in zip(ys, colors):
    # plt.scatter(x, y, color=c)
alpha = np.array([1.9793050418972403e-08, 2.6390664180394155e-09, 1.9793050418972403e-08, 2.6390664180394155e-09, 1.9793050418972403e-08, 2.6390664180394155e-09, 1.9793050418972403e-08, 2.6390664180394155e-09, 1.9793050418972403e-08, 2.6390664180394155e-09, 1.9793050418972403e-08, 2.6390664180394155e-09, 1.9793050418972403e-08, 2.6390664180394155e-09, 1.9793050418972403e-08, 2.6390664180394155e-09, 1.9793050418972403e-08, 2.6390664180394155e-09, 1.9793050418972403e-08, 2.6390664180394155e-09])
#x = np.arange(len(alpha))
x = np.array([0.0020230273658164927, 0.0007387041728202621, 0.0020230273658164927, 0.0007387041728202621, 0.0020230273658164927, 0.0007387041728202621, 0.0020230273658164927, 0.0007387041728202621, 0.0020230273658164927, 0.0007387041728202621, 0.0020230273658164927, 0.0007387041728202621, 0.0020230273658164927, 0.0007387041728202621, 0.0020230273658164927, 0.0007387041728202621, 0.0020230273658164927, 0.0007387041728202621, 0.0020230273658164927, 0.0007387041728202621])
#for c in colors:
#for y, c in zip(alpha, colors):
plt.scatter(x, alpha, color=colors)

plt.figure()


x = [1,2,3]
y = [[1,2,3],[4,5,6],[7,8,9]]
plt.xlabel("X-axis")
plt.ylabel("Y-axis")
plt.title("A test graph")
print(y[0])
print(y[1])
print(y[2])

for i in range(len(y[0])):
    plt.plot(x,[pt[i] for pt in y],label = 'id %s'%i)
plt.legend()
plt.show()

"""" 
rng = np.random.RandomState(0)
for marker in ['o', '.', ',', 'x', '+', 'v', '^', '<', '>', 's', 'd']:
    plt.plot(rng.rand(5), rng.rand(5), marker,
             label="marker='{0}'".format(marker))
plt.legend(numpoints=1)
plt.xlim(0, 1.8);

"""

x = [1, 2, 3, 4, 5, 6, 7]
y = [1, 3, 3, 2, 5, 7, 9]

# Find the slope and intercept of the best fit line
slope, intercept = np.polyfit(x, y, 1)

# Create a list of values in the best fit line
abline_values = [slope * i + intercept for i in x]

# Plot the best fit line over the actual values
plt.plot(x, y, '--')
plt.plot(x, abline_values, 'b')
plt.title(slope)
plt.show()