from dash import Dash, html, Input, Output, register_page, clientside_callback, _dash_renderer
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash_iconify import DashIconify

# import pages.Y25.W13.components as components

layout_Y25W13 = html.Div([
    'cool'

], className='flex-fill d-flex flex-column align-items-center gap-2 p-2 overflow-auto dbc-ag-grid')

if __name__ == '__main__':
    # for local development
    from dash_bootstrap_templates import ThemeChangerAIO

    _dash_renderer._set_react_version("18.2.0")

    dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"

    app = Dash(
        external_stylesheets=[dbc.themes.SOLAR, dbc_css, dmc.styles.DATES],
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
            layout_Y25W13
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
        path="/2025/W13",
        name="W13",  # used as label for the main app navlink
        title="New York City Subway (MTA) Daily Ridership Data: Beginning 2020",
        # image="assets/W13.jpg",  # used by the tooltip for the main app navbar
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
        layout_Y25W13
    ], className='h-100 d-flex')
