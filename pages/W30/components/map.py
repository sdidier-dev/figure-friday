import json
import os

import pandas as pd
from io import StringIO

from dash import dcc, html, Input, Output, State, callback, no_update, clientside_callback
from dash_bootstrap_templates import ThemeChangerAIO, template_from_url
import dash_mantine_components as dmc

import plotly.graph_objects as go

# Load Geojsons
assets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets'))
geojsons = {}
for area_type in ['state', 'CD', 'county']:
    with open(f'{assets_dir}/geojson-usa-{area_type}.geojson') as f:
        geojsons[area_type] = json.load(f)

# Dash components
map_graph = html.Div([
    dmc.LoadingOverlay(
        id="graph-map-loading-overlay",
        visible=True,
        loaderProps={"type": "bars", "color": "var(--bs-primary)"},
        overlayProps={"radius": "sm", "blur": 2},
    ),
    dcc.Graph(
        id='graph-map',
        responsive=True,
        className='h-100'
    )
], className='h-100', style={'position': 'relative'})

# callback reactivating the loader when changing the dataset as it is time-consuming
clientside_callback(
    "(n_clicks) => true",
    Output("graph-map-loading-overlay", "visible", allow_duplicate=True),
    Input("store-processed-geo-data", "data"),
    prevent_initial_call=True,
)


# Note: can't use a patch while modifying the theme, the fig must be fully regenerated
@callback(
    Output("graph-map", "figure"),
    Output("graph-map-loading-overlay", "visible"),
    Input("rangeslider-color", "value"),
    Input("store-processed-geo-data", "data"),
    Input(ThemeChangerAIO.ids.radio("theme"), "value"),
    Input("color-mode-switch", "checked"),
    State("radio-map-area-type", "value")
)
def update_map_area(slider_range, processed_data, theme, switch_on, area_type):
    if not processed_data:
        return no_update

    dff = pd.read_json(
        StringIO(processed_data), orient='split',
        dtype={'state_GEOID': str, 'CD_GEOID': str, 'county_GEOID': str}
    )

    match area_type:
        case 'state':
            locations = dff['state_GEOID']
            customdata = list(zip(dff['Number of Investments'], dff['State Name']))
            hovertemplate = '%{z:$.4s} (%{customdata[0]})<extra>%{customdata[1]}</extra>'
        case 'CD':
            locations = dff['CD_GEOID']
            customdata = list(zip(dff['Number of Investments'], dff['State Name'], dff['Congressional District']))
            hovertemplate = '%{z:$.4s} (%{customdata[0]})<extra>%{customdata[1]}-%{customdata[2]}</extra>'
        case _:
            locations = dff['county_GEOID']
            customdata = list(zip(dff['Number of Investments'], dff['State Name'], dff['County']))
            hovertemplate = '%{z:$.4s} (%{customdata[0]})<extra>%{customdata[2]}, %{customdata[1]}</extra>'

    fig = go.Figure()
    fig.add_choropleth(
        geojson=geojsons[area_type],
        featureidkey='properties.GEOID',
        locations=locations,
        z=dff['Investment Dollars'],
        zmin=slider_range[0] * 10 ** 6,
        zmax=slider_range[1] * 10 ** 6,
        colorscale="Viridis",
        colorbar_title_text='Investment ($)',
        customdata=customdata,
        hovertemplate=hovertemplate,
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        geo=dict(scope='usa', bgcolor='rgba(0,0,0,0)', lakecolor='rgba(0,0,0,0)', landcolor='rgba(0,0,0,0)'),
        template=f"{template_from_url(theme)}{'' if switch_on else '_dark'}",
    )
    # Note: False is to hide the loader when the fig is ready
    return fig, False
