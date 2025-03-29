from dash import Dash, html, Input, Output, register_page, clientside_callback, _dash_renderer
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash_iconify import DashIconify

_dash_renderer._set_react_version("18.2.0")

layout_W33 = html.Div('Coming soon!')

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
            layout_W33
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
        path="/2024/W33",
        name="W33",  # used as label for the main app navlink
        title="US Presidential Election Results by State from 1976 to 2020",
        # image="assets/W33.jpg",  # used by the tooltip for the main app navbar
        description='Self explanatory 😎'
                    '\n\n**(Coming soon!)**',
        data_source='*Data Source: '
                    '[US Elections Dataset](https://www.kaggle.com/datasets/tunguz/us-elections-dataset/data), '
                    'provided by Bojan Tunguz.*',
        disabled=True,
    )
    layout = html.Div([
        layout_W33
    ], className='h-100 d-flex')
