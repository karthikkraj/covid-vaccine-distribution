# Covid-19 Vaccine Distribution Network Optimizer

A robust system for equitable vaccine allocation using network analysis and optimization

## Key Features

- **Data Processing**:
  - Handles missing vaccination data with fallback values
  - Processes country population and vaccination metrics
  - Validates network node attributes

- **Network Analysis**:
  - Hub-and-spoke model with 4 manufacturers and 27 countries
  - Degree/betweenness centrality calculations
  - Bottleneck detection

- **Optimization**:
  - Need-based scoring (vaccination rate + recency)
  - Linear programming allocation
  - 26% improvement in equity (Gini coefficient reduction)

## Project Structure

```
NSA/
├── data_acquisition.py       # Data loading and preprocessing
├── network_construction.py   # Network modeling and analysis  
├── optimization_model.py     # Allocation optimization
├── main.py                   # Pipeline controller
├── requirements.txt          # Dependencies
├── results/                  # Output directory
│   ├── enhanced_network.png      # Network visualization
│   ├── optimization_results.json # Allocation details
│   ├── optimization_results.png  # Equity comparison
│   └── processed_vaccination_data.csv
└── README.md                 # This documentation
```

## Installation

```bash
git clone [repository_url]
cd NSA
pip install -r requirements.txt
```

## Usage

Run full pipeline:
```bash
python main.py --run-all --output-dir results
```

Component options:
- `--data-only`: Process data
- `--network-only`: Build network
- `--optimize-only`: Run optimization
- `--vaccines`: Set available doses (default: 1B)

## Results

Sample optimization output (1B doses):
```json
{
  "total_allocated": 1000000000,
  "equity_metrics": {
    "before_gini": 0.42,
    "after_gini": 0.31
  }
}
```

Visualizations include:
- Network diagram showing manufacturer-country connections
- Before/after vaccination rate distributions
- Allocation heatmaps

## Technical Details

- **Languages**: Python 3.8+
- **Libraries**:
  - NetworkX for graph analysis
  - PuLP for optimization  
  - Pandas for data processing
  - Matplotlib for visualization

## Authors

- [Karthik Raj(2022BCD0041)](https://github.com/karthikkraj)
- [Srivathsa K(2022BCD0020)](https://github.com/srivathsa252)

## License

This project is licensed under the [MIT License](LICENSE).
