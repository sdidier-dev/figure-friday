from dash import html, Input, Output, callback, page_registry, clientside_callback
from dash_bootstrap_templates import ThemeChangerAIO
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash_iconify import DashIconify

page_titles = {}


def main_app_header(url_base_pathname):
    global page_titles
    page_titles = {page['path']: page['title'] for page in page_registry.values()}
    return html.Div([
        html.A(
            html.Div([
                DashIconify(icon="cil:graph", width=25, color='var(--bs-primary)'),
                html.Span(" FIGURE FRIDAY", className='text-linear-gradient fs-5 fw-bolder text-nowrap')
            ], className='d-inline-flex gap-1'),
            href=url_base_pathname if url_base_pathname else "/", className='text-decoration-none'),

        html.Div(id='app-title', className='flex-grow-1 text-center fs-3'),

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
                offcanvas_props={"placement": "end"}
            ),
            html.A(
                DashIconify(icon="mdi:github", width=34),
                href="https://github.com/sdidier-dev/figure-friday", target="_blank", className='text-body mx-2'
            ),
        ], className='d-inline-flex gap-2'),
    ], className='d-flex align-items-center border-bottom border-primary border-2 mx-2', style={'height': 60})


@callback(
    Output('app-title', 'children'),
    Input('current-url-location', 'pathname'),
    prevent_initial_call=True
)
def set_title(url):
    return page_titles[f"/{url.split('/')[-1]}"]


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
