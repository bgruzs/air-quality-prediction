import time
import requests
import pandas as pd
import numpy as np
from datetime import datetime

def GetHourlyAverages(latitude, longitude, api_key, radius, limit):
    """
    Retrieves the hourly average of air sensor data for sensors in a given
    radius around a specified location.

    Parameters
    ----------
    - Latitude (float): Latitude of the target location.
    - Longitude (float): Longitude of the target location.
    - api_key (str): API key to authenticate with the OpenAQ API.
    - radius (int): Search radius for sensors (meters) around the given location.
    - limit (int): Maximum number of locations to retrieve.

    Returns
    -------
    df (Pandas DataFrame): A DataFrame containing average pollutant concentrations,
        including location name, latitude, longitude, pollutant name, pollutant
        measurement, units of measurement, and hour of day. Some results may not be
        pollutants, but rather other quantities measured by the sensors (temperature,
        humidity, etc.)

    Example
    -------
    >>> df = GetHourlyAverages(39.1626, -76.6247, api_key, radius=25000, limit=10)
    >>> print(df.head)
        location_name   latitude   longitude  parameter  value  unit  hour
    0   Glen Burnie      39.1800    -76.6100     o3      0.032   ppm    0
    1   Glen Burnie      39.1800    -76.6100     o3      0.028   ppm    1
    ...
    """

    # Set the required HTTP headers, create a list to store measurements
    headers = {'X-API-KEY': api_key}
    all_data = []

    # Step 1: Find monitoring stations neat the given coordinates
    locations_url = 'https://api.openaq.org/v3/locations'
    locations_params = {
        'coordinates':f'{latitude},{longitude}',
        'radius': radius,
        'limit': limit
    }

    response = requests.get(locations_url, headers=headers, params=locations_params)
    if response.status_code != 200:
        print(f'Error fetching locations {response.status_code}')
        print(response.text)
        exit()

    locations = response.json().get('results', [])

    # Step 2: For each locations, get the associated sensors
    for location in locations:
        location_id = location['id']
        location_name = location.get('name', f'Location {location_id}')
        location_lat = location.get('coordinates', {}).get('latitude', None)
        location_lon = location.get('coordinates', {}).get('longitude', None)
        print(f'\n📍 Location found: {location_name}')

        sensors_url = f'https://api.openaq.org/v3/locations/{location_id}/sensors'
        sensors_response = requests.get(sensors_url, headers=headers)
        sensors = sensors_response.json().get('results', [])

        if not sensors:
            print('  No sensors found.')
            continue

        # Step 3: Get the measurement data from the sensors
        for sensor in sensors:
            sensor_id = sensor['id']
            measurements_url = f'https://api.openaq.org/v3/sensors/{sensor_id}/hours/hourofday'
            measurements_params = {
                'date_from': '2000-01-01',
                'date_to': '2025-01-01'
            }

            measurements_response = requests.get(measurements_url, headers=headers, params=measurements_params)
            if measurements_response.status_code != 200:
                print(f"  Error fetching measurements for sensor {sensor_id}")
                continue

            measurements = measurements_response.json().get("results", [])
            if not measurements:
                print(f"  No recent measurements for sensor {sensor_id}")
                continue

            for measurement in measurements:
                param_info = measurement.get("parameter", {})

                # Use 'displayName' if available, else fall back to 'name' or 'id'
                parameter = (
                    param_info.get("displayName")
                    or param_info.get("name")
                    or param_info.get("id")
                    or "Unknown"
                )

                unit = param_info.get('units', '')
                value = measurement.get('value', 'N/A')

                # Get the hour of the measurements from the period
                period = measurement.get('period', {})
                data_hour = period.get('label', 'N/A')

                # Add the data to the list
                all_data.append({
                    'location_name': location_name,
                    'latitude': location_lat,
                    'longitude': location_lon,
                    'parameter': parameter,
                    'value': value,
                    'unit': unit,
                    'hour': data_hour
                })

    df = pd.DataFrame(all_data)

    return df

