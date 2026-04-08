import queue

class ExperimentQueue:
    def __init__(self):
        # queue of type Experiment
        self.queue = queue.Queue()
    
    def add_experiment(self, experiment):
        self.queue.put(experiment)
    
    def get_experiment(self):
        return self.queue.get()
    
    def is_empty(self):
        return self.queue.empty()
    
    def size(self):
        return self.queue.qsize()