from meteostat import Point, Hourly
import pandas as pd
from datetime import timedelta

# Read-in the 2020 data as a csv file
df = pd.read_csv('maryland_all_data_2020.csv')

# Create a datetime column in the DataFrame
df['datetime'] = pd.to_datetime(df[['year', 'month', 'day', 'hour']])

# Prepare new columns for weather data
weather_columns = ['temp', 'dwpt', 'rhum', 'prcp', 'snow', 'wdir', 'wspd', 'wpgt', 'pres', 'tsun', 'coco']
for col in weather_columns:
    df[col] = None  # Fill with NaNs initially

# Loop through every row in the DataFrame and get the weather data for it
for idx, row in df.iterrows():
    lat = row['latitude']
    lon = row['longitude']
    dt = row['datetime']

    # Define the location
    location = Point(lat, lon)

    # Get data for the location
    weather = Hourly(location, dt, dt + timedelta(hours=1)).fetch()

    if not weather.empty:
        for col in weather_columns:
            df.at[idx, col] = weather.iloc[0].get(col, None)

    print(f'Iteration {idx} complete')

# Save a new csv
df.to_csv('maryland_with_weather.csv', index=False)

# Remove the three columns that don't have any data and rename the new columns with units included
df.drop(columns=['snow', 'wpgt', 'tsun'], inplace=True)
unit_map = {
    'temp': 'temp (°C)',
    'dwpt': 'dew point (°C)',
    'rhum': 'relative humidity (%)',
    'prcp': 'precipitation (mm)',
    'wdir': 'wind direction (°)',
    'wspd': 'wind speed (km/h)',
    'pres': 'pressure (hPa)',
    'coco': 'weather condition code'
}

df.rename(columns=unit_map, inplace=True)

# Save the new updated DataFrame
df.to_csv('maryland_2020_with_weather.csv', index=False)