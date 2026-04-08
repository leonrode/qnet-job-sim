from network import Network
from experiment_queue import ExperimentQueue
class Environment:
    
    def __init__(self, adjacency_matrix, experiments):
        self.network = Network(adjacency_matrix) 
        self.experiment_queue = ExperimentQueue()

    def add_experiments_to_queue(self, experiments):
        for experiment in experiments:
            self.experiment_queue.add_experiment(experiment)

