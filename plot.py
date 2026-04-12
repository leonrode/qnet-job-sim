from matrix_network import MatrixNetwork
import numpy as np
from visualizer import NetworkVisualizer
import random
import matplotlib.pyplot as plt
from collections import Counter
# # Grid network with 3x3 nodes (nodes 0–8 laid out row-wise).
adjacency_matrix = np.array([
    # 0  1  2  3  4  5  6  7  8
    [0, 1, 0, 1, 0, 0, 0, 0, 0],  # 0
    [1, 0, 1, 0, 1, 0, 0, 0, 0],  # 1
    [0, 1, 0, 0, 0, 1, 0, 0, 0],  # 2
    [1, 0, 0, 0, 1, 0, 1, 0, 0],  # 3
    [0, 1, 0, 1, 0, 1, 0, 1, 0],  # 4
    [0, 0, 1, 0, 1, 0, 0, 0, 1],  # 5
    [0, 0, 0, 1, 0, 0, 0, 1, 0],  # 6
    [0, 0, 0, 0, 1, 0, 1, 0, 1],  # 7
    [0, 0, 0, 0, 0, 1, 0, 1, 0],  # 8
])

memories = np.array([2, 3, 2, 3, 4, 3, 2, 3, 2])

network = MatrixNetwork(adjacency_matrix, memories, [], mstar=10)
visualizer = NetworkVisualizer(network)
# num edges in complete graph of 9 nodes:
complete_graph_num_edges = 9 * 8 / 2
num_physical_links = 12
c = 0
num = []
while c <= 1000:
    network.env_step()
    obs = network.get_observation()
    # let's get all virtual links we can assign at this time and choose one randomly
    possible_virtual_links = network._get_generateable_virtual_links()
    #print(possible_virtual_links)
    if len(possible_virtual_links) > 0:
        i, j = random.choice(possible_virtual_links)
        #print(f"Assigning virtual link {i} {j}")
        #visualizer.render(step_label=c)
        network.assign_virtual_link(i, j)
    #visualizer.render(step_label=c)
    num.append(len(possible_virtual_links))
    c += 1

average = np.mean(num)
print(average)
# plot a line = average
fig, ax1 = plt.subplots()
ax1.plot(np.ones(len(num)) * average, color='tab:blue', linestyle='--')

color = 'tab:red'

ax1.plot(num, color=color, linestyle='-')
ax1.tick_params(axis='y', labelcolor=color)


fig.tight_layout()  # otherwise the right y-label is slightly clipped
plt.show()

from collections import Counter

# Compute frequencies of possible virtual links per timestep (ignoring zeros for clarity)
counts = Counter(num)
values = sorted(counts.keys())
frequencies = [counts[val] for val in values]

# Generate a bar plot to visualize the distribution
plt.figure(figsize=(8,4))
plt.bar(values, frequencies, color='tab:purple')
plt.xlabel('Number of Generateable Virtual Links per Timestep')
plt.ylabel('Frequency')
plt.title('Distribution of Generateable Virtual Links per Timestep (Grid Network, N=9)')
plt.tight_layout()
plt.show()

#now let's do a linear chain of 9 nodes
# adjacency_matrix = np.array([
#     [0, 1, 0, 0, 0, 0, 0, 0, 0],
#     [1, 0, 1, 0, 0, 0, 0, 0, 0],
#     [0, 1, 0, 1, 0, 0, 0, 0, 0],
#     [0, 0, 1, 0, 1, 0, 0, 0, 0],
#     [0, 0, 0, 1, 0, 1, 0, 0, 0],
#     [0, 0, 0, 0, 1, 0, 1, 0, 0],
#     [0, 0, 0, 0, 0, 1, 0, 1, 0],
#     [0, 0, 0, 0, 0, 0, 1, 0, 1],
#     [0, 0, 0, 0, 0, 0, 0, 1, 0],
# ])

# memories = np.array([1, 2, 2, 2, 2, 2, 2, 2, 1])

# linearNetwork = MatrixNetwork(adjacency_matrix, memories, [], mstar=10)
# linearVisualizer = NetworkVisualizer(linearNetwork)
# num = []
# c = 0
# while c <= 1000:
#     linearNetwork.env_step()
#     obs = linearNetwork.get_observation()
#     possible_virtual_links = linearNetwork._get_generateable_virtual_links()
#     if len(possible_virtual_links) > 0:
#         i, j = random.choice(possible_virtual_links)
#         linearNetwork.assign_virtual_link(i, j)
#         #linearVisualizer.render(step_label=c)
#     num.append(len(possible_virtual_links))
#     c += 1
# average = np.mean(num)
# print(average)

# # number that appeared the most often besides 0
# from collections import Counter

# # Compute frequencies of possible virtual links per timestep (ignoring zeros for clarity)
# counts = Counter(num)
# values = sorted(counts.keys())
# frequencies = [counts[val] for val in values]

# # Generate a bar plot to visualize the distribution
# plt.figure(figsize=(8,4))
# plt.bar(values, frequencies, color='tab:purple')
# plt.xlabel('Number of Generateable Virtual Links per Timestep')
# plt.ylabel('Frequency')
# plt.title('Distribution of Generateable Virtual Links per Timestep (Linear Chain, N=9)')
# plt.tight_layout()
# plt.show()
# # plot a line = average
# fig, ax1 = plt.subplots()
# ax1.plot(np.ones(len(num)) * average, color='tab:blue', linestyle='--')

# color = 'tab:red'

# ax1.plot(num, color=color, linestyle='-')
# ax1.tick_params(axis='y', labelcolor=color)


# fig.tight_layout()  # otherwise the right y-label is slightly clipped
# plt.show()

