import pulp
import numpy as np
from itertools import product

def optimize_vaccine_distribution(G, available_vaccines=1e9):
    """
    Optimize the distribution of vaccines across the network using linear programming.
    Uses PuLP for optimization.
    """
    print("\nOptimizing vaccine distribution...")
    
    # Create optimization problem
    problem = pulp.LpProblem("Vaccine_Distribution_Optimization", pulp.LpMaximize)
    
    # Extract nodes with manufacturing capability
    manufacturers = [n for n, attr in G.nodes(data=True) if attr.get('manufacturing_capacity', 0) > 0]
    recipients = list(G.nodes())
    
    # Create decision variables: how many vaccines to ship from each manufacturer to each recipient
    shipments = pulp.LpVariable.dicts("shipment", 
                                    [(m, r) for m in manufacturers for r in recipients],
                                    lowBound=0)
    
    # Objective: Maximize equity-weighted vaccination coverage
    # We prioritize countries with low current vaccination rates and high population
    objective_terms = []
    for r in recipients:
        current_vax = G.nodes[r].get('vaccinated_pct', 0)
        population = G.nodes[r].get('population', 0)
        
        # Equity weight: higher for less vaccinated countries
        equity_weight = (100 - current_vax) / 100
        
        # Sum of shipments to this recipient
        total_received = pulp.lpSum([shipments[(m, r)] for m in manufacturers if (m, r) in shipments])
        
        # Coverage improvement from new shipments (as percentage points)
        coverage_improvement = total_received / population * 100 if population > 0 else 0
        
        # Add weighted term to objective
        objective_terms.append(equity_weight * coverage_improvement)
    
    # Set objective function
    problem += pulp.lpSum(objective_terms)
    
    # Constraints
    # 1. Total vaccines allocated cannot exceed available amount
    problem += pulp.lpSum([shipments[(m, r)] for m, r in shipments]) <= available_vaccines
    
    # 2. Manufacturing capacity constraints
    for m in manufacturers:
        capacity = G.nodes[m].get('manufacturing_capacity', 0) * 1e6  # Convert to absolute numbers
        problem += pulp.lpSum([shipments[(m, r)] for r in recipients if (m, r) in shipments]) <= capacity
    
    # 3. Transportation capacity constraints (from network edges)
    for m, r in shipments:
        if G.has_edge(m, r):
            transport_capacity = G[m][r].get('capacity', 0) * 1e6  # Convert to absolute numbers
            problem += shipments[(m, r)] <= transport_capacity
        else:
            problem += shipments[(m, r)] == 0  # No shipment if no edge exists
    
    # Solve the optimization problem
    problem.solve(pulp.PULP_CBC_CMD(msg=False))
    
    print(f"Optimization status: {pulp.LpStatus[problem.status]}")
    
    # Extract and return results
    results = {
        'status': pulp.LpStatus[problem.status],
        'objective_value': pulp.value(problem.objective),
        'shipments': {(m, r): pulp.value(shipments[(m, r)]) 
                    for m, r in shipments if pulp.value(shipments[(m, r)]) > 0},
        'total_allocated': sum(pulp.value(shipments[(m, r)]) 
                            for m, r in shipments if pulp.value(shipments[(m, r)]) > 0)
    }
    
    # Calculate improvement in vaccination rates
    improvement_by_country = {}
    for r in recipients:
        total_received = sum(pulp.value(shipments[(m, r)]) 
                          for m in manufacturers if (m, r) in shipments)
        population = G.nodes[r].get('population', 0)
        if population > 0:
            improvement_points = total_received / population * 100
            improvement_by_country[r] = improvement_points
    
    results['improvement_by_country'] = improvement_by_country
    
    # Print summary statistics
    print(f"Total vaccines allocated: {results['total_allocated']:,.0f}")
    print(f"Number of countries receiving vaccines: {len([c for c, imp in improvement_by_country.items() if imp > 0])}")
    
    # Top recipients
    top_recipients = sorted(improvement_by_country.items(), key=lambda x: x[1], reverse=True)[:5]
    print("\nTop 5 countries by vaccination rate improvement:")
    for country, improvement in top_recipients:
        print(f"{country}: +{improvement:.2f} percentage points")
    
    return results

