import streamlit as st
import matplotlib.pyplot as plt
from main import create_connection_plot
import networkx as nx
import pickle
import streamlit.components.v1 as components
import plotly.graph_objects as go

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
        # pickle.dump(G, open('graph.pkl', 'wb'))
        # G = pickle.load(open('graph.pkl', 'rb'))

        pos = nx.spring_layout(G, weight='weight')  # positions for all nodes based on edge weight
        node_size_weights = [sum([d['weight'] for (_, v, d) in G.edges(data=True) if v == n]) for n in G.nodes()]
        node_sizes =[x*100/ sum(node_size_weights) for x in node_size_weights]

        colors = ['blue', 'red', 'green', 'yellow', 'orange', 'purple']

        node_colors = []
        for i in range(len(G.nodes())):
            idx = node_size_weights[i]
            idx = idx%len(colors)
            node_colors.append(colors[idx])


        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines')

        node_x = []
        node_y = []
        node_text = []  # List to store node hover text

        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_text.append(G.nodes.get(node)['arxivlink'])

        node_trace = go.Scatter(
            x=node_x, y=node_y, 
            mode='markers',
            hoverinfo='text',
            marker=dict(
                size=node_sizes,
                showscale=True,
                colorscale='YlGnBu',
                reversescale=True,
                color=node_colors,
                # size=10,
                colorbar=dict(
                    thickness=15,
                    title='Node Connections',
                    xanchor='left',
                    titleside='right'
                ),
                line_width=2))

        node_trace.text = node_text


        # Define the on_click behavior
        # node_trace.on_click(lambda x, y: print(f"Node ID: {x}"))

        # # Define the callback function
        # def display_params(trace, points, selector):
        #     print('clicked')
        #     print(trace, points, selector)
        #     point_id = points.point_inds[0]
        #     params = trace.customdata[point_id]
        #     print(params)  # Replace with your desired action to display the parameters

        # # Add the on_click event to the node_trace
        # node_trace.on_click(display_params)

        fig = go.Figure(data=[edge_trace, node_trace],
                        layout=go.Layout(
                            title='Network Graph with Plotly',
                            titlefont_size=16,
                            showlegend=False,
                            hovermode='closest',
                            margin=dict(b=20, l=5, r=5, t=40),
                            annotations=[dict(
                                text="Python code: <a href='https://plotly.com/python/'>Plotly</a>",
                                showarrow=False,
                                xref="paper", yref="paper",
                                x=0.005, y=-0.002)],
                            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                        ))
        fig.add_trace(node_trace)

        # Plot on Streamlit
        clicked_node = st.plotly_chart(fig, use_container_width=True)
        # nodeskey = list(G.nodes.keys())
        # while clicked_node:
        #     # st.write(G.nodes.get(clicked_node)['title'])
        #     idx = clicked_node.__dict__['_provided_cursor'].__dict__['_index']
        #     _id = nodeskey[idx]
        #     st.write(G.nodes.get(_id))


if __name__ == "__main__":
    main()
