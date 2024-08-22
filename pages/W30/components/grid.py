import json
import os

from dash import Input, Output, callback, no_update, Patch
import dash_ag_grid as dag
import pandas as pd

df = pd.read_csv(
    # 'assets/rural-investment.csv', #for dev
    'https://raw.githubusercontent.com/plotly/Figure-Friday/main/2024/week-30/rural-investments.csv',
    usecols=[
        'State Name', 'Congressional District', 'County FIPS', 'County', 'Program Area', 'Program',
        'NAICS Industry Sector', 'Project Name', 'Project Announced Description', 'Investment Dollars',
        'Number of Investments'
    ],
    dtype={'Investment Dollars': int},
    converters={'County FIPS': lambda x: x.zfill(5)},
    thousands=","
).sort_values(['State Name', 'Congressional District', 'County'])

### Add state_GEOID, CD_GEOID and  county_GEOID used as key to link to geojsons data

# get the State FIPS from the geojson-usa-states.geojson
assets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets'))
with open(f'{assets_dir}/geojson-usa-state.geojson') as f:
    geojson = json.load(f)
states_FIPS = {feat['properties']["NAME"]: feat['properties']["GEOID"] for feat in geojson['features']}

# Add the 'state_GEOID' col in df (being the states FIPS)
df['state_GEOID'] = df.apply(lambda row: states_FIPS.get(row['State Name']), axis=1)


def get_cd_geoid(row):
    if row['Congressional District'] == 'At-Large':
        # particular case where states have only one CD (CD identified as "00" in geojson)
        return f"{row['state_GEOID']}00"
    elif row['state_GEOID'] == '72':
        # particular case of Puerto Rico which doesn't have any CD (CD identified as "98" in geojson)
        return f"{row['state_GEOID']}98"
    else:
        return f"{row['state_GEOID']}{row['Congressional District']}"


df['CD_GEOID'] = df.apply(get_cd_geoid, axis=1)
# Fill empty Congressional District with NA for the map labels
df.fillna({'Congressional District': 'NA'}, inplace=True)

# Use 'County FIPS' as county_GEOID, only rename the col
df.rename(columns={"County FIPS": "county_GEOID"}, inplace=True)

columnDefs = [
    {
        'headerName': 'Location',
        'children': [
            {'field': 'State Name', 'headerName': 'State',
             "headerClass": 'center-aligned-header', "cellClass": 'center-aligned-cell'},
            {'field': 'Congressional District', 'maxWidth': 170,
             "headerClass": 'center-aligned-header', "cellClass": 'center-aligned-cell'},
            {'field': 'County',
             "headerClass": 'center-aligned-header', "cellClass": 'center-aligned-cell'},
        ]
    },
    {
        'headerName': 'Program details',
        'children': [
            {'field': 'Program Area'},
            {'field': 'Program', 'maxWidth': 300, 'tooltipField': 'Program'},
            {'field': 'NAICS Industry Sector'},
            {'field': 'Project Name'},
            {'field': 'Project Announced Description', 'maxWidth': 1000,
             'tooltipField': 'Project Announced Description', 'flex': 1},
        ]
    },
    {
        'field': 'Investment Dollars', 'headerName': 'Investments',
        "pinned": "right", 'maxWidth': 150,
        "headerClass": 'center-aligned-header', "cellClass": 'center-aligned-cell',
        "valueFormatter": {"function": "d3.format('$,')(params.value)"}
    },
    {
        'field': 'Number of Investments',
        "pinned": "right", 'maxWidth': 150,
        "headerClass": 'center-aligned-header', "cellClass": 'center-aligned-cell',
    },
]

defaultColDef = {
    "resizable": True,
    'filter': True, "filterParams": {"buttons": ["reset"]}, "floatingFilter": True,
    "wrapHeaderText": True,
    'suppressHeaderMenuButton': True
}

dashGridOptions = {
    "headerHeight": 30,
    "floatingFiltersHeight": 30,
    'tooltipShowDelay': 1000,
}

# Dash component
aggrig_grid = dag.AgGrid(
    id="grid-data",
    rowData=df.to_dict("records"),
    columnDefs=columnDefs,
    defaultColDef=defaultColDef,
    dashGridOptions=dashGridOptions,
    columnSize="autoSize",
    style={"height": None},
    className='ag-theme-alpine flex-fill'
)


@callback(
    Output("grid-data", "dashGridOptions"),
    Input("grid-data", "virtualRowData"),
)
def row_pinning_bottom(virtual_data):
    if not virtual_data:
        return no_update
    dff = pd.DataFrame(virtual_data, columns=['Investment Dollars', 'Number of Investments'])

    totals = dff[['Investment Dollars', 'Number of Investments']].sum()

    totals_formatted = {
        "Investment Dollars": totals['Investment Dollars'],
        "Number of Investments": totals['Number of Investments'],
    }

    grid_option_patch = Patch()
    grid_option_patch["pinnedBottomRowData"] = [{"State Name": "Total", **totals_formatted}]
    return grid_option_patch
