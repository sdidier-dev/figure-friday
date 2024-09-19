import json
import os

import pandas as pd

assets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '.', 'assets'))

df = pd.read_csv(
    # f'{assets_dir}/air-pollution.csv', # for dev
    'https://raw.githubusercontent.com/plotly/Figure-Friday/main/2024/week-36/air-pollution.csv',
    index_col='Year'
)

df.drop(columns=['Singapore', 'Birmingham, UK'], inplace=True)  # remove duplicates
df.rename(columns={
    "Bangui, CAR": "Bangui, Central African Republic",
    "Brazzaville, Congo": "Brazzaville, Republic of the Congo",
    "Kinshasa, DRC": "Kinshasa, Democratic Republic of the Congo",
    "Abu Dhabi, UAE": "Abu Dhabi, United Arab Emirates",
    "Washington, D.C., USA": "Washington, D.C., United States of America",
    "Los Angeles, USA": "Los Angeles, United States of America",
    "Fairbanks, USA": "Fairbanks, United States of America",
}, inplace=True)

# Data for the map and bar plots
df_cities = df.transpose()
# add lat and lon cols
with open(f'{assets_dir}/city_loc.json') as f:
    cities_loc = json.load(f)
df_cities['lat'] = df_cities.apply(lambda row: cities_loc[row.name]['lat'], axis=1)
df_cities['lon'] = df_cities.apply(lambda row: cities_loc[row.name]['lon'], axis=1)

pollution_levels = {
    'Good': {
        'min': 0, 'max': 9, 'color': '#009600',
        'description': 'Air quality is satisfactory and poses little or no risk.'
    },
    'Moderate': {
        'min': 9.1, 'max': 35.4, 'color': '#F8D461',
        'description': 'Sensitive individuals should avoid outdoor activity as they may experience '
                       'respiratory symptoms.'
    },
    'Unhealthy for Sensitive Groups': {
        'min': 35.5, 'max': 55.4, 'color': '#FB9956',
        'description': 'General public and sensitive individuals in particular are at risk to experience irritation '
                       'and respiratory problems.'
    },
    'Unhealthy': {
        'min': 55.5, 'max': 125.4, 'color': '#F6686A',
        'description': 'Increase likelihood of adverse effects and aggravation to the heart and lungs among '
                       'general public.'
    },
    'Very Unhealthy': {
        'min': 125.5, 'max': 225.4, 'color': '#A47DB8',
        'description': 'General public will be noticeably affected. Sensitive groups should restrict '
                       'outdoor activities.'
    },
    'Hazardous': {
        'min': 225.5, 'max': float('inf'), 'color': '#4C3940',
        'description': 'General public at high risk of experiencing strong irritations and adverse health effects. '
                       'Should avoid outdoor activities.'
    },
}
