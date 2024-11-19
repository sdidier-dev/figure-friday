import os
from datetime import timedelta, datetime, date
from logging import disable
from pprint import pprint
from dash_bootstrap_templates import ThemeChangerAIO, template_from_url

from dash import Dash, html, Input, Output, register_page, clientside_callback, _dash_renderer, dcc, callback, State, \
    Patch, no_update
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import pandas as pd
import plotly.graph_objects as go

import pages.W41.components as components

# date: weekday, week of year, month, year
# total: overall since 2020, by year, month, week
# mean: overall yearly/monthly/weekly/daily mean
#       by year monthly/weekly/daily mean
#       by month weekly/daily mean
#       by week daily mean
# overlap by year, month, week
# compare pre covid

# decomposition: trend + seasonality+...
# auto-correlation

layout_W41 = html.Div([

    dbc.Card([
        dbc.CardHeader(components.MTA_aggregate_title_controls,
                       className='d-flex justify-content-center fs-5 text-body text-nowrap'),
        dbc.CardBody(components.MTA_aggregate_bar, className='p-2'),
    ], className='flex-fill', style={'min-width': 300, 'min-height': 400}),

    dbc.Card([
        dbc.CardHeader('Ridership Prediction',
                       className='d-flex justify-content-center fs-5 text-body text-nowrap'),
        dbc.CardBody('⚒ Coming Soon!', className='p-2'),
    ], className='flex-fill overflow-auto', style={'min-width': 300, 'min-height': 400}),
], className='flex-fill d-flex flex-column gap-2 p-2 overflow-auto')


if __name__ == '__main__':
    # for local development
    from dash_bootstrap_templates import ThemeChangerAIO

    _dash_renderer._set_react_version("18.2.0")

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
            layout_W41
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
        path="/W41",
        name="W41",  # used as label for the main app navlink
        title="New York City Subway (MTA) Daily Ridership Data: Beginning 2020",
        # image="assets/W41.jpg",  # used by the tooltip for the main app navbar
        description="""
        The daily ridership dataset provides system wide ridership and traffic estimates for subways (including the 
        Staten Island Railway), buses, Long Island Rail Road, Metro-North Railroad, Access-A-Ride, and Bridges and 
        Tunnels, beginning 3/1/2020, and provides a percentage comparison against a comparable pre-pandemic date.
        """,
        data_source="""
        *Data Source: [New York State Open Data](https://data.ny.gov/Transportation/MTA-Daily-Ridership-Data-Beginning-2020/vxuj-8kew/about_data).  
        Created March 15, 2022; Last Updated October 12, 2024*        
        """,
        disabled=False,
    )
    layout = html.Div([
        layout_W41
    ], className='h-100 d-flex')
