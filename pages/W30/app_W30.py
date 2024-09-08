from dash import Dash, dcc, html, Input, Output, State, callback, no_update, register_page, clientside_callback, \
    _dash_renderer
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from prefixed import Float

import pandas as pd

from pages.W30.components import *

_dash_renderer._set_react_version("18.2.0")

layout_W30 = html.Div([
    # Drawer
    html.Div([
        html.Div([
            html.Div('Controls', className='fs-4 fw-bolder text-center p-2'),
            map_controls,
            program_details_controls
        ], className='d-flex flex-column h-100 border-end border-secondary mb-2 p-2'),
    ], id='controls-drawer', className='d-flex justify-content-end h-100',
        style={'transition': 'width 1s', 'width': 330}),

    # Controls collapse button
    html.Div([
        dmc.ActionIcon(
            DashIconify(id='collapse-controls-btn-icon', icon='mdi:chevron-double-left', width=25),
            id="collapse-controls-btn",
            radius='xl', variant="outline", color='var(--bs-secondary)', bg='var(--bs-body-bg)',
        )],
        className='d-flex justify-content-center pt-4 overflow-visible', style={'width': 0}
    ),

    # Main container
    html.Div([
        # TL;DR
        html.Div([
            dbc.Card([
                dbc.CardHeader("Total Overall", className='fs-6 text-body p-0'),
                dbc.CardBody(id='tldr-overall-div', className='p-1'),
            ], color="primary", outline=True, className='text-nowrap text-center'),
            dbc.Card([
                dbc.CardHeader("Total Filtered", className='fs-6 text-body p-0'),
                dbc.CardBody(id='tldr-filtered-div', className='p-1'),
            ], color="primary", outline=True, className='text-nowrap text-center'),
        ], className='d-flex justify-content-center gap-4'),

        # Grid
        html.Div([
            html.Div("The grid can be used to filter the data of the graphs"),
            rural_inv_grid
        ], className='h-50 d-flex flex-column dbc dbc-ag-grid'),

        # Graphs
        html.Div([
            # Map
            dbc.Card([
                dbc.CardHeader(id='graph-card-header', className='fs-5 text-body text-center'),
                dbc.CardBody(map_graph, className='p-2'),
            ], className='flex-fill', style={'min-width': 700, 'min-height': 400}),
            # Programs
            dbc.Card([
                dbc.CardHeader("Investments by programs", className='fs-5 text-body text-center'),
                dbc.CardBody(program_details_graph, className='p-2'),
            ], className='flex-fill', style={'min-width': 700, 'min-height': 400}),
        ], className='h-50 d-flex flex-wrap overflow-auto gap-2'),

        dcc.Store(id='store-processed-geo-data'),
    ], className='flex-fill d-flex flex-column gap-2 p-2')

], className='flex-fill d-flex')


@callback(
    Output("collapse-controls-btn-icon", "flip"),
    Output("controls-drawer", "style"),
    Input("collapse-controls-btn", "n_clicks"),
    prevent_initial_call=True
)
def collapse_controls(n_clicks):
    return (
        "horizontal" if n_clicks % 2 else None,
        {'transition': 'width 1s', 'width': 0 if n_clicks % 2 else 330}
    )


@callback(
    Output("tldr-overall-div", "children"),
    Output("tldr-filtered-div", "children"),
    Input("grid-data", "virtualRowData"),
    State("tldr-overall-div", "children"),
)
def update_tldr_text(virtual_data, tldr_overall_children):
    if not virtual_data:
        return no_update, no_update

    dff = pd.DataFrame(virtual_data)

    # Overall tldr, created only at init
    if not tldr_overall_children:
        tldr_overall = {
            'total': f"${Float(dff['Investment Dollars'].sum()):.2h}",
            'total_nb': f"{dff['Number of Investments'].sum():,}",
            'min': f"${Float(dff['Investment Dollars'].min()):.2h}",
            'mean': f"${Float(dff['Investment Dollars'].sum() // dff['Number of Investments'].sum()):.2h}",
            'max': f"${Float(dff['Investment Dollars'].max()):.2h}",
        }
        tldr_overall_children = [
            html.Div([
                html.Span(tldr_overall['total'], className='text-primary fw-bold'), ' in ',
                html.Span(tldr_overall['total_nb'], className='text-primary fw-bold'), ' investments',
            ], className='fs-5'),
            '(min ', html.Span(tldr_overall['min'], className='text-primary fw-bold'), ' | mean ',
            html.Span(tldr_overall['mean'], className='text-primary fw-bold'), ' | max ',
            html.Span(tldr_overall['max'], className='text-primary fw-bold'), ')'
        ]
    else:
        tldr_overall_children = no_update

    # Filtered tldr
    tldr_filtered = {
        'total': f"${Float(dff['Investment Dollars'].sum()):.2h}",
        'total_nb': f"{dff['Number of Investments'].sum():,}",
        'min': f"${Float(dff['Investment Dollars'].min()):.2h}",
        'mean': f"${Float(dff['Investment Dollars'].sum() // dff['Number of Investments'].sum()):.2h}",
        'max': f"${Float(dff['Investment Dollars'].max()):.2h}",
    }
    tldr_filtered_children = [
        html.Div([
            html.Span(tldr_filtered['total'], className='text-primary fw-bold'), ' in ',
            html.Span(tldr_filtered['total_nb'], className='text-primary fw-bold'), ' investments',
        ], className='fs-5'),
        '(min ', html.Span(tldr_filtered['min'], className='text-primary fw-bold'), ' | mean ',
        html.Span(tldr_filtered['mean'], className='text-primary fw-bold'), ' | max ',
        html.Span(tldr_filtered['max'], className='text-primary fw-bold'), ')'
    ]

    return tldr_overall_children, tldr_filtered_children


