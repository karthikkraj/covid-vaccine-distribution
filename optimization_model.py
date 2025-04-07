import numpy as np
import pandas as pd
from scipy.optimize import linprog
import matplotlib.pyplot as plt

def optimize_vaccine_distribution(G, available_vaccines):
    """Optimize vaccine distribution accounting for booster needs"""
    nodes = list(G.nodes())
    n = len(nodes)
    
    # Calculate booster need scores (higher for countries with older vaccinations)
    scores = []
    for node in nodes:
        last_vax_date = pd.to_datetime(G.nodes[node]['last_vaccination_date'])
        days_since_vax = (pd.Timestamp.now() - last_vax_date).days
        coverage_gap = max(0, 1 - (G.nodes[node]['vaccination_rate'] / 100))
        score = 0.7 * days_since_vax/180 + 0.3 * coverage_gap
        scores.append(score)
    
    # Normalize scores
    scores = np.array(scores)
    if scores.sum() > 0:
        scores = scores / scores.sum()
    
    # Create objective function (prioritize high-need countries)
    c = -scores  # Minimize negative need
    
    # Constraints
    A_ub = np.ones((1, n))  # Total vaccines constraint
    b_ub = [available_vaccines]
    
    # Bounds (minimum 0, maximum proportional to population)
    bounds = [(0, G.nodes[node]['population'] * 0.1) for node in nodes]
    
    # Solve optimization problem
    result = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')
    
    # Process results
    allocation = {nodes[i]: result.x[i] for i in range(n)}
    
    return {
        'status': result.message,
        'objective_value': result.fun,
        'allocation': allocation,
        'total_allocated': sum(result.x)
    }

def analyze_optimization_results(G, results):
    """Analyze the optimization results"""
    before_rates = [G.nodes[node]['vaccination_rate'] for node in G.nodes()]
    
    after_rates = []
    for node in G.nodes():
        new_vaccinations = results['allocation'][node]
        population = G.nodes[node]['population']
        current_rate = G.nodes[node]['vaccination_rate']
        new_rate = current_rate + (new_vaccinations / population * 100)
        after_rates.append(new_rate)
    
    return {
        'before_gini': calculate_gini(before_rates),
        'after_gini': calculate_gini(after_rates),
        'before_rates': before_rates,
        'after_rates': after_rates
    }

def calculate_gini(array):
    """Calculate Gini coefficient as measure of inequality"""
    array = np.array(array)
    array = array.flatten()
    if np.amin(array) < 0:
        array -= np.amin(array)
    array += 0.0000001
    array = np.sort(array)
    index = np.arange(1, array.shape[0] + 1)
    n = array.shape[0]
    return ((np.sum((2 * index - n - 1) * array)) / (n * np.sum(array)))

def visualize_optimization_results(analysis_results, output_dir):
    """Create visualizations of optimization results"""
    try:
        plt.figure(figsize=(12, 6))
        
        # Only plot if we have valid data
        if len(analysis_results['before_rates']) > 0 and len(analysis_results['after_rates']) > 0:
            plt.subplot(1, 2, 1)
            plt.hist(analysis_results['before_rates'], bins=20, alpha=0.5, label='Before')
            plt.hist(analysis_results['after_rates'], bins=20, alpha=0.5, label='After')
            plt.title('Distribution of Vaccination Rates')
            plt.legend()
            
            plt.subplot(1, 2, 2)
            labels = ['Before', 'After']
            values = [analysis_results['before_gini'], analysis_results['after_gini']]
            plt.bar(labels, values)
            plt.title('Gini Coefficient (Inequality Measure)')
            
            plt.tight_layout()
            plt.savefig(f"{output_dir}/optimization_results.png")
            plt.close()
    except Exception as e:
        print(f"Visualization error: {str(e)}")
