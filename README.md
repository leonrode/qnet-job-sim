# qnet-job-sim

Repository for working code related to the research project.

An Overleaf is in progress. For now, please see `notes.pdf` for a rough overview.

Most working code is in `matrix_network.py` and `main.py`.

`matrix_network.py` exposes a `MatrixNetwork` class that handles the dynamics of the environment (probabilistic link generation, aging, etc.). 

`main.py` contains the driver code, defining a grid network with max link age $m^* = 10$ time steps and a square experiment topology with a duration of 5 time steps.

Install the dependencies in `requirements.txt` and run `main.py`. The network will be plotted at each time step (close the plot to continue to the next time step) indefinitely. 

## Next Steps

### 1. Deciding the learning architecture

The architecture we use depends on the properties of our environment. For example, the action space is non uniform in each time step, requiring techniques like action masking. 

### 2. Implementation

Using `tensorflow` to implement the learning model will be trivial with the exposed subroutines (in particular, `.step()`) from `MatrixNetwork`. 