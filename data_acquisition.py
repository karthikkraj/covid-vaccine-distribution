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
    
    # Configure SSL context to handle certificate verification
    import ssl
    ssl._create_default_https_context = ssl._create_unverified_context
    
    try:
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
        
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        raise
    

# Process the data for network analysis
def prepare_data_for_network_analysis(data_dict):
    print("Preparing data for network analysis...")
    
    # Join location information with vaccination data
    index_df = data_dict['index']
    vaccines_df = data_dict['vaccines']
    demographics_df = data_dict['demographics']
    
    # Focus on specific countries of interest (30 countries total)
    target_countries = ['US', 'AU', 'IN', 'BR', 'GB', 'FR', 'DE', 'IT', 'ES', 'CA', 
                       'MX', 'JP', 'KR', 'CN', 'ZA', 'NG', 'EG', 'PK', 'RU', 'ID', 
                       'TR', 'VN', 'IR', 'TH', 'PH', 'AR', 'CO', 'ET', 'KE']
    print(f"Total countries in index: {len(index_df)}")
    print(f"Countries with aggregation_level 0: {len(index_df[index_df['aggregation_level'] == 0])}")
    
    country_index = index_df[(index_df['aggregation_level'] == 0) & 
                           (index_df['country_code'].isin(target_countries))]
    print(f"Filtered countries: {country_index['country_code'].tolist()}")
    
    # Merge vaccination data with country information
    print(f"\nVaccine data shape before merge: {vaccines_df.shape}")
    print(f"Country index shape: {country_index.shape}")
    
    vax_with_location = pd.merge(
        vaccines_df,
        country_index[['location_key', 'country_name', 'country_code']],
        on='location_key',
        how='inner'
    )
    print(f"After merge shape: {vax_with_location.shape}")
    print(f"Unique countries after merge: {vax_with_location['country_code'].nunique()}")
    
    # Get most recent vaccination data for each country (may be different dates)
    vax_with_location['date'] = pd.to_datetime(vax_with_location['date'])
    latest_vax_data = vax_with_location.loc[vax_with_location.groupby('country_code')['date'].idxmax()]
    print(f"\nCountries with available data: {latest_vax_data['country_code'].unique()}")
    
    # Merge with demographic data to get population information
    demographics_country = demographics_df[demographics_df['location_key'].isin(country_index['location_key'])]
    
    vax_demo_data = pd.merge(
        latest_vax_data,
        demographics_country[['location_key', 'population', 'population_density']],
        on='location_key',
        how='left'
    )
    
    # Calculate vaccination coverage using current column names
    if 'cumulative_persons_vaccinated' in vax_demo_data.columns:
        vax_demo_data['people_vaccinated_per_hundred'] = vax_demo_data['cumulative_persons_vaccinated'] / vax_demo_data['population'] * 100
    if 'cumulative_persons_fully_vaccinated' in vax_demo_data.columns:
        vax_demo_data['people_fully_vaccinated_per_hundred'] = vax_demo_data['cumulative_persons_fully_vaccinated'] / vax_demo_data['population'] * 100
    if 'cumulative_vaccine_doses_administered' in vax_demo_data.columns:
        vax_demo_data['total_vaccinations_per_hundred'] = vax_demo_data['cumulative_vaccine_doses_administered'] / vax_demo_data['population'] * 100
    
    # Check if we have any vaccination data
    if not any(col.endswith('_per_hundred') for col in vax_demo_data.columns):
        raise ValueError("No valid vaccination data columns found in the dataset")
    
    # Clean up data - remove rows with missing crucial data
    network_nodes = vax_demo_data.dropna(subset=['population', 'people_vaccinated_per_hundred'])
    
    print(f"Data prepared. We have vaccination data for {len(network_nodes)} countries.")
    
    return network_nodes

# Example usage
if __name__ == "__main__":
    covid_data = load_covid_data()
    network_nodes = prepare_data_for_network_analysis(covid_data)
    
    print("\nSample of the prepared data:")
    print(network_nodes[['country_name', 'population', 'people_vaccinated_per_hundred']].head())

    