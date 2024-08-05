import json

import pandas as pd


# def load_data():
df = pd.read_csv(
    'assets/rural-investments.csv',
    dtype={'Investment Dollars': int},
    converters={'County FIPS': lambda x: x.zfill(5)},
    thousands=","
)

# get the State FIPS from the geojson-usa-states.json and add it to df
with open('assets/geojson-usa-state.json') as f:
    geojson = json.load(f)
states_FIPS = {feat['properties']["NAME"]: feat['properties']["STATE"] for feat in geojson['features']}
# Add the 'State FIPS' col in df
df['State FIPS'] = df.apply(lambda row: states_FIPS.get(row['State Name'].replace(' ', '')), axis=1)
# Fill empty Congressional District with NA, some states doesn't have any CD
df.fillna({'Congressional District': 'NA'}, inplace=True)

# Load Geojsons
geojsons = {}
for area_type in ['state', 'CD', 'county']:
    with open(f'assets/geojson-usa-{area_type}.json') as f:
        geojsons[area_type] = json.load(f)

# Add id to CDs
geoID = []
for feat in geojsons['CD']['features']:
    if feat['properties']['CD'] == '00':
        cd = 'At-Large'  # particular case where states have only one CD (CD identified as "00" in geojson)
    elif feat['properties']['CD'] == '98':
        cd = 'NA'  # particular case of Puerto Rico which doesn't have any CD (CD identified as "98" in geojson)
    else:
        cd = feat['properties']['CD']
    feat['id'] = f"{feat['properties']['STATE']}-{cd}"
    geoID.append(feat['id'])

    # return df, geojsons
