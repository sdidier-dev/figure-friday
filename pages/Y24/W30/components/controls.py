from dash import dcc, html, Input, Output, State, callback, no_update
from dash_bootstrap_templates import ThemeChangerAIO, template_from_url
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import plotly.graph_objects as go

import pandas as pd
from io import StringIO

map_controls = html.Div([
    dmc.Divider(
        label=[
            DashIconify(icon='mdi:map-marker', height=25, color='var(--bs-primary)'),
            dmc.Text('Map', ml=5, size="lg", c='var(--bs-body-color)'),
        ], color='var(--bs-body-color)'),

    html.H6("Total of Investments by:", className='text-decoration-underline mt-4'),
    dmc.RadioGroup(
        id="radio-map-area-type",
        children=dmc.Stack([
            dmc.Radio(label='States', value='state', color='var(--bs-primary)'),
            dmc.Radio(label='Congressional Districts', value='CD', color='var(--bs-primary)'),
            dmc.Radio(label='Counties', value='county', color='var(--bs-primary)'),
        ], gap=10),
        value="state",
        size="sm", className='text-nowrap'
    ),

    html.H6("Range of map's colorscale:", className='text-decoration-underline mt-4'),
    html.Div([
        dmc.LoadingOverlay(
            id="graph-invest-distrib-loading-overlay",
            visible=True,
            loaderProps={"type": "bars", "color": "var(--bs-primary)"},
            overlayProps={"radius": "sm", "blur": 2},
        ),
        dcc.Graph(
            id='graph-invest-distrib',
            responsive=True,
            config={'displayModeBar': False},
            style={'height': 100, 'width': 300}
        ),
        dcc.RangeSlider(
            id="rangeslider-color",
            min=0, marks=None, pushable=True,
            tooltip={"placement": "bottom", "always_visible": True, "template": "${value}M"},
            className='dbc ps-5 mb-2'
        )
    ], style={'position': 'relative'})
], className='d-flex flex-column mb-5')

program_details_controls = html.Div([
    dmc.Divider(
        label=[
            DashIconify(icon='mingcute:document-fill', height=25, color='var(--bs-primary)'),
            dmc.Text('Programs', ml=5, size="lg", c='var(--bs-body-color)'),
        ], color='var(--bs-body-color)'),

    html.H6('Display only top categories (0 = All):', className='text-decoration-underline mt-4'),
    dmc.NumberInput(id='input-program-details-top-prog-area',
                    label="Program Area", value=5, min=0, w=70, className='text-nowrap'),
    dmc.NumberInput(id='input-program-details-top-prog',
                    label="Program", value=5, min=0, w=70, className='text-nowrap'),
    dmc.NumberInput(id='input-program-details-top-NAICS',
                    label="NAICS Industry Secctor", value=5, min=0, w=70, className='text-nowrap'),

    dmc.Checkbox(id="chk-program-details-hide-labels", label="Hide labels", color='var(--bs-primary)', mt=20),
])


@callback(
    Output("rangeslider-color", "max"),
    Output("rangeslider-color", "value"),
    Input("store-processed-geo-data", "data"),
    State("radio-map-area-type", "value"),
)
def update_map_color_range(processed_data, area_type):
    if not processed_data:
        return no_update, no_update
    dff = pd.read_json(StringIO(processed_data), orient='split', dtype={'State FIPS': str, 'County FIPS': str})
    slider_max = dff['Investment Dollars'].max() / 10 ** 6
    max_val = 8 if area_type == 'county' else 70 if area_type == 'CD' else slider_max
    return slider_max, [0, max_val]


# Note: can't use a patch while modifying the theme, the fig must be fully regenerated
@callback(
    Output("graph-invest-distrib", "figure"),
    Output("graph-invest-distrib-loading-overlay", "visible"),
    Input("store-processed-geo-data", "data"),
    Input(ThemeChangerAIO.ids.radio("theme"), "value"),
    Input("color-mode-switch", "checked"),
    State("radio-map-area-type", "value")
)
def update_invest_distrib(processed_data, theme, switch_on, area_type):
    if not processed_data:
        return no_update, no_update

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
        margin={'autoexpand': False, "r": 25, "t": 5, "l": 45, "b": 25},
        template=f"{template_from_url(theme)}{'' if switch_on else '_dark'}"
    )
    # Note: False is to hide the loader when the fig is ready
    return fig, False
