import json
from io import StringIO
from pprint import pprint

from dash import Dash, dcc, html, Input, Output, State, callback, Patch, no_update
import dash_bootstrap_components as dbc
import dash_ag_grid as dag

import plotly.express as px
import plotly.graph_objects as go
from dash_bootstrap_templates import load_figure_template

import pandas as pd
import numpy as np
from components import graph_invest_distrib, graph_map, graph_program_details

from assets.data import df, geojsons

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
app = Dash(__name__, external_stylesheets=[dbc.themes.SOLAR, dbc_css, dbc.icons.FONT_AWESOME])
server = app.server

# Grid params
columnDefs = [
    {'field': 'State FIPS'},
    {'field': 'State Name', 'headerName': 'State'},
    {'field': 'Congressional District'},
    {'field': 'County FIPS'},
    {'field': 'County'},
    {'field': 'Program Area'},
    {'field': 'Program'},
    {'field': 'NAICS Industry Sector'},
    {'field': 'Investment Dollars', 'headerName': 'Investments'},
    {'field': 'Number of Investments'},
]

app.layout = html.Div(
    [
        html.Div([
            html.H1("Figure Friday"),
        ], className='d-flex bg-primary bg-gradient text-white'),
        # ], className='d-flex align-items-center bg-secondary bg-gradient bg-opacity-25 p-3 flex-nowrap'),
        # html.Div([
        #
        # ], className='d-flex border  border-info border-3'),
        # html.Div([
        #
        # ], className='d-flex border border-info border-3', style={'height': '60%'}),
        html.Div([
            html.Div([
                html.Div('Total of Investments by:'),
                dcc.RadioItems(
                    id='radio-map-area-type',
                    options={
                        'state': 'States',
                        'CD': 'Congressional Districts',
                        'county': 'Counties'
                    },
                    value='state',
                    inline=True,
                    className='my-1'
                ),
                graph_invest_distrib,
                html.Div("Range of map's colorscale (set a nice range with the help of the above distribution):",
                         className='mt-1'),
                dcc.RangeSlider(
                    id="rangeslider-color",
                    min=0,
                    # step=0.001,
                    marks=None,
                    pushable=True,
                    tooltip={"placement": "bottom", "always_visible": True, "template": "${value}"},
                    className='mb-3'
                ),
                graph_map,
            ], className='d-flex flex-column w-50 p-2'),
            html.Div([
                html.Div("Investments proportions by 'Program Area' > 'Program' > 'NAICS Industry Sector':"),
                graph_program_details
            ], className='d-flex flex-column w-50 p-2'),
        ], className='d-flex', style={'height': '60%'}),

        html.Div([
            dag.AgGrid(
                id="grid-data",
                rowData=df.to_dict("records"),
                columnDefs=columnDefs,
                defaultColDef={'filter': True, 'flex': 1, "filterParams": {"buttons": ["reset"]}},
                style={"height": None},
                className="ag-theme-quartz-dark"
            ),
        ], className='d-flex flex-fill p-2'),

        dcc.Store(id='store-processed-geo-data'),
    ], className="dbc d-flex flex-column vh-100"
    # ], className="dbc d-flex flex-column vh-100 overflow-hidden border border-danger border-5"
)


@callback(
    Output("store-processed-geo-data", "data"),
    Input("grid-data", "virtualRowData"),
    Input("radio-map-area-type", "value")
)
def store_processed_filtered_geo_data(virtual_data, area_type):
    if virtual_data:
        dff = pd.DataFrame(virtual_data)
        dff["State FIPS"] = dff["State FIPS"].astype(str)
        dff["County FIPS"] = dff["County FIPS"].astype(str)

        # groupby depending on area type
        if area_type == 'state':
            group_by_cols = ['State FIPS', 'State Name']
        elif area_type == 'CD':
            group_by_cols = ['State FIPS', 'State Name', 'Congressional District']
        else:
            group_by_cols = ['State Name', 'County FIPS', 'County']

        dff = dff[[*group_by_cols, 'Investment Dollars', 'Number of Investments']].groupby(
            group_by_cols).sum().reset_index()

        # Add Id for Congressional Districts <State FIPS>-<CD> to match geojson data
        if area_type == 'CD':
            dff['id'] = dff.apply(lambda row: f"{row['State FIPS']}-{row['Congressional District']}", axis=1)

        return dff.to_json(orient='split')
    return no_update


@callback(
    Output("rangeslider-color", "max"),
    Output("rangeslider-color", "value"),
    Input("store-processed-geo-data", "data"),
    State("radio-map-area-type", "value"),
)
def update_map_color_range(processed_data, area_type):
    if processed_data:
        dff = pd.read_json(StringIO(processed_data), orient='split', dtype={'State FIPS': str, 'County FIPS': str})
        slider_max = dff['Investment Dollars'].max()
        max_val = 8 * 10 ** 6 if area_type == 'county' else 70 * 10 ** 6 if area_type == 'CD' else slider_max
        return slider_max, [0, max_val]
    return no_update


if __name__ == '__main__':
    app.run(debug=True)
