import itertools
import networkx as nx

def build_connection_graph(data, output_dir):
    # Create an empty graph
    G = nx.Graph()

    keys = [list(d.keys())[0] for d in data]
    realtions = [list(d.values())[0]['related_papers'] for d in data]

    for d in data:
        key = list(d.keys())[0]
        node_data = list(d.values())[0]['metadata']
        G.add_node(key, **node_data)
    
    # Create edges between keys with intersecting values
    for pair in itertools.combinations(keys, 2):
        intersection = len(set(realtions[keys.index(pair[0])]).intersection(set(realtions[keys.index(pair[1])])))
        if intersection > 0:
            G.add_edge(pair[0], pair[1], weight=intersection)
    G.remove_nodes_from(list(nx.isolates(G)))
    return G