def GetHourlyData(latitude, longitude, api_key, date_from, date_to, radius, limit):
    """
    Fetches hourly environmental sensor data from OpenAQ for sensors within a specified
    radius of a given geographic coordinate.

    Parameters
    ----------
    latitude : float
        Latitude of the target location.
    longitude : float
        Longitude of the target location.
    api_key : str
        API key to authenticate with the OpenAQ API.
    date_from : str
        Start date for data retrieval in 'YYYY-MM-DD' format.
    date_to : str
        End date for data retrieval in 'YYYY-MM-DD' format.
    radius : int
        Search radius (in meters) for nearby sensors.
    limit : int
        Maximum number of monitor locations to retrieve.

    Returns
    -------
    pandas.DataFrame
        A DataFrame containing hourly pollutant concentrations (or other measured 
        quantities) at each sensor location. Includes metadata such as location name, 
        geographic coordinates, parameter name, measured value and units, as well as 
        the year, month, day, and hour of each measurement.

    Notes
    -----
    - If no data is available for the specified timeframe or sensors, those sensors 
      will be skipped.
    - Data may include parameters beyond air pollutants (e.g., temperature, humidity).

    Example
    -------
    >>> df = GetHourlyData(39.0553, -76.8783, api_key, '2020-01-01', '2020-01-02', 25000, 1)
    >>> print(df.head())
          location_name   latitude   longitude  parameter  value  unit  year  month  day  hour
    0    HU-Beltsville   39.055302  -76.878304     o3      0.032   ppm   2020     1     1     5
    1    HU-Beltsville   39.055302  -76.878304     o3      0.033   ppm   2020     1     1     6
    """

    # Set the required HTTP headers, create a list to store measurements
    headers = {'X-API-KEY': api_key}
    all_data = []

    # Step 1: Find monitoring stations neat the given coordinates
    locations_url = 'https://api.openaq.org/v3/locations'
    locations_params = {
        'coordinates':f'{latitude},{longitude}',
        'radius': radius,
        'limit': limit
    }

    response = requests.get(locations_url, headers=headers, params=locations_params)
    if response.status_code != 200:
        print(f'Error fetching locations {response.status_code}')
        print(response.text)
        exit()

    locations = response.json().get('results', [])

    # Step 2: For each locations, get the associated sensors
    for location in locations:
        location_id = location['id']
        location_name = location.get('name', f'Location {location_id}')
        location_lat = location.get('coordinates', {}).get('latitude', None)
        location_lon = location.get('coordinates', {}).get('longitude', None)
        print(f'\n📍 Location found: {location_name}')

        sensors_url = f'https://api.openaq.org/v3/locations/{location_id}/sensors'
        sensors_response = requests.get(sensors_url, headers=headers)
        sensors = sensors_response.json().get('results', [])

        if not sensors:
            print('  No sensors found.')
            continue

        # Step 3: Get hourly data per sensor with pagination
        for sensor in sensors:
            sensor_id = sensor['id']
            measurements_url = f'https://api.openaq.org/v3/sensors/{sensor_id}/hours'
            page = 1
            limit_per_page = 1000
            measurements_params = {
                'datetime_from': date_from,
                'datetime_to': date_to,
                'sort': 'asc',
                'limit': limit_per_page
            }

            measurements_response = requests.get(measurements_url, headers=headers, params=measurements_params)
            if measurements_response.status_code != 200:
                print(f"  Error fetching measurements for sensor {sensor_id}")
                continue

            measurements = measurements_response.json().get("results", [])
            if not measurements:
                print(f"  No recent measurements for sensor {sensor_id}")
                continue

            # Step 4: Extract data from the measurements
            for measurement in measurements:
                param_info = measurement.get("parameter", {})
                #print(measurement)  # Remove once done

                # Use 'displayName' if available, else fall back to 'name' or 'id'
                parameter = (
                    param_info.get("displayName")
                    or param_info.get("name")
                    or param_info.get("id")
                    or "Unknown"
                )

                unit = param_info.get('units', '')
                value = measurement.get('value', 'N/A')

                # Get the year, month, day, and hour of the measurement from the period
                period = measurement.get('period', {})
                datetime_from = period.get('datetimeFrom', {}).get('utc', '')

                # If the datetimeFrom value exists, process it
                if datetime_from:
                    # Convert the string to a datetime object
                    dt = datetime.strptime(datetime_from, '%Y-%m-%dT%H:%M:%SZ')
                    data_year = dt.year
                    data_month = dt.month
                    data_day = dt.day
                    data_hour = dt.hour

                # Add the data to the list
                all_data.append({
                    'location_name': location_name,
                    'latitude': location_lat,
                    'longitude': location_lon,
                    'parameter': parameter,
                    'value': value,
                    'unit': unit,
                    'year': data_year,
                    'month': data_month,
                    'day': data_day,
                    'hour': data_hour
                })

    df = pd.DataFrame(all_data)

    return df

