import pandas as pd
import numpy as np
from geopy.distance import geodesic
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

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
    idw_power : int
        Power to use for inverse distance weighting. A higher power means that
        sensors further away will be given less weight in the prediction.

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

def ParityPlot(df, pollutant, year, month, day, hour, n_sensors=4, idw_power=2):
    """
    Creates a parity plot for predicted pollutants by using the PredictPollutant function.

    Parameters
    ----------
    df : DataFrame
        Pandas DataFrame of pollution data collected from OpenAQ.
    pollutant : str
        String of the pollutant to make predictions for.
    year : int
        Year to predict pollutant concentration for using the DataFrame.
    month : int
        Month to predict pollutant concentration for using the DataFrame.
    day : int
        Day to predict pollutant concentration for using the DataFrame.
    hour : int
        Hour to predict pollutant concentration for using the DataFrame.
    n_sensors : int
        Number of nearby sensors to collect data from.
    idw_power : int
        Power to use for inverse distance weighting. A higher power means that
        sensors further away will be given less weight in the prediction.
    

    Returns
    -------
    None
        This function does not return a value. It displays a parity plot using matplotlib
        and prints evaluation metrics (MAE, RMSE, R²) to the console.

    Notes
    -----
    - It is recommended to use 2-4 sensors to make the prediction.
    - p = 2 is recommended in the idw formula, as this quadratically decreases the
      infulence of a point with distance.

    Example
    -------
    >>> ParityPlot(df, pollutant='o3', year=2020, month=1, day=1, hour=8)
    """

    # Filter the DataFrame for rows only with the specified datetime and pollutant
    filtered_df = df[
    (df['parameter'] == pollutant) &
    (df['year'] == year) &
    (df['month'] == month) &
    (df['day'] == day) &
    (df['hour'] == hour)
    ]

    print(filtered_df)
    # Create lists to store true and predicted pollutant concentration for each location
    true_vals = []
    predicted_vals = []

    # Loop through all of the rows in the filtered DataFrame
    for idx, row in filtered_df.iterrows():
        # Retrieve the latitude, longitude, and pollutant concentration of the current row
        lat = row['latitude']
        lon = row['longitude']
        true_val = row['value']
        coords = (lat, lon)

        # Create a temporary DataFrame without the current row
        df_temp = filtered_df.drop(index=idx)

        # Use inverse distance weighting interpolation to find the predicted concentration at the coordinates of the current row
        try:
            prediction = PredictPollutant(df_temp, coords, n_sensors=n_sensors, pollutant=pollutant,
                                          year=year, month=month, day=day, hour=hour, idw_power=idw_power)
            true_vals.append(true_val)
            predicted_vals.append(prediction)
        except Exception as e:
            print(f'Skipping index {idx} due to error: {e}')

    # Create a visualization of the true vs. predicted values
    plt.figure(figsize=(5, 5))
    plt.scatter(true_vals, predicted_vals, alpha=0.7, edgecolors='k')
    plt.plot([min(true_vals), max(true_vals)], [min(true_vals), max(true_vals)], 'b--', label='Perfect prediction')
    plt.xlabel(f'Actual {pollutant}')
    plt.ylabel(f'Predicted {pollutant}')
    plt.title(f'Predicted vs. Actual {pollutant}')
    plt.legend()
    plt.tight_layout()
    plt.show()

    # Compute metrics
    mae = mean_absolute_error(true_vals, predicted_vals)
    rmse = np.sqrt(mean_squared_error(true_vals, predicted_vals))
    r2 = r2_score(true_vals, predicted_vals)

    # Print results
    print(f'Mean Absolute Error (MAE): {mae:.4f}')
    print(f'Root Mean Squared Error (RMSE): {rmse:.4f}')
    print(f'R² Score: {r2:.4f}')