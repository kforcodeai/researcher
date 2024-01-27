import streamlit as st
import matplotlib.pyplot as plt
from main import create_connection_plot
import networkx as nx

# Streamlit app
def main():
    st.title("Paper Search and Plot App")

    # Search bar for keywords
    keyword = st.text_input(
        "Enter keywords to search", "Large language Model based agents"
    )

    # Slider for number of results
    num_results = st.slider(
        "Select number of results to return", min_value=2, max_value=20, value=5
    )

    # Button to trigger the search and plot
    if st.button("Search and Plot"):
        G = create_connection_plot(keyword, num_results)
        fig, ax = plt.subplots()
        pos = nx.spring_layout(G, weight='weight')  # positions for all nodes based on edge weight
        node_sizes = [sum([d['weight'] for (_, v, d) in G.edges(data=True) if v == n]) * 200 for n in G.nodes()]
        node_color_map = plt.cm.viridis
        nx.draw(G, pos, with_labels=True, node_color=range(len(G)), cmap=node_color_map, node_size=node_sizes, font_size=8, font_weight='bold', edge_color='gray', width=0.5, edge_cmap=plt.cm.Blues)
        labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, font_size=8)
        st.pyplot(fig)


if __name__ == "__main__":
    main()
