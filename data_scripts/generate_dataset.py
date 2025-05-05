import os
import sys
import pandas as pd

# Add the parent directory (project root) to the import path to find GetMarylandData
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from data_collection.get_openaq_data import GetMarylandData

# Fetch the OpenAQ API key from the environment
api_key = os.getenv('OPENAQ_API_KEY')

if api_key is None:
    raise ValueError('API key is missing! Please set the OPENAQ_API_KEY environment variable.')

# Define the year and months from which to collect data
year = '2020'
months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']

# Fetch the data for each month and save it as a csv file
for month in months:
    date_from = f'{year}-{month}-01'

    # 31-day months
    if month in ['01', '03', '05', '07', '08', '10', '12']:
        date_to = f'{year}-{month}-31'

    # 30-day months
    elif month in ['04', '06', '09', '11']:
        date_to = f'{year}-{month}-30'

    # Handle February by determining whether or not it is a leap year
    elif month == '02':
        if (int(year) % 4 == 0 and (int(year) % 100 != 0 or int(year) % 400 == 0)):
            date_to = f'{year}-{month}-29' 
        else:
            date_to = f'{year}-{month}-28'

    # Collect the data for the month
    print(f'Collecting data for month {month}')
    df = GetMarylandData(api_key, date_from, date_to, delay=60)

    # Save the data as a csv file
    output_dir = '../raw_data'
    os.makedirs(output_dir, exist_ok=True)
    output_fname = f'maryland_data_{year}_{month}.csv'
    output_path = f'{output_dir}/{output_fname}'
    df.to_csv(output_path, index=False)