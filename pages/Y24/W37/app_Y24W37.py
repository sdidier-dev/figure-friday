from dash import Dash, html, Input, Output, register_page, clientside_callback, _dash_renderer
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash_iconify import DashIconify

_dash_renderer._set_react_version("18.2.0")

layout_W37 = html.Div('Coming soon!')

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
            layout_W37
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
        path="/2024/W37",
        name="W37",  # used as label for the main app navlink
        title="Child mortality rate, under age five, 1751 to 2022",
        # image="assets/W37.jpg",  # used by the tooltip for the main app navbar
        description="""
        Child mortality is one of the world’s largest problems. For most of human history, around 1 in 2 newborns died 
        before reaching the age of 15. By 1950, that figure had declined to around one-quarter globally. By 2020, 
        it had fallen to 4%.  
                         
        But while humanity has made much progress, there’s still a lot of work to do. To make more progress, 
        it’s essential to have data on child mortality and its causes, and research on how to prevent it.
        """,
        data_source='*Data Source: United Nations Inter-agency Group for Child Mortality Estimation (UN IGME, 2024) '
                    'and [Gapminder](https://www.gapminder.org/data/documentation/gd005/) (2015).*',
        disabled=True,
    )
    layout = html.Div([
        layout_W37
    ], className='h-100 d-flex')
