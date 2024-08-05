import json
from io import StringIO
from pprint import pprint

from dash import Dash, dcc, html, Input, Output, State, callback, Patch, no_update
import dash_bootstrap_components as dbc
import dash_ag_grid as dag

import plotly.express as px
import plotly.graph_objects as go

import pandas as pd
from dash_bootstrap_templates import load_figure_template

from assets.data import df, geojsons

load_figure_template("solar")

fig_invest_distrib = go.Figure()
fig_invest_distrib.add_histogram(
    xbins_start=0, nbinsx=50,
)
fig_invest_distrib.update_layout(
    title_text='Investment distribution',
    title_x=0.5,
    paper_bgcolor='rgba(0,0,0,0)',

    margin={'autoexpand': False, "r": 25, "t": 25, "l": 25, "b": 25},
)

graph_invest_distrib = dcc.Graph(
    id='graph-invest-distrib',
    figure=fig_invest_distrib,
    config=dict(responsive=True),
    # className='flex-fill',
    style={'height': '20%'}
)


@callback(
    Output("graph-invest-distrib", "figure"),
    Input("store-processed-geo-data", "data"),
)
def update_invest_distrib(processed_data):
    if processed_data:
        dff = pd.read_json(StringIO(processed_data), orient='split', dtype={'State FIPS': str, 'County FIPS': str})
        patched_fig = Patch()
        patched_fig['data'][0]['x'] = dff['Investment Dollars']
        return patched_fig
    return no_update
