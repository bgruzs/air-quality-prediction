## air-quality-prediction
This project collects and processes **hour-by-hour air quality data** using the [OpenAQ API](https://docs.openaq.org/) to make air quality predictions at locations where air quality monitoring sites are not present.

### Requirements
---
- [Python](https://www.python.org/)
- [Pandas](https://pandas.pydata.org/)
- [Numpy](https://numpy.org/)
- [Matplotlib](https://matplotlib.org/)
- [Scikit-learn](https://scikit-learn.org/stable/)
- [Requests](https://pypi.org/project/requests/)
- [Geopy](https://geopy.readthedocs.io/en/stable/#)
- [Meteostat](https://dev.meteostat.net/)

### Directory Structure
---
The directories and files in this repository are organized as follows:

- `/analysis`: Contains code for analysis of the collected data.
    - `idw_interpolation.py`: Contains one function used to implement inverse distance weighting (IDW) interpolation.

- `/data_collection`: Contains code for collecting data using the [OpenAQ API](https://docs.openaq.org/).
    - `get_openaq_data.py`: Includes three functions used to collect pollutant data.

- `/data_scripts`: Contains code that uses functions from `/data_collection` to acquire data.
    - `add_weather_data.py`: Script used to add weather data to existing pollution data.
    - `generate_dataset.py`: Script used to acquire a year of pollutant data for the Maryland area.

- `/notebooks`: Contains Jupyter notebooks used to analyze and make predictions from raw data.
    - `interpolation.ipynb`: Jupyter notebook used to implement IDW interpolation.

- `/raw_data`: Contains the raw data collected from the scripts in `/data_scripts`.
    - `maryland_2020_with_weather.csv`: CSV file containing pollutant and weather data for all of 2020.
    - `maryland_all_data_2020.csv`: CSV file containing all of the Maryland area pollutant data for 2020.
    - `maryland_data_2020_*`: CSV files containing Maryland area pollutant data for each month in 2020.