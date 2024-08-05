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

from assets.data import df, geojsons

load_figure_template("solar")

# Map fig base
fig_map = go.Figure()
fig_map.add_choroplethmapbox(
    colorscale="Viridis",
    marker_opacity=0.5,
    colorbar_title_text='Investment ($)'
)
fig_map.update_layout(
    mapbox_style='open-street-map',
    mapbox_zoom=2.5, mapbox_center={"lat": 37.0902, "lon": -95.7129},
    paper_bgcolor='rgba(0,0,0,0)',
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
)

# Map component
graph_map = dcc.Graph(
    id='graph-map',
    figure=fig_map,
    config=dict(responsive=True),
    className='flex-fill'
)


@callback(
    Output("graph-map", "figure"),
    Input("rangeslider-color", "value"),
    Input("store-processed-geo-data", "data"),
    State("radio-map-area-type", "value"),
)
def update_map_area(slider_range, processed_data, area_type):
    if processed_data:
        patched_fig = Patch()
        trace = patched_fig['data'][0]
        dff = pd.read_json(StringIO(processed_data), orient='split', dtype={'State FIPS': str, 'County FIPS': str})

        match area_type:
            case 'state':
                locations = dff['State FIPS']
                customdata = list(zip(dff['Number of Investments'], dff['State Name']))
                hovertemplate = '%{z:$.4s} (%{customdata[0]})<extra>%{customdata[1]}</extra>'
            case 'CD':
                locations = dff['id']
                customdata = list(zip(dff['Number of Investments'], dff['State Name'], dff['Congressional District']))
                hovertemplate = '%{z:$.4s} (%{customdata[0]})<extra>%{customdata[1]}-%{customdata[2]}</extra>'
            case _:
                locations = dff['County FIPS']
                customdata = list(zip(dff['Number of Investments'], dff['State Name'], dff['County']))
                hovertemplate = '%{z:$.4s} (%{customdata[0]})<extra>%{customdata[2]}, %{customdata[1]}</extra>'

        trace['geojson'] = geojsons[area_type]
        trace['featureidkey'] = 'id' if area_type != 'state' else 'properties.STATE'
        trace['locations'] = locations
        trace['z'] = dff['Investment Dollars']
        trace['customdata'] = customdata
        trace['hovertemplate'] = hovertemplate

        trace['zmin'] = slider_range[0]
        trace['zmax'] = slider_range[1]
        return patched_fig
    return no_update
