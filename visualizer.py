import matplotlib.pyplot as plt
import igraph

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
            "virtual": "#27ae60",     # Green (active link between nodes with no physical edge)
            "text": "#2c3e50"
        }

    def _iter_virtual_links(self):
        """
        Yields (i, j) with i < j for active entanglement where no physical topology edge exists
        (see MatrixNetwork.assign_virtual_link — edge_states may be set off net_topology).
        """
        for i in range(self.network._N):
            for j in range(i + 1, self.network._N):
                if self.network.net_graph.are_connected(i, j):
                    continue
                if self.network.edge_states[i, j, 0] != -1:
                    yield i, j

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

        # Virtual links: direct (i, j) where entanglement exists but no physical edge (matrix_network.assign_virtual_link)
        for i, j in self._iter_virtual_links():
            age = self.network.edge_states[i, j, 0]
            duration = self.network.edge_states[i, j, 1]
            xi, yi = self.layout[i]
            xj, yj = self.layout[j]
            if duration > 0:
                vcolor = self.colors["assigned"]
                vwidth = 4.0
                vlabel = f"V:{age}\nD:{duration}"
            else:
                vcolor = self.colors["virtual"]
                vwidth = 2.5
                vlabel = f"VA:{age}"
            ax.plot(
                [xi, xj], [yi, yj],
                color=vcolor,
                linewidth=vwidth,
                zorder=2,
                solid_capstyle="round",
            )
            ax.text(
                (xi + xj) / 3, (yi + yj) / 3, # offset from the center of the edge
                vlabel,
                fontsize=8,
                ha="center",
                va="center",
                color=self.colors["text"],
                zorder=3,
            )

        title = f"Quantum Network State (m*={self.network.mstar})"
        if step_label is not None:
            title += f" - Step: {step_label}"
        
        ax.set_title(title, fontsize=15, fontweight='bold')
        plt.show()