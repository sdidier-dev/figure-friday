import os
import pandas as pd

if os.getenv('DASH_URL_BASE_PATHNAME', 'prod') == 'dev':
    assets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '.', 'assets'))
    dataset = f'{assets_dir}/MTA_Daily_Ridership_Data__Beginning_2020_20241009.csv'
else:
    plotly_dataset_repo = 'https://raw.githubusercontent.com/plotly/Figure-Friday/main/2024'
    dataset = plotly_dataset_repo + '/week-41/MTA_Daily_Ridership_Data__Beginning_2020_20241009.csv'

df = pd.read_csv(dataset, index_col='Date', date_format={'Date': '%m/%d/%Y'})

df.rename(columns={
    'Subways: Total Estimated Ridership': 'Subways',
    'Subways: % of Comparable Pre-Pandemic Day': 'Subways%',
    'Buses: Total Estimated Ridership': 'Buses',
    'Buses: % of Comparable Pre-Pandemic Day': 'Buses%',
    'LIRR: Total Estimated Ridership': 'LIRR',
    'LIRR: % of Comparable Pre-Pandemic Day': 'LIRR%',
    'Metro-North: Total Estimated Ridership': 'Metro-North',
    'Metro-North: % of Comparable Pre-Pandemic Day': 'Metro-North%',
    'Access-A-Ride: Total Scheduled Trips': 'Access-A-Ride',
    'Access-A-Ride: % of Comparable Pre-Pandemic Day': 'Access-A-Ride%',
    'Bridges and Tunnels: Total Traffic': 'Bridges and Tunnels',
    'Bridges and Tunnels: % of Comparable Pre-Pandemic Day': 'Bridges and Tunnels%',
    'Staten Island Railway: Total Estimated Ridership': 'Staten Island Railway',
    'Staten Island Railway: % of Comparable Pre-Pandemic Day': 'Staten Island Railway%'
}, inplace=True)

transports = [t for t in df.columns if '%' not in t and t != 'Date']

df.replace(0, 1, inplace=True)
# add comparable pre-pandemic ridership number
df = df.assign(**{t + '_pre': (df[t] * 100 / df[t + '%']) for t in transports})
# remove % col
df.drop([c for c in df.columns if '%' in c], axis="columns", inplace=True)
# add difference actual - comparable pre-pandemic ridership
df = df.assign(**{t + '_diff': (df[t] - df[t + '_pre']) for t in transports})

# little helper to convert in ms
to_ms = {
    'D': 1000 * 60 * 60 * 24,
    'W-SAT': 1000 * 60 * 60 * 24 * 7,
    'MS': 1000 * 60 * 60 * 24 * 365 / 12,
    'QS': 1000 * 60 * 60 * 24 * 365 / 4,
    '2QS': 1000 * 60 * 60 * 24 * 365 / 2,
    'YS': 1000 * 60 * 60 * 24 * 365,
}

# Map Pandas period to Plotly period, use for bar xperiod
plotly_period = {
    'YS': 'M12',
    '2QS': 'M6',
    'QS': 'M3',
    'MS': 'M1',
    'W-SAT': to_ms['W-SAT'],
    'D': to_ms['D']
}
