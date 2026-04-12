import igraph

complete_grid_graph = igraph.Graph.Full(9)

experiments = [[
    # 0 1 2 3
    [0, 1, 1],
    [1, 0, 1],
    [1, 1, 0]
],
[
    [0, 1, 0, 1],
    [1, 0, 1, 0],
    [0, 1, 0, 1],
    [1, 0, 1, 0],
],
[
    [0, 1, 0, 0, 0, 1],
    [1, 0, 1, 0, 0, 0],
    [0, 1, 0, 1, 0, 0],
    [0, 0, 1, 0, 1, 0],
    [0, 0, 0, 1, 0, 1],
    [1, 0, 0, 0, 1, 0]
],
[
    [0, 1, 0, 0, 0, 1],
    [1, 0, 1, 0, 0, 1],
    [0, 1, 0, 1, 1, 0],
    [0, 0, 1, 0, 1, 0],
    [0, 0, 1, 1, 0, 1],
    [1, 1, 0, 0, 1, 0],
]]

for experiment in experiments:
    experiment_graph = igraph.Graph.Adjacency(experiment, mode="undirected")
    exp_edges = experiment_graph.get_edgelist()
    isomorphic_subgraphs = complete_grid_graph.get_subisomorphisms_lad(experiment_graph)
        
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
            
    mappings = list(unique_assignments.values())
    print(f"Experiment {experiment} has {len(mappings)} mappings")
    print(f"First mapping: {mappings[0]}")
    #print(f"Mappings: {mappings}")