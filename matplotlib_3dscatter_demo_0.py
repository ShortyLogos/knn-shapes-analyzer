import matplotlib.pyplot as plt
import numpy as np


size = 10
rng = np.random.default_rng()
data1 = rng.random((size,3))
data2 = rng.random((size,3))

fig = plt.figure()
ax = fig.add_subplot(projection='3d')
ax.scatter(data1[:,0], data1[:,1], data1[:,2], marker='o', color='r')
ax.scatter(data2[:,0], data2[:,1], data2[:,2], marker='*', color='b')
ax.scatter(0.2, 0.3, 0.7, marker='>', color=(0,0,0.25))

ax.set_title('Espace de solution')
ax.set_xlabel('x label')
ax.set_ylabel('y label')
ax.set_zlabel('z label')

plt.show()