import json
import os

import pandas as pd
from io import StringIO

from dash import dcc, html, Input, Output, State, callback, no_update
from dash_bootstrap_templates import ThemeChangerAIO, template_from_url
import plotly.graph_objects as go

# Load Geojsons
assets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets'))
geojsons = {}
for area_type in ['state', 'CD', 'county']:
    with open(f'{assets_dir}/geojson-usa-{area_type}.geojson') as f:
        geojsons[area_type] = json.load(f)

# Dash components
graph_invest_distrib = dcc.Graph(
    id='graph-invest-distrib',
    config=dict(responsive=True),
    style={'height': '75px'}
)

map_controls = html.Div([
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
            className='my-1'
        ),
    ], className='d-inline-flex flex-column m-2'),

    html.Div([
        html.Div("Range of map's colorscale:", className='mb-2'),
        graph_invest_distrib,
        dcc.RangeSlider(
            id="rangeslider-color",
            min=0,
            marks=None,
            pushable=True,
            tooltip={"placement": "bottom", "always_visible": True, "template": "${value}M"},
            className='mb-2 ps-5'
        )
    ], className='d-flex flex-column flex-fill m-2'),

], className='d-flex h-auto')

map_graph = dcc.Graph(
    id='graph-map',
    config=dict(responsive=True),
    className='flex-fill'
)


@callback(
    Output("rangeslider-color", "max"),
    Output("rangeslider-color", "value"),
    Input("store-processed-geo-data", "data"),
    State("radio-map-area-type", "value"),
)
def update_map_color_range(processed_data, area_type):
    if processed_data:
        dff = pd.read_json(StringIO(processed_data), orient='split', dtype={'State FIPS': str, 'County FIPS': str})
        slider_max = dff['Investment Dollars'].max() / 10 ** 6
        max_val = 8 if area_type == 'county' else 70 if area_type == 'CD' else slider_max
        return slider_max, [0, max_val]
    return no_update


# Note: can't use a patch while modifying the theme, the fig must be fully regenerated
@callback(
    Output("graph-invest-distrib", "figure"),
    Input("store-processed-geo-data", "data"),
    Input(ThemeChangerAIO.ids.radio("theme"), "value"),
    Input("color-mode-switch", "value"),
    State("radio-map-area-type", "value")
)
def update_invest_distrib(processed_data, theme, switch_on, area_type):
    if not processed_data:
        return no_update

    dff = pd.read_json(StringIO(processed_data), orient='split', dtype={'State FIPS': str, 'County FIPS': str})
    fig = go.Figure()
    fig.add_histogram(
        # add [-1] to the list as a trick to solve a bug,
        # the histogram seems to dislike when there is only one data point > 1M (7 digits)
        x=[-1] + dff['Investment Dollars'].tolist(),
        xbins_start=0, nbinsx=50,
    )
    yaxis_title_text = f"Nb of {'States' if area_type == 'state' else 'CDs' if area_type == 'CD' else 'Counties'}"
    fig.update_layout(
        title_text='Investment distribution',
        title_font_size=14,
        title_x=0.5,
        title_y=0.95,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis_showgrid=False,
        yaxis_title_text=yaxis_title_text,
        yaxis_title_font_size=12,
        margin={'autoexpand': False, "r": 25, "t": 5, "l": 48, "b": 25},
        template=f"{template_from_url(theme)}{'' if switch_on else '_dark'}"
    )

    return fig


# Note: can't use a patch while modifying the theme, the fig must be fully regenerated
@callback(
    Output("graph-map", "figure"),
    Input("rangeslider-color", "value"),
    Input("store-processed-geo-data", "data"),
    Input(ThemeChangerAIO.ids.radio("theme"), "value"),
    Input("color-mode-switch", "value"),
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
    title_text_by = 'State' if area_type == 'state' else 'Congressional District' if area_type == 'CD' else 'County'
    fig.update_layout(
        title_text=f"Investment by {title_text_by}",
        title_x=0.4,
        title_y=0.9,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        geo_scope='usa',
        template=f"{template_from_url(theme)}{'' if switch_on else '_dark'}",
    )
    return fig
