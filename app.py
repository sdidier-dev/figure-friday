from dash_bootstrap_templates import ThemeChangerAIO
from dash import Dash, html, page_container, dcc, Input, Output, State, callback, page_registry, ALL, ctx, no_update
import dash_bootstrap_components as dbc

# from apps import layout_W30

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
app = Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc_css, dbc.icons.BOOTSTRAP]
)

server = app.server

page_container.className = 'flex-fill'

header = html.Div([
    html.Div([
        ThemeChangerAIO(
            aio_id="theme",
            radio_props=dict(value=dbc.themes.SOLAR),
            button_props=dict(outline=False, color="primary"),
        ),
        html.Div([
            dbc.Label(className="bi bi-moon-stars-fill", html_for="color-mode-switch"),
            dbc.Switch(id="color-mode-switch", className="ms-1", persistence=True),
            dbc.Label(className="bi bi-sun-fill", html_for="color-mode-switch"),
        ], className="d-flex mt-1"),
    ], className="d-flex flex-column align-items-center"),

    html.Div("Figure Friday", className='flex-grow-1 fs-1 text-center'),
    html.A(
        html.Div(className='bi bi-github fs-1'),
        href="https://github.com/sdidier-dev/figure-friday",
        target='_blank', style={'color': 'inherit'}
    )
], className='d-flex bg-gradient align-items-center p-2')

buttons_with_tooltips = []
for page in page_registry.values():
    buttons_with_tooltips += [
        dbc.Button(
            page['name'],
            id={'type': 'nav-btn', 'index': page['path']},
            href=page['path'],
            color="primary"
        ),
        dbc.Tooltip(page['title'], target={'type': 'nav-btn', 'index': page['path']}, className='border border-primary')
    ]

app.layout = html.Div([
    header,
    dcc.Location(id='current-url-location'),
    dbc.ButtonGroup(buttons_with_tooltips, className='mx-2'),
    page_container
], className='d-flex flex-column vh-100')


@callback(
    Output({'type': 'nav-btn', 'index': ALL}, 'outline'),
    Input('current-url-location', 'pathname')
)
def update_btn_outline(url):
    return [output['id']['index'] != f"/{url.split('/')[-1]}" for output in ctx.outputs_list]


if __name__ == '__main__':
    app.run()
