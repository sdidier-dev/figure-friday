from dash import Dash, html,  Input, Output, register_page, clientside_callback, _dash_renderer
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash_iconify import DashIconify

from pages.W35.components import *

layout_W35 = html.Div([

    dbc.Card([
        dbc.CardHeader("People Map", className='fs-5 text-body text-center'),
        dbc.CardBody(people_map_graph, className='p-2'),
    ], className='h-50'),

    html.Div([
        html.Div("The grid can be used to filter the data of the map"),
        people_grid
    ], className='h-50 d-flex flex-column dbc dbc-ag-grid'),

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
            layout_W35
        ], className='vh-100 d-flex flex-column')
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
        path="/W35",
        name="W35",  # used as label for the main app navlink
        title="People Map of the US",
        description='What if we replace the names of US cities by the name of their most Wikipedia’ed resident '
                    '(from July 2015 through May 2019): people born in, lived in, or connected to a place?',
        image="assets/W35.jpg",  # used by the tooltip for the main app navbar
        data_source='*Data Source: '
                    '[People Map](https://github.com/the-pudding/data/tree/master/people-map), '
                    'from [The Pudding](https://pudding.cool/)*',
        disabled=False,
    )
    layout = html.Div([
        layout_W35
    ], className='h-100 d-flex')
