import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def create_vaccine_distribution_network(network_nodes, mobility_df, threshold=0.3):
    """Create a more realistic vaccine distribution network"""
    G = nx.DiGraph()  # Use directed graph for shipment flows
    
    # Add manufacturing hubs as special nodes
    manufacturers = ['US', 'IN', 'EU', 'CN']
    for mfg in manufacturers:
        G.add_node(mfg, type='manufacturer', capacity=100000000)
    
    # Add country nodes with vaccination data
    for _, row in network_nodes.iterrows():
        # Calculate days since last vaccination based on doses administered
        last_vax_days = 180  # Default to 6 months if no recent data
        if 'new_vaccine_doses_administered' in row and row['new_vaccine_doses_administered'] > 0:
            last_vax_days = 30  # If recent vaccinations, assume last month
        elif 'cumulative_vaccine_doses_administered' in row and row['cumulative_vaccine_doses_administered'] > 0:
            last_vax_days = 90  # If some vaccinations but none recent, assume 3 months
            
        G.add_node(row['country_code'],
                 type='country',
                 population=row['population'],
                 vaccination_rate=row.get('people_vaccinated_per_hundred', 0),
                 last_vaccination_date=(pd.Timestamp.now() - pd.Timedelta(days=last_vax_days)).strftime('%Y-%m-%d'),
                 name=row['country_name'])
    
    # Add edges based on significant mobility (above threshold)
    for key, weight in mobility_df.items():
        if isinstance(key, tuple) and len(key) == 2 and weight > threshold:
            c1, c2 = key
            G.add_edge(c1, c2, weight=float(weight), type='transport')
    
    # Connect manufacturers to countries
    for mfg in manufacturers:
        for country in G.nodes():
            if G.nodes[country]['type'] == 'country':
                # Base connection weight on population and existing vaccination rate
                weight = (G.nodes[country]['population'] / 1e6) * \
                        (100 - G.nodes[country]['vaccination_rate']) / 100
                G.add_edge(mfg, country, weight=weight, type='shipment')
    
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
    """Create enhanced visualizations for directed vaccine network"""
    plt.figure(figsize=(20, 12))
    pos = nx.spring_layout(G, k=0.5, iterations=50)
    
    # Draw nodes with different styles for manufacturers and countries
    country_nodes = [n for n in G.nodes() if G.nodes[n]['type'] == 'country']
    mfg_nodes = [n for n in G.nodes() if G.nodes[n]['type'] == 'manufacturer']
    
    # Draw country nodes
    nx.draw_networkx_nodes(G, pos, nodelist=country_nodes,
                         node_color=[G.nodes[n]['vaccination_rate'] for n in country_nodes],
                         node_size=[G.nodes[n]['population']/1e6 for n in country_nodes],
                         cmap=plt.cm.YlOrRd, alpha=0.8)
    
    # Draw manufacturer nodes with capacity labels
    nx.draw_networkx_nodes(G, pos, nodelist=mfg_nodes,
                         node_color='green',
                         node_size=500,
                         node_shape='s')
    
    # Add capacity labels for manufacturers
    mfg_labels = {n: f"{n}\n{G.nodes[n]['capacity']/1e6:.1f}M" for n in mfg_nodes}
    nx.draw_networkx_labels(G, pos, mfg_labels, font_size=8, font_color='white')
    
    # Draw edges with different styles
    transport_edges = [(u,v) for (u,v,d) in G.edges(data=True) if d['type'] == 'transport']
    shipment_edges = [(u,v) for (u,v,d) in G.edges(data=True) if d['type'] == 'shipment']
    
    nx.draw_networkx_edges(G, pos, edgelist=transport_edges,
                          edge_color='gray', width=0.5, alpha=0.3,
                          connectionstyle='arc3,rad=0.1')
    
    nx.draw_networkx_edges(G, pos, edgelist=shipment_edges,
                          edge_color='red', width=1.5, alpha=0.7,
                          arrows=True, arrowstyle='->',
                          connectionstyle='arc3,rad=0.1')
    
    # Add labels - handle both country and manufacturer nodes
    labels = {}
    for n in G.nodes():
        if 'name' in G.nodes[n]:
            labels[n] = G.nodes[n]['name']
        else:
            labels[n] = f"{n} (Mfg)"
    nx.draw_networkx_labels(G, pos, labels, font_size=8)
    
    plt.title("Enhanced Vaccine Distribution Network")
    
    # Create proper mappable for colorbar
    sm = plt.cm.ScalarMappable(cmap=plt.cm.YlOrRd,
                             norm=plt.Normalize(vmin=0, vmax=100))
    sm.set_array([])
    plt.colorbar(sm, ax=plt.gca(), label='Vaccination Rate (%)')
    
    plt.savefig(f"{output_dir}/enhanced_network.png", dpi=300, bbox_inches='tight')
    plt.close()