def GetMarylandData(api_key, date_from, date_to, delay=60):
    """
    Fetches hourly environmental sensor data from OpenAQ for sensors within the maximum
    and minimum coordinates for Maryland. Some sensors outside of maryland may lie in
    this range, and therefore also have their data collected.

    Parameters
    ----------
    api_key : str
        API key to authenticate with the OpenAQ API.
    date_from : str
        Start date for data retrieval in 'YYYY-MM-DD' format.
    date_to : str
        End date for data retrieval in 'YYYY-MM-DD' format.
    delay : int    
        Time delay between each coordinate search.
    
    Returns
    -------
    pandas.DataFrame
        A DataFrame containing hourly pollutant concentrations (or other measured 
        quantities) at each sensor location. Includes metadata such as location name, 
        geographic coordinates, parameter name, measured value and units, as well as 
        the year, month, day, and hour of each measurement.

    Notes
    -----
    - If no data is available for the specified timeframe or sensors, those sensors 
      will be skipped.
    - Data may include parameters beyond air pollutants (e.g., temperature, humidity).
    - Due to API data retrieval constraints, this function will run for several hours.

    Example
    -------
    >>> df = GetMarylandData(api_key, date_from='2020-01-01', date_to='2020-01-31', delay=60)
    >>> print(df.head())
          location_name   latitude   longitude  parameter  value  unit  year  month  day  hour
    0    HU-Beltsville   39.055302  -76.878304     o3      0.032   ppm   2020     1     1     5
    1    HU-Beltsville   39.055302  -76.878304     o3      0.033   ppm   2020     1     1     6
    """

    # Set the longitude and latitude bounds of MD and create a coordinate grid
    lat_range = np.arange(37.9, 39.76, 0.25)   # South to North
    lon_range = np.arange(-79.5, -74.9, 0.25)  # West to East
    coordinate_pairs = [(lat, lon) for lat in lat_range for lon in lon_range]
    coordinate_total = len(coordinate_pairs)

    # Create a Maryland DataFrame to hold all of the data
    md_df = pd.DataFrame()

    # Collect data for Maryland
    for i, (lat, lon) in enumerate(coordinate_pairs, start=1):
        print(f'Checking for data near ({lat}, {lon})')
        try:
            df = GetHourlyData(lat, lon, api_key, date_from, date_to, radius=25000, limit=100)
            if not df.empty:
                md_df = pd.concat([md_df, df], ignore_index=True)
        except Exception as e:
            print(f'⚠️ Skipping ({lat}, {lon}) due to error: {e}')

        print(f'Current number of DataFrame rows: {md_df.shape[0]}')
        print(f'{i}/{coordinate_total} iterations complete, sleeping for {delay} seconds...')
        time.sleep(delay)

    # Remove any duplicates that are present
    md_df.drop_duplicates(
        subset=['latitude', 'longitude', 'parameter', 'value', 'unit', 'year', 'month', 'day', 'hour'],
        keep="first",
        inplace=True
    )

    return md_df
