import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import seaborn as sns
from datetime import datetime, timedelta

# Set visualization style
plt.style.use('ggplot')  # Or 'classic', 'fivethirtyeight', etc.
sns.set_palette("deep")

# Define the URLs for Google COVID-19 Open Data
BASE_URL = "https://storage.googleapis.com/covid19-open-data/v3/"
EPIDEMIOLOGY_URL = f"{BASE_URL}epidemiology.csv"
DEMOGRAPHICS_URL = f"{BASE_URL}demographics.csv"
MOBILITY_URL = f"{BASE_URL}mobility.csv"
GOVERNMENT_RESPONSE_URL = f"{BASE_URL}oxford-government-response.csv"
VACCINES_URL = f"{BASE_URL}vaccinations.csv"
INDEX_URL = f"{BASE_URL}index.csv"

# Load the data
def load_covid_data():
    print("Loading COVID-19 data...")
    
    # Download index file to get location information
    index_df = pd.read_csv(INDEX_URL)
    
    # Download vaccination data
    vaccines_df = pd.read_csv(VACCINES_URL)
    
    # Download demographic data for population density
    demographics_df = pd.read_csv(DEMOGRAPHICS_URL)
    
    # Download mobility data for transportation network proxy
    mobility_df = pd.read_csv(MOBILITY_URL)
    
    # Download government response data
    gov_response_df = pd.read_csv(GOVERNMENT_RESPONSE_URL)
    
    print("Data loaded successfully!")
    
    return {
        'index': index_df,
        'vaccines': vaccines_df,
        'demographics': demographics_df,
        'mobility': mobility_df,
        'gov_response': gov_response_df
    }

# Process the data for network analysis
def prepare_data_for_network_analysis(data_dict):
    print("Preparing data for network analysis...")
    
    # Join location information with vaccination data
    index_df = data_dict['index']
    vaccines_df = data_dict['vaccines']
    demographics_df = data_dict['demographics']
    
    # Focus on country-level data for initial analysis
    country_index = index_df[index_df['aggregation_level'] == 0]
    
    # Merge vaccination data with country information
    vax_with_location = pd.merge(
        vaccines_df,
        country_index[['key', 'country_name', 'country_code']],
        on='key',
        how='inner'
    )
    
    # Get the latest vaccination data for each country
    latest_date = vax_with_location['date'].max()
    latest_vax_data = vax_with_location[vax_with_location['date'] == latest_date]
    
    # Merge with demographic data to get population information
    demographics_country = demographics_df[demographics_df['key'].isin(country_index['key'])]
    
    vax_demo_data = pd.merge(
        latest_vax_data,
        demographics_country[['key', 'population', 'population_density']],
        on='key',
        how='left'
    )
    
    # Calculate vaccination coverage and create network nodes data
    vax_demo_data['total_vaccinations_per_hundred'] = vax_demo_data['total_vaccinations'] / vax_demo_data['population'] * 100
    vax_demo_data['people_vaccinated_per_hundred'] = vax_demo_data['people_vaccinated'] / vax_demo_data['population'] * 100
    vax_demo_data['people_fully_vaccinated_per_hundred'] = vax_demo_data['people_fully_vaccinated'] / vax_demo_data['population'] * 100
    
    # Clean up data - remove rows with missing crucial data
    network_nodes = vax_demo_data.dropna(subset=['population', 'people_vaccinated'])
    
    print(f"Data prepared. We have vaccination data for {len(network_nodes)} countries.")
    
    return network_nodes

# Example usage
if __name__ == "__main__":
    covid_data = load_covid_data()
    network_nodes = prepare_data_for_network_analysis(covid_data)
    
    print("\nSample of the prepared data:")
    print(network_nodes[['country_name', 'population', 'people_vaccinated_per_hundred']].head())
