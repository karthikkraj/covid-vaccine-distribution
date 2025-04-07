def create_vaccine_distribution_network(network_nodes, mobility_df):
    """
    Create a network model of vaccine distribution.
    - Nodes: Countries
    - Attributes: Population, vaccination rates, manufacturing capacity
    - Edges: Transportation connections, trade relationships
    """
    print("Creating vaccine distribution network...")
    
    # Create an empty directed graph
    G = nx.DiGraph()
    
    # Add countries as nodes with their attributes
    for _, row in network_nodes.iterrows():
        G.add_node(
            row['country_name'],
            population=row['population'],
            population_density=row.get('population_density', 0),
            vaccinated_pct=row.get('people_vaccinated_per_hundred', 0),
            fully_vaccinated_pct=row.get('people_fully_vaccinated_per_hundred', 0),
            # Dummy data for manufacturing capacity - you would replace this with real data
            manufacturing_capacity=np.random.randint(0, 100) if row['country_name'] in 
                ['United States', 'United Kingdom', 'Germany', 'China', 'India', 'Russia', 'South Korea'] else 0
        )
    
    # Add edges based on geographical proximity and vaccine trade relationships
    # For demonstration, we'll create edges between major manufacturing countries and others
    # In a real implementation, you would use actual trade or transportation data
    
    manufacturing_countries = ['United States', 'United Kingdom', 'Germany', 'China', 'India', 'Russia', 'South Korea']
    
    # Create connections from manufacturing countries to others
    for m_country in manufacturing_countries:
        if m_country not in G.nodes():
            continue
            
        # Connect to countries with low vaccination rates first (prioritize)
        for country in G.nodes():
            if country != m_country:
                # Calculate edge weight based on vaccination need and population
                vax_need = 100 - G.nodes[country].get('vaccinated_pct', 0)
                population_factor = G.nodes[country].get('population', 0) / 1e9  # Normalize by billion
                
                # Edge attributes
                capacity = G.nodes[m_country]['manufacturing_capacity'] * population_factor
                priority_score = vax_need * population_factor
                
                # Add edge with attributes
                G.add_edge(
                    m_country, 
                    country, 
                    capacity=capacity,
                    priority=priority_score,
                    distance=np.random.randint(500, 10000)  # Dummy distance in km
                )
    
    print(f"Network created with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")
    return G

def analyze_network(G):
    """
    Analyze the vaccine distribution network to identify key metrics and bottlenecks.
    """
    print("\nAnalyzing network characteristics...")
    
    # Basic network statistics
    print(f"Network has {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
    
    # Identify important nodes using centrality measures
    # Degree centrality - countries with many direct connections
    degree_centrality = nx.degree_centrality(G)
    top_degree = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)[:5]
    print("\nTop 5 countries by connectivity (degree centrality):")
    for country, score in top_degree:
        print(f"{country}: {score:.4f}")
    
    # Betweenness centrality - countries that serve as bridges in the network
    betweenness_centrality = nx.betweenness_centrality(G)
    top_betweenness = sorted(betweenness_centrality.items(), key=lambda x: x[1], reverse=True)[:5]
    print("\nTop 5 countries as distribution hubs (betweenness centrality):")
    for country, score in top_betweenness:
        print(f"{country}: {score:.4f}")
    
    # Calculate flow capacity and bottlenecks
    print("\nAnalyzing distribution capacity and bottlenecks...")
    
    # Identify nodes with manufacturing capacity
    manufacturers = [n for n, attr in G.nodes(data=True) if attr.get('manufacturing_capacity', 0) > 0]
    
    # Find bottlenecks - countries with high need but limited incoming capacity
    bottlenecks = []
    for node in G.nodes():
        in_capacity = sum(G[u][node]['capacity'] for u in G.predecessors(node))
        need = G.nodes[node]['population'] * (100 - G.nodes[node].get('vaccinated_pct', 0)) / 100
        if need > 0 and in_capacity/need < 0.5:  # Less than 50% of need can be met
            bottlenecks.append((node, need, in_capacity))
    
    # Sort bottlenecks by severity (capacity/need ratio)
    bottlenecks.sort(key=lambda x: (x[2]/x[1] if x[1] > 0 else float('inf')))
    
    print("\nTop bottlenecks in the distribution network:")
    for country, need, capacity in bottlenecks[:10]:
        if need > 0:
            print(f"{country}: Can supply only {capacity/need*100:.1f}% of vaccination need")
    
    return {
        'degree_centrality': degree_centrality,
        'betweenness_centrality': betweenness_centrality,
        'bottlenecks': bottlenecks,
        'manufacturers': manufacturers
    }

def visualize_network(G, analysis_results):
    """
    Create visualizations of the vaccine distribution network.
    """
    plt.figure(figsize=(12, 10))
    
    # Node colors based on vaccination rates
    node_colors = [100 - G.nodes[n].get('vaccinated_pct', 0) for n in G.nodes()]
    
    # Node sizes based on population
    node_sizes = [np.sqrt(G.nodes[n].get('population', 0)) / 1000 for n in G.nodes()]
    
    # Edge weights based on capacity
    edge_weights = [G[u][v]['capacity']/10 for u, v in G.edges()]
    
    # Position nodes using layout algorithm
    pos = nx.spring_layout(G, seed=42)
    
    # Draw the network
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes, 
                          cmap=plt.cm.YlOrRd, alpha=0.8)
    nx.draw_networkx_edges(G, pos, width=edge_weights, alpha=0.4, edge_color='grey', 
                          arrowsize=10)
    
    # Label only important nodes
    important_nodes = set(analysis_results['manufacturers'])  # Add manufacturers
    important_nodes.update([n for n, _ in sorted(analysis_results['betweenness_centrality'].items(), 
                                               key=lambda x: x[1], reverse=True)[:5]])  # Add top hubs
    
    # Add labels for important nodes
    labels = {n: n for n in important_nodes if n in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=10, font_weight='bold')
    
    plt.title('COVID-19 Vaccine Distribution Network', fontsize=16)
    plt.colorbar(plt.cm.ScalarMappable(cmap=plt.cm.YlOrRd), 
                label='Vaccination need (higher = less vaccinated)')
    plt.axis('off')
    plt.tight_layout()
    
    return plt

# Example usage continued
def create_and_analyze_network(network_nodes, mobility_df):
    G = create_vaccine_distribution_network(network_nodes, mobility_df)
    analysis_results = analyze_network(G)
    plot = visualize_network(G, analysis_results)
    plot.savefig('vaccine_distribution_network.png', dpi=300)
    plt.close()
    print("\nNetwork visualization saved as 'vaccine_distribution_network.png'")
    return G, analysis_results
