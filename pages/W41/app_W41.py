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


MTA_aggregate_controls = [
    dmc.Select(
        id="MTA-aggregate-sum-select",
        data=[
            {"value": "TOTAL", "label": "Total"},
            {"value": "D", "label": "Daily Mean"},
            {"value": "W-SAT", "label": "Weekly Mean"},
            {"value": "MS", "label": "Monthly Mean"},
            {"value": "QS", "label": "Quarterly Mean"},
            {"value": "2QS", "label": "Half-Yearly Mean"},
            {"value": "YS", "label": "Yearly Mean"},
        ],
        value="TOTAL",
        size="xs", w=180, searchable=True, allowDeselect=False, checkIconPosition="right",
        variant='unstyled',
        classNames={"input": 'fw-bold text-primary text-end text-decoration-underline'},
        styles={"input": {'font-family': 'Source Sans Pro', 'font-size': 22, 'cursor': 'pointer'}},
        rightSection=DashIconify(icon="mynaui:chevron-up-down"), rightSectionWidth=15,
        rightSectionPointerEvents="none",
    ),
    'of Ridership by',
    dmc.Select(
        id="MTA-aggregate-mean-select",
        data=[
            {"value": "ALL", "label": "Overall"},
            {"value": "M12", "label": "Year"},
            {"value": "M6", "label": "Semester"},
            {"value": "M3", "label": "Quarter"},
            {"value": "M1", "label": "Month"},
            {"value": "W", "label": "Week"},
            {"value": "D", "label": "Day"},
        ],
        value="M1",
        size="xs", w=180, searchable=True, allowDeselect=False, checkIconPosition="right",
        variant='unstyled',
        classNames={"input": 'fw-bold text-primary text-decoration-underline'},
        styles={"input": {'font-family': 'Source Sans Pro', 'font-size': 22, 'cursor': 'pointer'}},
        leftSection=DashIconify(icon="mynaui:chevron-up-down"), leftSectionWidth=15,
        rightSection=' ', rightSectionWidth=0,
        leftSectionPointerEvents="none", rightSectionPointerEvents="none",
    )
]


@callback(
    Output('MTA-aggregate-mean-select', 'data'),
    Input('MTA-aggregate-sum-select', "value"),
    State('MTA-aggregate-mean-select', 'data'),
)
def update_aggregate_mean_select_data(sum_value, mean_data):
    disabled_options = {
        "TOTAL": [],
        "D": ['D'],
        "W-SAT": ['W', 'D'],
        "MS": ['M1', 'W', 'D'],
        "QS": ['M3', 'M1', 'W', 'D'],
        "2QS": ['M6', 'M3', 'M1', 'W', 'D'],
        "YS": ['M12', 'M6', 'M3', 'M1', 'W', 'D'],
    }

    patched_options = Patch()
    for i, option in enumerate(mean_data):
        patched_options[i]["disabled"] = option['value'] in disabled_options[sum_value]

    return patched_options


layout_W41 = html.Div([

    dbc.Card([
        dbc.CardHeader(MTA_aggregate_controls, id='pollution-bar-title',
                       className='d-flex justify-content-center fs-5 text-body text-nowrap'),
        dbc.CardBody(components.MTA_aggregate_histogram, className='p-2'),
    ], className='flex-fill overflow-auto', style={'min-width': 300, 'min-height': 400}),

    dbc.Card([
        dbc.CardHeader('Pre-Pandemic Comparison',
                       className='d-flex justify-content-center fs-5 text-body text-nowrap'),
        dbc.CardBody(components.MTA_pre_pandemic_bar, className='p-2'),
    ], className='flex-fill overflow-auto', style={'min-width': 300, 'min-height': 400}),

], className='flex-fill d-flex flex-column p-2 overflow-auto')



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
        disabled=True,
    )
    layout = html.Div([
        layout_W41
    ], className='h-100 d-flex')
