from network import Network
from matrix_network import MatrixNetwork
import numpy as np
from visualizer import NetworkVisualizer
import random
# Adjacency matrix entries are the optical link length L for each existing edge, 0 otherwise.
# Grid network with 3x3 nodes (nodes 0–8 laid out row-wise).
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
# List of (connectivity adjacency, duration); each adjacency is square (here 4x4).
experiments = np.array([
    (
        np.array([
            # 0  1  2  3
            [0, 1, 0, 1],  # 0
            [1, 0, 1, 0],  # 1
            [0, 1, 0, 1],  # 2
            [1, 0, 1, 0],  # 3
        ]),
        5,
    ),
    (
        np.array([
            # 0  1  2  3
            [0, 1, 0, 1],  # 0
            [1, 0, 1, 0],  # 1
            [0, 1, 0, 1],  # 2
            [1, 0, 1, 0],  # 3
        ]),
        5,
    ),
], dtype=[("adjacency_matrix", np.ndarray), ("duration", np.int16)])
"""network = Network(adjacency_matrix)
print(len(network.graph.es))
print(network.graph.es["length"])

network.step()
network.show_graph(path="network.png")
network.show_active_graph(path="active_network.png")"""

network = MatrixNetwork(adjacency_matrix, memories, experiments, mstar=10)
visualizer = NetworkVisualizer(network)
c = 0
while True:
    network.env_step()
    obs = network.get_observation()
    print(obs)
    # now two actions are possible, let them be equally likely
    if random.random() < 0.5:
        print("Assigning virtual link")
        network.assign_virtual_link(0, 7)
    else:
        for i in range(len(experiments)):
            num_mappings = len(obs["possible_experiment_assignments"][i])
            if num_mappings > 0:
                print("Assigning experiment")   
                mapping = obs["possible_experiment_assignments"][i][0] # take the first mapping for now
                network.assign_experiment(experiments[i], mapping)
    print(network.get_valid_swaps())
    visualizer.render(step_label=c)
    c += 1