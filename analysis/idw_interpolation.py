import pandas as pd
from geopy.distance import geodesic

def PredictPollutant(df, target_location, n_sensors, pollutant, year, month, day, hour, idw_power=2):
    """
    Uses inverse distance weighting to predict a pollutant concentration at a given
    location.

    Parameters
    ----------
    df : DataFrame
        Pandas DataFrame of pollution data collected from OpenAQ.
    target_location : tuple
        Target location to predict pollutant concentration in (latitude, longitude).
    n_sensors : int
        Number of nearby sensors to collect data from.
    pollutant : str
        Pollutant to be predicted.
    year : int
        Year to predict pollutant concentration for using the DataFrame.
    month : int
        Month to predict pollutant concentration for using the DataFrame.
    day : int
        Day to predict pollutant concentration for using the DataFrame.
    hour : int
        Hour to predict pollutant concentration for using the DataFrame.

    Returns
    -------
    estimate
        An estimate of the specified pollutant concentration at the specified
        location and time.

    Notes
    -----
    - It is recommended to use 2-4 sensors to make the prediction.
    - p = 2 is recommended in the idw formula, as this quadratically decreases the
      infulence of a point with distance.

    Example
    -------
    >>> df = pd.read_csv('maryland_data_january_2020.csv')
    >>> target_location = (38.6, -77.1)
    >>> pred = PredictPollutant(df, target_location, n_sensors=4, pollutant='pm25', year=2020, month=1, day=1, hour=8)
    >>> print(pred)
    3.4112498372220905
    """

    # Filter the DataFrame to find rows that measured the specified pollutant at the specified time
    filtered_df = df[
        (df['parameter'] == pollutant) &
        (df['year'] == year) &
        (df['month'] == month) &
        (df['day'] == day) &
        (df['hour'] == hour)
    ]

    target_df = filtered_df.copy()

    # Compute distances to target location and add them to the DataFrame
    def compute_distance(row):
        return geodesic(target_location, (row['latitude'], row['longitude'])).km
    
    target_df['distance_km'] = target_df.apply(compute_distance, axis=1)

    # Get the n nearest sensors
    nearest = target_df.nsmallest(n_sensors, 'distance_km')

    # Perform inverse distance weighting (IDW) interpolation to get an estimated value
    def idw_prediction(df, value_col='value', dist_col='distance_km', power=idw_power):
        weights = 1 / (df[dist_col] ** power)
        weighted_values = df[value_col] * weights
        return weighted_values.sum() / weights.sum()
    
    estimate = idw_prediction(nearest)
    return estimate