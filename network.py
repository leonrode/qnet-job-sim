import igraph
import numpy as np
import random
import matplotlib.pyplot as plt

class Network:
    def __init__(self, adjacency_matrix, gamma_link=1.0):
        self.seed = 42
        random.seed(self.seed)
        self.gamma_link = gamma_link
        self.graph = igraph.Graph.Adjacency(adjacency_matrix, mode="undirected")
        # set length attribute for each edge
        for e in self.graph.es:
            e["length"] = adjacency_matrix[e.source][e.target]
        # need a graph on top of this graph for which some
        # edges can be removed / added later
        self.active_graph = self.graph.copy()
        self.active_graph.delete_edges()

    def activate_edge(self, source, target):
        # check that edge is in self.graph
        if not self.graph.are_connected(source, target):
            raise ValueError(f"Edge {source} {target} is not in the graph")
        eid = self.graph.get_eid(source, target)
        # calculate p_link
        p_link = np.exp(-self.gamma_link * self.graph.es[eid]["length"])
        print(f"p_link: {p_link}")
        if random.random() < p_link:
            self.active_graph.add_edge(source, target)
            return True
        else:
            return False
   
    def step(self):
        # activate each edge in self.active_graph
        print(f"Number of edges before activation: {len(self.active_graph.es)}")
        for e in self.graph.es:
            self.activate_edge(e.source, e.target)
        print(f"Number of edges after activation: {len(self.active_graph.es)}")
        
        # 

        return self.active_graph

    def assign_experiment(self, experiment):
        # check to make sure the experiment fits in the network
        # if not, then we need to allow the use of virtual links to connect the nodes
        # required to make the experiment fit

        
        pass


    def show_active_graph(self, path=None):
        fig, ax = plt.subplots(figsize=(8, 8))

        # Render Graph to Axes
        igraph.plot(
            self.active_graph,
            target=ax,
            layout="kamada_kawai", # Force-directed layout
            vertex_size=0.3,
            vertex_color="steelblue",
            vertex_label=range(self.active_graph.vcount()),
            edge_width=1.5,
            edge_color="gray"
        )

        if path is not None:
            plt.savefig(path)
        else:
            plt.show()

    def show_graph(self, path=None):
        fig, ax = plt.subplots(figsize=(8, 8))
        igraph.plot(
            self.graph,
            target=ax,
            layout="kamada_kawai", # Force-directed layout
            vertex_size=0.3,
            vertex_color="steelblue",
            vertex_label=range(self.graph.vcount()),
        )
        if path is not None:
            plt.savefig(path)
        else:
            plt.show()

