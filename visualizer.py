import matplotlib.pyplot as plt
import igraph
import numpy as np

class NetworkVisualizer:
    def __init__(self, network, figsize=(10, 10)):
        self.network = network
        self.figsize = figsize
        # Precompute layout based on static topology for consistency across steps
        self.layout = self.network.net_graph.layout_kamada_kawai()
        
        # Define Color Palette
        self.colors = {
            "inactive": "#d3d3d3",    # Light Grey
            "available": "#3498db",   # Blue
            "assigned": "#e74c3c",    # Red
            "text": "#2c3e50"
        }

    def render(self, step_label=None):
        """
        Renders the current state of the network.
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # 1. Prepare Edge Attributes
        edge_colors = []
        edge_widths = []
        edge_labels = []
        
        # Iterate through edges of the static topology
        for edge in self.network.net_graph.es:
            i, j = edge.tuple
            age = self.network.edge_states[i, j, 0]
            duration = self.network.edge_states[i, j, 1]
            
            if age == -1:
                edge_colors.append(self.colors["inactive"])
                edge_widths.append(1.0)
                edge_labels.append("")
            elif duration > 0:
                edge_colors.append(self.colors["assigned"])
                edge_widths.append(4.0)
                edge_labels.append(f"A:{age}\nD:{duration}")
            else:
                edge_colors.append(self.colors["available"])
                edge_widths.append(2.5)
                edge_labels.append(f"A:{age}")

        # 2. Prepare Vertex Attributes
        vertex_labels = [
            f"ID:{i}\nMem:{self.network.memory_states[i]}" 
            for i in range(self.network._N)
        ]

        # 3. Plot using igraph
        igraph.plot(
            self.network.net_graph,
            target=ax,
            layout=self.layout,
            vertex_size=40,
            vertex_color="white",
            vertex_frame_width=2,
            vertex_frame_color=self.colors["text"],
            vertex_label=vertex_labels,
            vertex_label_size=10,
            vertex_label_color=self.colors["text"],
            edge_color=edge_colors,
            edge_width=edge_widths,
            edge_label=edge_labels,
            edge_label_size=8,
            autocurve=True
        )

        title = f"Quantum Network State (m*={self.network.mstar})"
        if step_label is not None:
            title += f" - Step: {step_label}"
        
        ax.set_title(title, fontsize=15, fontweight='bold')
        plt.show()