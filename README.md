# COVID-19 Vaccine Distribution Optimization

A network-based optimization tool for analyzing and improving global vaccine distribution equity during pandemics.

## Overview:

This project creates a computational model to optimize global vaccine distribution using network theory and linear programming. The system analyzes country-level vaccination data, population demographics, manufacturing capabilities, and transportation networks to identify bottlenecks and determine the most equitable allocation of limited vaccine supplies.

## Features:

- **Data Acquisition**: Downloads and processes COVID-19 data from Google's COVID-19 Open Data repository
- **Network Construction**: Models vaccine distribution as a directed network with countries as nodes
- **Network Analysis**: Identifies key distribution hubs, bottlenecks, and flow capacity issues
- **Optimization Model**: Uses linear programming to maximize vaccination equity across countries
- **Visualization**: Generates network diagrams and comparative charts of optimization results

## Project Structure:

```
covid-vaccine-distribution/
├── data_acquisition.py      # Functions to download and preprocess COVID-19 data
├── network_construction.py  # Build and analyze the vaccine distribution network
├── optimization_model.py    # Linear programming model to optimize distribution
├── main.py                  # Command-line interface to run analysis components
├── requirements.txt         # Project dependencies
├── results/                 # Output directory (created at runtime)
│   ├── processed_vaccination_data.csv   # Preprocessed data by country
│   ├── network_analysis_results.json    # Network metrics and bottlenecks
│   ├── optimization_results.json        # Optimization results and equity metrics
│   ├── vaccine_distribution_network.png # Network visualization
│   └── vaccination_rate_comparison.png  # Before/after visualization
└── README.md                # Project documentation
```

## Requirements:

- Python 3.8+
- pandas
- numpy
- matplotlib
- networkx
- seaborn
- pulp (for optimization)

## Installation:

1. Clone the repository:
   ```bash
   git clone https://github.com/karthikkraj/covid-vaccine-distribution.git
   cd covid-vaccine-distribution
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage:

### Basic Usage:

Run the full analysis pipeline:

```bash
python main.py --run-all --vaccines 1000000000 --output-dir results
```

### Component-specific Usage:

Run individual components:

```bash
# Only download and prepare data
python main.py --data-only

# Only build and analyze network
python main.py --network-only

# Only run optimization with 500M vaccines
python main.py --optimize-only --vaccines 5e8
```

### Example Workflow:

1. Prepare the data:
   ```bash
   python main.py --data-only
   ```

2. Build and analyze the network:
   ```bash
   python main.py --network-only
   ```

3. Run optimization with different vaccine quantities:
   ```bash
   python main.py --optimize-only --vaccines 1e9
   python main.py --optimize-only --vaccines 2e9
   ```

4. Compare results:
   ```bash
   # Results will be in the output directory
   ls -la results/
   ```

## Command-line Arguments:

- `--run-all`: Run all analysis steps
- `--data-only`: Only load and prepare data
- `--network-only`: Only build and analyze network
- `--optimize-only`: Only run optimization
- `--vaccines`: Number of available vaccines to distribute (default: 1 billion)
- `--output-dir`: Directory to save output files (default: 'results')

## Output:

The program generates several output files in the specified directory:

- `processed_vaccination_data.csv`: Preprocessed vaccination data by country
- `network_analysis_results.json`: Network metrics and bottleneck analysis
- `optimization_results.json`: Optimization results and equity metrics
- `vaccine_distribution_network.png`: Visualization of the distribution network
- `vaccination_rate_comparison.png`: Before/after comparison of vaccination rates

## Example Analysis Results:

The optimization model identifies countries where vaccine distribution would have the greatest impact on global equity. The analysis includes:

- Vaccination rate improvements by country
- Equity impact (reduction in Gini coefficient)
- Remaining bottlenecks after optimization
- Logistics metrics for distribution

## Development:

To extend this project:
- Add new data sources in `data_acquisition.py`
- Enhance the network model in `network_construction.py`
- Improve the optimization objective in `optimization_model.py`
- Add visualization tools as needed

## License

MIT


##  Authors:
**[Karthik Raj (2022BCD0041)](https://github.com/karthikkraj)** 
**[Srivathsa K (2022BCD0020)](https://github.com/srivathsa252)** 