def analyze_optimization_results(G, optimization_results):
    """
    Analyze the results of the optimization model.
    """
    print("\nAnalyzing optimization results...")
    
    # Calculate equity improvement
    before_optimization = {}
    after_optimization = {}
    
    for country in G.nodes():
        population = G.nodes[country].get('population', 0)
        current_vax = G.nodes[country].get('vaccinated_pct', 0)
        
        before_optimization[country] = current_vax
        
        # Calculate new vaccination rate after optimization
        improvement = optimization_results['improvement_by_country'].get(country, 0)
        after_optimization[country] = min(current_vax + improvement, 100)  # Cap at 100%
    
    # Calculate Gini coefficient for vaccination rates before and after
    before_gini = calculate_gini([before_optimization[c] for c in G.nodes()])
    after_gini = calculate_gini([after_optimization[c] for c in G.nodes()])
    
    print(f"Equity impact (Gini coefficient for vaccination rates):")
    print(f"  Before optimization: {before_gini:.4f}")
    print(f"  After optimization: {after_gini:.4f}")
    print(f"  Improvement: {(before_gini - after_gini) / before_gini * 100:.2f}%")
    
    # Calculate coverage statistics
    before_avg = np.mean(list(before_optimization.values()))
    after_avg = np.mean(list(after_optimization.values()))
    
    print(f"\nVaccination coverage:")
    print(f"  Average before: {before_avg:.2f}%")
    print(f"  Average after: {after_avg:.2f}%")
    print(f"  Improvement: {after_avg - before_avg:.2f} percentage points")
    
    # Calculate logistics metrics
    shipment_count = len(optimization_results['shipments'])
    avg_shipment_size = (optimization_results['total_allocated'] / shipment_count 
                        if shipment_count > 0 else 0)
    
    print(f"\nLogistics metrics:")
    print(f"  Total shipments: {shipment_count}")
    print(f"  Average shipment size: {avg_shipment_size:,.0f} doses")
    
    # Identify remaining bottlenecks after optimization
    remaining_bottlenecks = []
    for country in G.nodes():
        population = G.nodes[country].get('population', 0)
        new_vax_rate = after_optimization[country]
        
        if new_vax_rate < 50:  # Countries with less than 50% vaccination rate still
            remaining_bottlenecks.append((country, new_vax_rate))
    
    remaining_bottlenecks.sort(key=lambda x: x[1])
    
    print(f"\nRemaining bottlenecks (countries with <50% vaccination after optimization):")
    for country, rate in remaining_bottlenecks[:5]:
        print(f"  {country}: {rate:.2f}%")
    
    return {
        'before_optimization': before_optimization,
        'after_optimization': after_optimization,
        'before_gini': before_gini,
        'after_gini': after_gini,
        'remaining_bottlenecks': remaining_bottlenecks
    }

def calculate_gini(values):
    """
    Calculate the Gini coefficient as a measure of inequality.
    Lower values = more equality, Higher values = more inequality
    """
    values = np.array(values)
    values = values[np.isfinite(values)]  # Remove any NaN values
    
    if len(values) == 0:
        return float('nan')
    
    # Sort values
    values = np.sort(values)
    
    # Calculate cumulative sum
    cum_values = np.cumsum(values)
    
    # Calculate Gini coefficient
    n = len(values)
    index = np.arange(1, n+1)
    return (n + 1 - 2 * np.sum(cum_values) / (cum_values[-1] * n)) / n

def visualize_optimization_results(G, analysis_results):
    """
    Create visualizations showing the impact of the optimization.
    """
    # 1. Bar chart of before/after vaccination rates for top 20 countries by population
    plt.figure(figsize=(12, 8))
    
    # Get countries sorted by population
    countries_by_pop = sorted(G.nodes(), key=lambda x: G.nodes[x].get('population', 0), reverse=True)[:20]
    
    # Extract before/after data
    before_rates = [analysis_results['before_optimization'][c] for c in countries_by_pop]
    after_rates = [analysis_results['after_optimization'][c] for c in countries_by_pop]
    
    # Set up bar positions
    bar_width = 0.35
    positions = np.arange(len(countries_by_pop))
    
    # Create bars
    plt.bar(positions - bar_width/2, before_rates, bar_width, label='Before Optimization', color='lightcoral')
    plt.bar(positions + bar_width/2, after_rates, bar_width, label='After Optimization', color='lightgreen')
    
    # Add labels and title
    plt.xlabel('Country')
    plt.ylabel('Vaccination Rate (%)')
    plt.title('Impact of Optimization on Vaccination Rates (Top 20 Countries by Population)')
    plt.xticks(positions, countries_by_pop, rotation=90)
    plt.legend()
    plt.tight_layout()
    plt.savefig('vaccination_rate_comparison.png', dpi=300)
    plt.close()
    
    # 2. Visualization of distribution network with optimized flow
    print("\nVisualization outputs saved as 'vaccination_rate_comparison.png'")
    
    return plt

# Example usage continued
def run_optimization_analysis(G, analysis_results):
    # Run the optimization model
    optimization_results = optimize_vaccine_distribution(G)
    
    # Analyze the optimization results
    opt_analysis = analyze_optimization_results(G, optimization_results)
    
    # Visualize the results
    visualize_optimization_results(G, opt_analysis)
    
    return optimization_results, opt_analysis
