import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def create_vaccine_distribution_network(network_nodes, mobility_df):
    """Create a network representation of vaccine distribution system"""
    G = nx.Graph()
    
    # Add nodes (countries) with their attributes
    for _, row in network_nodes.iterrows():
        G.add_node(row['country_code'],
                  population=row['population'],
                  vaccinated=row.get('cumulative_persons_vaccinated', 0),
                  vaccination_rate=row.get('people_vaccinated_per_hundred', 0),
                  last_vaccination_date='2022-09-16',  # Using date from processed data
                  name=row['country_name'])
    
    # Add edges based on mobility data
    for country1 in G.nodes():
        for country2 in G.nodes():
            if country1 != country2:
                # Use mobility data as edge weight
                weight = mobility_df.get((country1, country2), 0.1)
                G.add_edge(country1, country2, weight=weight)
    
    return G

def analyze_network(G):
    """Analyze network properties"""
    results = {
        'degree_centrality': nx.degree_centrality(G),
        'betweenness_centrality': nx.betweenness_centrality(G),
        'bottlenecks': [],
        'manufacturers': [],
        'network': G  # Add the network itself to results
    }
    
    # Identify potential bottlenecks
    for node in G.nodes():
        degree = G.degree(node)
        betweenness = results['betweenness_centrality'][node]
        if degree > np.mean([G.degree(n) for n in G.nodes()]) and betweenness > 0.1:
            results['bottlenecks'].append((node, degree, betweenness))
    
    return results

def visualize_network(G, analysis_results, output_dir):
    """Create network visualization"""
    plt.figure(figsize=(15, 10))
    pos = nx.spring_layout(G)
    
    # Draw nodes
    nx.draw_networkx_nodes(G, pos, 
                          node_color=[G.nodes[node]['vaccination_rate'] for node in G.nodes()],
                          node_size=[G.nodes[node]['population']/1e6 for node in G.nodes()],
                          cmap=plt.cm.YlOrRd)
    
    # Draw edges
    nx.draw_networkx_edges(G, pos, alpha=0.2)
    
    # Add labels
    labels = {node: G.nodes[node]['name'] for node in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels, font_size=8)
    
    plt.title("Vaccine Distribution Network")
    plt.savefig(f"{output_dir}/network_visualization.png")
    plt.close()
