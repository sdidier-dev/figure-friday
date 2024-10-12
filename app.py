from dash import Dash, html, page_container, dcc, _dash_renderer
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from components import *

_dash_renderer._set_react_version("18.2.0")

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"

app = Dash(
    use_pages=True,
    external_stylesheets=[dbc_css, dbc.themes.SOLAR],
)

server = app.server

page_container.className = 'flex-fill overflow-auto'

app.layout = dmc.MantineProvider([
    dcc.Location(id='current-url-location'),
    html.Div([
        main_app_header(app.config.url_base_pathname),
        html.Div([
            main_app_navbar(),
            page_container
        ], className='flex-fill d-flex overflow-auto'),
    ], className='d-flex flex-column vh-100')
])

if __name__ == "__main__":
    app.run(debug=True)
