from dash import Dash, html, Input, Output, register_page, clientside_callback, _dash_renderer
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash_iconify import DashIconify

_dash_renderer._set_react_version("18.2.0")

layout_W38 = html.Div('Coming soon!')

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
            layout_W38
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
        path="/W38",
        name="W38",  # used as label for the main app navlink
        title="US H-1B Visa Lottery Data, 2021 to 2024",
        # image="assets/W38.jpg",  # used by the tooltip for the main app navbar
        description="""
        Every year, a random drawing determines which skilled foreigners get permission to work in the US. 
        But according to [Bloomberg](https://www.bloomberg.com/), some companies don’t play by the rules. 
        Read more at [Eric Fan’s post](https://www.linkedin.com/posts/ericfan24_every-year-a-random-drawing-determines-which-activity-7224534067688427520-QyqO)
        or the [full Story published by Bloomberg](https://www.bloomberg.com/graphics/2024-staffing-firms-game-h1b-visa-lottery-system/).
        """,
        data_source='*Data Source: [BloombergGraphics](https://github.com/BloombergGraphics/2024-h1b-immigration-data).*',
        disabled=True,
    )
    layout = html.Div([
        layout_W38
    ], className='h-100 d-flex')