@callback(
    Output("graph-card-header", "children"),
    Input("radio-map-area-type", "value"),
)
def update_graph_title(area_type):
    title_text_by = 'State' if area_type == 'state' else 'Congressional District' if area_type == 'CD' else 'County'
    return f"Investment by {title_text_by}"


@callback(
    Output("store-processed-geo-data", "data"),
    Input("grid-data", "virtualRowData"),
    Input("radio-map-area-type", "value"),
)
def store_processed_filtered_geo_data(virtual_data, area_type):
    if not virtual_data:
        return no_update

    dff = pd.DataFrame(virtual_data)
    # groupby depending on area type
    if area_type == 'state':
        group_by_cols = ['state_GEOID', 'State Name']
    elif area_type == 'CD':
        group_by_cols = ['CD_GEOID', 'State Name', 'Congressional District']
    else:
        group_by_cols = ['county_GEOID', 'State Name', 'County']

    dff = dff[[*group_by_cols, 'Investment Dollars', 'Number of Investments']].groupby(
        group_by_cols).sum().reset_index()

    return dff.to_json(orient='split')


if __name__ == '__main__':
    # for local development
    from dash_bootstrap_templates import ThemeChangerAIO

    dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"

    app = Dash(
        external_stylesheets=[dbc.themes.SOLAR, dbc_css],
        url_base_pathname='/',
    )

    app.layout = dmc.MantineProvider(
        html.Div([
            html.Div([
                dmc.Switch(
                    id='color-mode-switch',
                    offLabel=DashIconify(icon="radix-icons:moon", width=20),
                    onLabel=DashIconify(icon="radix-icons:sun", width=20),
                    size="lg", color='var(--bs-primary)',
                    styles={"track": {'border': '2px solid var(--bs-primary)'}},
                ),
                ThemeChangerAIO(
                    aio_id="theme",
                    radio_props=dict(value=dbc.themes.SOLAR),
                    button_props=dict(outline=False, color="primary"),
                ),
            ], className='d-inline-flex gap-2'),
            layout_W30
        ], className='h-100 d-flex flex-column')
    )

    # Switch color-theme for DBC and DMC components
    clientside_callback(
        """
        (switchOn) => {
           document.documentElement.setAttribute('data-bs-theme', switchOn ? 'light' : 'dark');
           document.documentElement.setAttribute('data-mantine-color-scheme', switchOn ? 'light' : 'dark');
           return window.dash_clientside.no_update
        }
        """,
        Output("color-mode-switch", "id"),
        Input("color-mode-switch", "checked"),
    )

    app.run(debug=True)
else:
    # for the main Figure Friday app
    register_page(
        __name__,
        path="/W30",
        name="W30",  # used as label for the main app navlink
        title="Rural investments in the US in 2024",  # used by the tooltip for the main app navbar
        description='The [Rural Development Agency](https://www.rd.usda.gov/about-rd) is part of the US Department of '
                    'Agriculture and it provides loans, grants, and loan guarantees to bring prosperity and '
                    'opportunity to rural areas.',
        image="assets/W30.jpg",  # used by the tooltip for the main app navbar
        data_source='*Data Source: [USDA-RD website](https://www.rd.usda.gov/rural-data-gateway/rural-investments/data) '
                    'filtered by fiscal year 2024.*',
        disabled=False,
    )
    layout = html.Div([
        layout_W30
    ], className='h-100 d-flex')
