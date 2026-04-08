import igraph

class Experiment:
    def __init__(self, adjacency_matrix, duration):
        self.adjacency_matrix = adjacency_matrix
        self.topology = igraph.Graph.Adjacency(adjacency_matrix, mode="undirected")
        self.duration = duration

    