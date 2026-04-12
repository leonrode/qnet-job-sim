"""
This module implemnts the environment as the markov decision process (S, A, P, R)
in the form of matrices and uses igraph purely for subgraph isomorphism checking.
"""

import numpy as np
import igraph
import random
import matplotlib.pyplot as plt
import itertools
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
    def __edge_states_to_adjacency_matrix(self, duration):
        """
        Returns the adjacency matrix of the subnetwork of active links whose age >= duration
        """
        adjacency_matrix = np.zeros((self._N, self._N), dtype=np.int16)
        for i in range(self._N):
            for j in range(self._N):
                if self.edge_states[i, j, 0] != -1                    and \
                   self.mstar - self.edge_states[i, j, 0] >= duration and \
                   not self._is_link_assigned(i, j): # active link with age <= mstar - duration
                    adjacency_matrix[i, j] = 1 # indicate presence of edge
        return adjacency_matrix
    
    def __active_unassigned_links_graph(self, age=0):
        """
        Returns the adjacency matrix of the subgraph of active, unassigned links of age >= `age`
        """
        adjacency_matrix = np.zeros((self._N, self._N), dtype=np.int16)
        for i in range(self._N):
            for j in range(self._N):
                if self._edge_exists(i, j) and \
                   self._is_link_active(i, j)                        and \
                   self._get_link_age(i, j) >= age                   and \
                   not self._is_link_assigned(i, j): # active link with age <= mstar - duration
                    adjacency_matrix[i, j] = 1 # indicate presence of edge
        return adjacency_matrix

    def _get_generateable_virtual_links(self):
        """
        Returns a list of all node pairs (i, j) that can currently form a virtual link.
        A virtual link is possible if:
        1. A path of active, unassigned links exists between i and j.
        2. No physical link or active virtual link currently exists between i and j.
        """
        # 1. Build the adjacency matrix for the subgraph of active, unassigned links
        # This includes both physical and existing virtual links that are active
        active_unassigned_adj = self.__active_unassigned_links_graph()
        
        # 2. Create a temporary igraph object to analyze reachability
        g = igraph.Graph.Adjacency(active_unassigned_adj, mode="undirected")
        
        # 3. Find connected components (nodes that can reach each other)
        components = g.connected_components()
        
        possible_virtual_links = []
        
        for component in components:
            # We need at least 2 nodes to form a pair
            if len(component) < 2:
                continue
            
            # 4. For every unique pair in the component, check if they are already connected
            for i, j in itertools.combinations(component, 2):
                # _edge_exists returns True if they are physical neighbors 
                # OR if they already have an active virtual link.
                if not self._edge_exists(i, j):
                    # Use sorted tuple to maintain consistency (i < j)
                    possible_virtual_links.append(tuple(sorted((i, j))))
        
        return possible_virtual_links
 

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
    def _get_memory_count(self, i):
        if i < 0 or i >= self._N:
            raise ValueError(f"Node {i} is not in the network")
        return self.memory_states[i]
    
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
        return self.net_graph.are_connected(i, j) or self.edge_states[i, j, 0] != -1
    
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
    
    def assign_virtual_link(self, i, j):
        """
        Assigns a virtual link between nodes i and j on the graph.

        The operation succeeds only if a path of active, unassigned links exists between i and j on the graph and the
        age of each link in the path is greater than the length of the path (prevents links dying before virtual link is created).

        The operation is performed instantaneously, i.e. all intermediate links are deactivated in the process of creating the virtual link.
        """

        if self._edge_exists(i, j):
            return False # would be masked out 
            raise ValueError(f"Edge {i} {j} already exists")
        

        # get the graph of active links between i and j
        active_graph = igraph.Graph.Adjacency(self.__active_unassigned_links_graph(), mode="undirected")
        
        # get the shortest path between i and j
        path = active_graph.get_shortest_path(i, j, output="vpath")

        #print(f"Path between {i} and {j}: {path}")
        if len(path) < 2:
            return False
        
        # calculate the maximum age of the intermediate links
        virtual_link_age = 0
        for k in range(1, len(path)):
            age = self._get_link_age(path[k-1], path[k])
            virtual_link_age = max(virtual_link_age, age)

            self._deactivate_link(path[k-1], path[k])

        # self._deactivate_link will increment the memories of end points,
        # so we decrement the end points again for the new virtual link
        self._decrement_memory(i)
        self._decrement_memory(j)

        self.edge_states[i, j, 0] = virtual_link_age # set age to 0
        self.edge_states[i, j, 1] = 0 # ensure unassigned

        self.edge_states[j, i, 0] = virtual_link_age # set age to 0
        self.edge_states[j, i, 1] = 0 # ensure unassigned

        return True


    def __get_active_topology(self, duration):
            """
            Generates an adjacency matrix of all links (physical or virtual) 
            that are active, unassigned, and will survive for the 'duration'.
            """
            adj = np.zeros((self._N, self._N), dtype=np.int16)
            
            # A link survives if: current_age + duration <= mstar
            # => current_age <= mstar - duration
            max_age = self.mstar - duration
            
            for i in range(self._N):
                for j in range(i + 1, self._N):
                    age = self.edge_states[i, j, 0]
                    is_assigned = self.edge_states[i, j, 1] > 0
                    
                    if age != -1 and age <= max_age and not is_assigned:
                        adj[i, j] = 1
                        adj[j, i] = 1
            return adj
    def get_possible_experiment_assignments(self, experiment):
        """
        Returns a list of possible experiment assignments for the given experiment w.r.t the current network state.
        Experiment is a tuple (adjacency_matrix, duration).

        Links are only considered if they are active, unassigned, and have an age greater than or equal to the experiment duration.
        """
        adj_matrix, duration = experiment

        # 1. Build the target graph (the experiment structure)
        temp_graph = igraph.Graph.Adjacency(adj_matrix, mode="undirected")
        exp_edges = temp_graph.get_edgelist()

        # 2. Build the current available graph (Physical + Virtual)
        # Only include links that won't decohere before the experiment ends
        active_adj = self.__get_active_topology(duration)
        active_graph = igraph.Graph.Adjacency(active_adj, mode="undirected")

        # 3. Find subisomorphisms (mappings from experiment to active network)
        isomorphic_subgraphs = active_graph.get_subisomorphisms_lad(temp_graph)
        
        unique_assignments = {}
        for m in isomorphic_subgraphs:
            # Map experiment edges to physical/virtual node IDs
            resource_links = []
            for u, v in exp_edges:
                p_u, p_v = m[u], m[v]
                resource_links.append(tuple(sorted((p_u, p_v))))
            
            # Key by the set of links used to avoid duplicates from symmetry
            resource_key = frozenset(resource_links)
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
        # iterate over all links and increment their age if active, otherwise activate if they have enough memories
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
                
                elif self._has_unused_memory(i) and self._has_unused_memory(j):
                    self._activate_link(i, j)

    def get_observation(self):
        return {
            "edge_states": self.edge_states,
            "memory_states": self.memory_states,
            "possible_experiment_assignments": [self.get_possible_experiment_assignments(experiment) for experiment in self.experiments],
            "mstar": self.mstar,
        }

