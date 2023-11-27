#%%
import numpy as np
import matplotlib.pyplot as plt
right = np.load("left.npy")
left = np.load("right.npy")
right_20k = np.load("left_20k.npy")
left_20k = np.load("right_20k.npy")

# window_size = 7
kernel = np.array([1, 2, 3, 5, 3, 2, 1])
kernel = kernel / np.sum(kernel)
# left = np.convolve(left, kernel, mode='valid')
# right = np.convolve(right, kernel, mode='valid')
# left_20k = np.convolve(left_20k, kernel, mode='valid')
# right_20k = np.convolve(right_20k, kernel, mode='valid')

# plt.plot(left)
# plt.plot(right)
fig = plt.figure(1)
# plt.plot(left, color='blue')
# plt.plot(right, color='green')
plt.plot(left-right, color='red')
fig = plt.figure(2)
# plt.plot(left_20k, color='blue')
# plt.plot(right_20k, color='green')
plt.plot(left_20k-right_20k, color='orange')
fig = plt.figure(3)
plt.plot(left-right, color='red')
plt.plot(left_20k-right_20k, color='orange')

# fig = plt.figure(4)
plt.plot((left-right) - (left_20k-right_20k), color='blue')



# %%


