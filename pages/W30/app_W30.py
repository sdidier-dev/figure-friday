from dash import Dash, dcc, html, Input, Output, State, callback, no_update, register_page, clientside_callback
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import ThemeChangerAIO
from prefixed import Float

import pandas as pd

from pages.W30.components import *

layout_W30 = [
    html.H3("Rural investments in the US in 2024", className='text-body text-center m-2'),

    dbc.Card([
        html.Div(id='tldr-overall-div', className=' flex-fill text-center'),
        html.Div(id='tldr-filtered-div', className=' flex-fill text-center'),
    ], className='d-flex flex-row p-2 mx-2', color="primary", outline=True),

    html.Div([
        dbc.Card([
            dbc.CardHeader("Investments by geographic areas", className='fs-5 text-body text-center'),
            dbc.CardBody([
                map_controls,
                map_graph,
            ], className='d-flex flex-column p-2'),
        ], className='w-50 m-2'),
        dbc.Card([
            dbc.CardHeader("Investments by programs", className='fs-5 text-body text-center'),
            dbc.CardBody([
                program_details_controls,
                program_details_graph,
            ], className='d-flex flex-column p-2'),
        ], className='w-50 m-2'),
    ], className='d-flex', style={'height': '55%'}),

    html.Div(
        [
            html.Div("The grid can be used to filter the data of the graphs"),
            aggrig_grid
        ], className='d-flex flex-column flex-fill m-2 dbc dbc-ag-grid'
    ),

    dcc.Store(id='store-processed-geo-data'),
]


@callback(
    Output("tldr-overall-div", "children"),
    Output("tldr-filtered-div", "children"),
    Input("grid-data", "virtualRowData"),
    State("tldr-overall-div", "children"),
)
def update_tldr_text(virtual_data, tldr_overall_children):
    if virtual_data:
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
                'OVERALL TOTAL: ', html.Span(tldr_overall['total'], className='text-primary fw-bold'), ' in ',
                html.Span(tldr_overall['total_nb'], className='text-primary fw-bold'), ' investments', html.Br(),
                '(min ', html.Span(tldr_overall['min'], className='text-primary fw-bold'), ' | mean ',
                html.Span(tldr_overall['mean'], className='text-primary fw-bold'), ' | max ',
                html.Span(tldr_overall['max'], className='text-primary fw-bold'), ')'
            ]
        else:
            tldr_overall_children = no_update

        # Filtered tldr, created only at init
        tldr_filtered = {
            'total': f"${Float(dff['Investment Dollars'].sum()):.2h}",
            'total_nb': f"{dff['Number of Investments'].sum():,}",
            'min': f"${Float(dff['Investment Dollars'].min()):.2h}",
            'mean': f"${Float(dff['Investment Dollars'].sum() // dff['Number of Investments'].sum()):.2h}",
            'max': f"${Float(dff['Investment Dollars'].max()):.2h}",
        }
        tldr_filtered_children = [
            'FILTERED TOTAL (with the grid): ', html.Span(tldr_filtered['total'], className='text-primary fw-bold'),
            ' in ', html.Span(tldr_filtered['total_nb'], className='text-primary fw-bold'), ' investments', html.Br(),
            '(min ', html.Span(tldr_filtered['min'], className='text-primary fw-bold'), ' | mean ',
            html.Span(tldr_filtered['mean'], className='text-primary fw-bold'), ' | max ',
            html.Span(tldr_filtered['max'], className='text-primary fw-bold'), ')'
        ]

        return tldr_overall_children, tldr_filtered_children
    return no_update


@callback(
    Output("store-processed-geo-data", "data"),
    Input("grid-data", "virtualRowData"),
    Input("radio-map-area-type", "value"),
)
def store_processed_filtered_geo_data_and_tldr_text(virtual_data, area_type):
    if virtual_data:
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
    return no_update


clientside_callback(
    """
    (switchOn) => {
       document.documentElement.setAttribute('data-bs-theme', switchOn ? 'light' : 'dark');  
       return window.dash_clientside.no_update
    }
    """,
    Output("color-mode-switch", "id"),
    Input("color-mode-switch", "value"),
)

if __name__ == '__main__':
    # for local development
    dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
    app = Dash(__name__, external_stylesheets=[dbc.themes.SOLAR, dbc.icons.BOOTSTRAP, dbc_css])
    app.layout = html.Div(
        [
            ThemeChangerAIO(
                aio_id="theme",
                radio_props=dict(value=dbc.themes.SOLAR),
                button_props=dict(outline=False, color="primary"),
            ),
            html.Span([
                dbc.Label(className="bi bi-moon-stars-fill", html_for="color-mode-switch"),
                dbc.Switch(id="color-mode-switch", className="d-inline-block ms-1"),
                dbc.Label(className="bi bi-sun-fill", html_for="color-mode-switch"),
            ]),
            *layout_W30
        ], className="dbc d-flex flex-column vh-100"
    )

    app.run(debug=True)
else:
    # for the main Figure Friday app
    register_page(
        __name__,
        path="/W30",
        name="W30",  # will be used as label for the main app buttons
        title="Rural investments in the US in 2024",  # will be used as tooltip for the main app buttons
    )
    layout = html.Div(layout_W30, className="dbc d-flex flex-column h-100")
