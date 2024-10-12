from dash import Dash, html, Input, Output, register_page, clientside_callback, _dash_renderer
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash_iconify import DashIconify

from pages.home.components import *

layout_home = html.Div([
    home_background_graph,
    home_part1,
    home_part2,
    home_part3,
], id='home-page', className='flex-fill d-inline-flex flex-column')

if __name__ == "__main__":
    # for local development
    from dash_bootstrap_templates import ThemeChangerAIO

    _dash_renderer._set_react_version("18.2.0")

    dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"

    app = Dash(
        external_stylesheets=[dbc.themes.SOLAR, dbc_css, dbc.icons.BOOTSTRAP],
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
            layout_home
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
        path='/',
        name=DashIconify(icon="ic:outline-home", width=25),
        title='Welcome to Plotly Figure Friday Project !',
        description="""
        Plotly launched a weekly initiative: 
        [Figure Friday](https://community.plotly.com/t/announcing-plotly-weekly-data-viz-projects-figure-friday/84953) !
        
        Each Friday, a new dataset is released with a sample figure. The aim is to gain insights from the data creating amazing
        visualisations.
        """,
        # image="assets/home.jpg",  # used by the tooltip for the main app navbar
        data_source=None,
        disabled=False,
    )
    layout = html.Div([
        layout_home
    ], className='h-100 d-flex')
