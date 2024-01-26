# Sample list of dictionaries
import networkx as nx
import matplotlib.pyplot as plt  # Optional for visualization


def create_citation_plot(data, output_dir):
    # Create an empty graph
    G = nx.MultiDiGraph()

    # Add edges from the list of dictionaries
    for d in data:
        for key, values in d.items():
            for v in values:
                G.add_edge(key, str(v))

    nx.draw(G, with_labels=True, font_weight='bold')
    plt.savefig(f"{output_dir}/graph.png", format="PNG")

    


