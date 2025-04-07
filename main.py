from data_acquisition import load_covid_data, prepare_data_for_network_analysis
from network_construction import create_vaccine_distribution_network, analyze_network, visualize_network
from optimization_model import optimize_vaccine_distribution, analyze_optimization_results, visualize_optimization_results

import argparse
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import json
import os
from datetime import datetime

# Import functions from other modules
# In a real project, these would be proper imports from separate files
from data_acquisition import load_covid_data, prepare_data_for_network_analysis
from network_construction import create_vaccine_distribution_network, analyze_network, visualize_network
from optimization_model import optimize_vaccine_distribution, analyze_optimization_results, visualize_optimization_results

def create_and_analyze_network(network_nodes, mobility_data):
    """Helper function to create and analyze network"""
    G = create_vaccine_distribution_network(network_nodes, mobility_data)
    analysis_results = analyze_network(G)
    visualize_network(G, analysis_results, args.output_dir)
    return G, analysis_results

def run_optimization_analysis(G, network_analysis):
    """Helper function to run optimization analysis"""
    optimization_results = optimize_vaccine_distribution(G, args.vaccines)
    opt_analysis = analyze_optimization_results(G, optimization_results)
    visualize_optimization_results(opt_analysis, args.output_dir)
    return optimization_results, opt_analysis

def main():
    parser = argparse.ArgumentParser(description='COVID-19 Vaccine Distribution Network Analysis')
    parser.add_argument('--run-all', action='store_true', help='Run all analysis steps')
    parser.add_argument('--data-only', action='store_true', help='Only load and prepare data')
    parser.add_argument('--network-only', action='store_true', help='Only build and analyze network')
    parser.add_argument('--optimize-only', action='store_true', help='Only run optimization')
    parser.add_argument('--vaccines', type=float, default=1e9, help='Number of available vaccines to distribute')
    parser.add_argument('--output-dir', type=str, default='results', help='Directory to save output files')
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    
    # Run based on arguments
    try:
        # Step 1: Data Acquisition and Preparation
        if args.run_all or args.data_only or args.network_only or args.optimize_only:
            print("\n" + "="*80)
            print("STEP 1: DATA ACQUISITION AND PREPARATION")
            print("="*80)
            covid_data = load_covid_data()
            network_nodes = prepare_data_for_network_analysis(covid_data)
            
            # Save preprocessed data
            network_nodes.to_csv(f"{args.output_dir}/processed_vaccination_data.csv", index=False)
            print(f"Preprocessed data saved to {args.output_dir}/processed_vaccination_data.csv")
        
        # Stop here if data-only flag is set
        if args.data_only:
            print("\nData processing completed. Exiting as requested.")
            return
        
        # Step 2: Network Construction and Analysis
        if args.run_all or args.network_only or args.optimize_only:
            print("\n" + "="*80)
            print("STEP 2: NETWORK CONSTRUCTION AND ANALYSIS")
            print("="*80)
            G, analysis_results = create_and_analyze_network(network_nodes, covid_data['mobility'])
            
            # Save network analysis results
            with open(f"{args.output_dir}/network_analysis_results.json", 'w') as f:
                # Convert to serializable format
                serializable_results = {
                    'degree_centrality': {k: float(v) for k, v in analysis_results['degree_centrality'].items()},
                    'betweenness_centrality': {k: float(v) for k, v in analysis_results['betweenness_centrality'].items()},
                    'bottlenecks': [[b[0], float(b[1]), float(b[2])] for b in analysis_results['bottlenecks']],
                    'manufacturers': analysis_results['manufacturers']
                }
                json.dump(serializable_results, f, indent=2)
            
            print(f"Network analysis results saved to {args.output_dir}/network_analysis_results.json")
        
        # Stop here if network-only flag is set
        if args.network_only:
            print("\nNetwork analysis completed. Exiting as requested.")
            return
        
        # Step 3: Optimization
        if args.run_all or args.optimize_only:
            print("\n" + "="*80)
            print(f"STEP 3: OPTIMIZATION OF VACCINE DISTRIBUTION (Available vaccines: {args.vaccines:,.0f})")
            print("="*80)
            optimization_results, opt_analysis = run_optimization_analysis(G, analysis_results)
            
            # Save optimization results
            with open(f"{args.output_dir}/optimization_results.json", 'w') as f:
                # Convert to serializable format
                serializable_results = {
                    'status': optimization_results['status'],
                    'objective_value': float(optimization_results['objective_value']),
                    'total_allocated': float(optimization_results['total_allocated']),
                    'improvement_by_country': {k: float(v) for k, v in optimization_results['improvement_by_country'].items()},
                    'equity_metrics': {
                        'before_gini': float(opt_analysis['before_gini']),
                        'after_gini': float(opt_analysis['after_gini']),
                        'improvement_pct': float((opt_analysis['before_gini'] - opt_analysis['after_gini']) / 
                                              opt_analysis['before_gini'] * 100)
                    }
                }
                json.dump(serializable_results, f, indent=2)
            
            print(f"Optimization results saved to {args.output_dir}/optimization_results.json")
        
        print("\n" + "="*80)
        print("ANALYSIS COMPLETE")
        print("="*80)
        print(f"All results saved to {args.output_dir}/ directory")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    main()
