"""
This module implemnts the environment as the markov decision process (S, A, P, R)
in the form of matrices and uses igraph purely for subgraph isomorphism checking.
"""

from sqlite3 import adapt
import numpy as np
import igraph
import random
import matplotlib.pyplot as plt
"""
The adjacency matrix is the |N| times |N| matrix where each entry is the optical link length
between the two nodes. This matrix is immutable and represents the static physical link topology
of the network.

memories is a vector of length N where memories[i] is the number of quantum memories remaining for node N_i.

experiments is a list of experiments, each experiment is a tuple (adjacency_matrix, duration)

Gamma_link is the attenuation constant for p_link.
"""
class MatrixNetwork:
    def __init__(self, adjacency_matrix, memories, experiments, mstar=10, gamma_link=1.0, seed=42):
        random.seed(seed)
        self.net_topology = adjacency_matrix
        self.net_graph = igraph.Graph.Adjacency(self.net_topology, mode="undirected")
        self.gamma_link = gamma_link
        self.experiments = np.copy(experiments)
        self.mstar = mstar

        self._N = adjacency_matrix.shape[0]

        # need three fields, E, M, and Q

        # N x N x 2: per directed edge (i, j), [:, :, 0] is age m (or -1 inactive), [:, :, 1] is assignment flag.
        # Inactive: (-1, 0); active unassigned: (m, 0); active assigned: (m, d), where d is the remaining duration of the experiment on the edge
        # Physical vs virtual follows net_topology.
        self.edge_states = np.zeros((self._N, self._N, 2), dtype=np.int16)
        self.edge_states[..., 0] = -1


        # M is a vector of length N where M[i] is the number of quantum memories remaining for node N_i.
        # we make a copy to leave the original memories unchanged
        self.memory_states = np.copy(memories)
    """
    Returns the adjacency matrix of the subnetwork of active links whose age >= duration
    """
    def __edge_states_to_adjacency_matrix(self, duration):
        adjacency_matrix = np.zeros((self._N, self._N), dtype=np.int16)
        for i in range(self._N):
            for j in range(self._N):
                if self.edge_states[i, j, 0] != -1                    and \
                   self.mstar - self.edge_states[i, j, 0] >= duration and \
                   not self._is_link_assigned(i, j): # active link with age <= mstar - duration
                    adjacency_matrix[i, j] = 1 # indicate presence of edge
        return adjacency_matrix

    def _decrement_memory(self, i):
        if i < 0 or i >= self._N:
            raise ValueError(f"Node {i} is not in the network")
        if self.memory_states[i] <= 0:
            raise ValueError(f"Node {i} has no memories remaining")
        self.memory_states[i] -= 1

    def _increment_memory(self, i):
        if i < 0 or i >= self._N:
            raise ValueError(f"Node {i} is not in the network")
        self.memory_states[i] += 1

    def _has_unused_memory(self, i):
        if i < 0 or i >= self._N:
            raise ValueError(f"Node {i} is not in the network")
        return self.memory_states[i] > 0
    
    def _activate_link(self, i, j):
        """
        Activates link (i, j) with success probability p_link.
        Returns True if activation is successful, False otherwise.
        """
        if not self._edge_exists(i, j):
            raise ValueError(f"Physical link {i} {j} is not in the graph")
        p_link = np.exp(-self.gamma_link * self.net_topology[i, j])
        if random.random() < p_link: # activation success
            self.edge_states[i, j, 0] = 0 # set age to 0
            self.edge_states[i, j, 1] = 0 # ensure unassigned

            self.edge_states[j, i, 0] = 0 # set age to 0
            self.edge_states[j, i, 1] = 0 # ensure unassigned

            self._decrement_memory(i)
            self._decrement_memory(j)
            return True
        return False

    def _edge_exists(self, i, j):
        return self.net_graph.are_connected(i, j)
    
    def _deactivate_link(self, i, j):
        if not self._edge_exists(i, j):
            raise ValueError(f"Edge {i} {j} is not in the graph")
        if self.edge_states[i, j, 0] == -1:
            raise ValueError(f"Link {i} {j} is inactive")

        self._increment_memory(i)
        self._increment_memory(j)
        self.edge_states[i, j, 0] = -1
        self.edge_states[j, i, 0] = -1

    def _increment_link_age(self, i, j):
        if not self._edge_exists(i, j):
            raise ValueError(f"Edge {i} {j} is not in the graph")
        if self.edge_states[i, j, 0] == -1:
            raise ValueError(f"Link {i} {j} is inactive")
        self.edge_states[i, j, 0] += 1
        self.edge_states[j, i, 0] += 1

    def _get_link_age(self, i, j):
        if not self._edge_exists(i, j):
            raise ValueError(f"Edge {i} {j} is not in the graph")
        if self.edge_states[i, j, 0] == -1:
            raise ValueError(f"Link {i} {j} is inactive")
        return self.edge_states[i, j, 0]

    def _is_link_active(self, i, j):
        if not self._edge_exists(i, j):
            raise ValueError(f"Edge {i} {j} is not in the graph")
        return self.edge_states[i, j, 0] != -1

    def _set_link_duration(self, i, j, duration):
        if not self._edge_exists(i, j):
            raise ValueError(f"Edge {i} {j} is not in the graph")
        if self.edge_states[i, j, 0] == -1:
            raise ValueError(f"Link {i} {j} is inactive")
        self.edge_states[i, j, 1] = duration
        self.edge_states[j, i, 1] = duration

    def _get_link_duration(self, i, j):
        if not self._edge_exists(i, j):
            raise ValueError(f"Edge {i} {j} is not in the graph")
        if self.edge_states[i, j, 0] == -1:
            raise ValueError(f"Link {i} {j} is inactive")
        return self.edge_states[i, j, 1]

    def _decrement_link_duration(self, i, j):
        if not self._edge_exists(i, j):
            raise ValueError(f"Edge {i} {j} is not in the graph")
        if self.edge_states[i, j, 0] == -1:
            raise ValueError(f"Link {i} {j} is inactive")
        self._set_link_duration(i, j, self._get_link_duration(i, j) - 1)

    def _is_link_assigned(self, i, j):
        if not self._edge_exists(i, j):
            raise ValueError(f"Edge {i} {j} is not in the graph")
        if self.edge_states[i, j, 0] == -1:
            raise ValueError(f"Link {i} {j} is inactive")
        return self.edge_states[i, j, 1] > 0


    def get_possible_experiment_assignments(self, experiment):
        """
        Returns a list of possible experiment assignments for the given experiment w.r.t the current network state.
        Experiment is a tuple (adjacency_matrix, duration).

        Links are only considered if they are active and have an age greater than or equal to the experiment duration.
        """
        adjacency_matrix, duration = experiment

        # build a temporary graph with the given adjacency matrix
        temp_graph = igraph.Graph.Adjacency(adjacency_matrix, mode="undirected")
        exp_edges = temp_graph.get_edgelist()

        # build a graph of the current network state
        # transform the edge_states matrix into an adjacency matrix
        active_graph = igraph.Graph.Adjacency(self.__edge_states_to_adjacency_matrix(duration), mode="undirected")

        # get all subgraphs of the temporary graph that are isomorphic to the active graph
        isomorphic_subgraphs = active_graph.get_subisomorphisms_lad(temp_graph)
        
        # unique under relabeling of nodes
        unique_assignments = {}
        for m in isomorphic_subgraphs:
            physical_links = []
            for u, v in exp_edges:
                p_u, p_v = m[u], m[v]
                physical_links.append(tuple(sorted((p_u, p_v))))
            
            resource_key = frozenset(physical_links)
            
            if resource_key not in unique_assignments:
                unique_assignments[resource_key] = m
                

        return list(unique_assignments.values())

    def get_valid_swaps(self):
        """
        Identifies all triplets (i, j, k) where a swap is physically possible.
        """
        valid_triplets = []
        for j in range(self._N):
            # Find all nodes i connected to j by an active, unassigned link
            neighbors = []
            for i in range(self._N):
                if i != j and self._edge_exists(i, j) and self._is_link_active(i, j) and not self._is_link_assigned(i, j):
                    neighbors.append(i)
            
            # If node j has at least 2 such neighbors, any pair of them is a valid swap
            if len(neighbors) >= 2:
                import itertools
                for i, k in itertools.combinations(neighbors, 2):
                    valid_triplets.append((i, j, k))
        return valid_triplets

    def assign_experiment(self, experiment, mapping):
        adjacency_matrix, duration = experiment
        # iterate through the edges in the experiment adjacency matrix
        for i in range(adjacency_matrix.shape[0]):
            for j in range(adjacency_matrix.shape[1]):
                if adjacency_matrix[i, j] == 1:
                    # get the mapping for subgraph edge (i, j)
                    print(f"Mapping: {mapping} i: {i} j: {j}")
                    _i = mapping[i]
                    _j = mapping[j]

                    # assign the duration to the edge (_i, _j)
                    self._set_link_duration(_i, _j, duration)


    """
    This function updates the environment
    - Increments the age of each active link by 1.
    - Attempts to activate each inactive link with success probability p_link.
    - If an active link's age is greater than mstar, it is deactivated and set to -1.
    """
    def env_step(self):
        # iterate over all links and increment their age if active, otherwise activate
        for i in range(self._N):
            for j in range(i + 1, self._N): # only iterate over upper triangle to avoid double counting
                if not self._edge_exists(i, j):
                    continue
                if self._is_link_active(i, j):
                    if self._is_link_assigned(i, j):
                        # decrement the duration of the link
                        if self._get_link_duration(i, j) > 0:
                            self._decrement_link_duration(i, j)
                    self._increment_link_age(i, j)
                    if self._get_link_age(i, j) > self.mstar: # deactivation
                        self._deactivate_link(i, j)
                
                else:
                    self._activate_link(i, j)

    def get_observation(self):
        return {
            "edge_states": self.edge_states,
            "memory_states": self.memory_states,
            "possible_experiment_assignments": [self.get_possible_experiment_assignments(experiment) for experiment in self.experiments],
            "mstar": self.mstar,
        }

