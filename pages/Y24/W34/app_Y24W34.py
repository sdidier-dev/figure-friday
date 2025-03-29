from dash import Dash, html, Input, Output, register_page, clientside_callback, _dash_renderer, callback
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash_iconify import DashIconify

from pages.Y24.W34.components import *

layout_W34 = html.Div([

    dbc.Card([
        dbc.CardHeader(id='genre-graph-card-header', className='fs-5 text-body text-center'),
        dbc.CardBody([
            genre_graph_controls,
            genre_graph
        ], className='p-2'),
    ], className='h-50', style={'min-width': 700, 'min-height': 300}),

    dbc.Card([
        dbc.CardHeader("Track Features Correlation", className='fs-5 text-body text-center'),
        dbc.CardBody([
            heatmap_corr_graph,
            detail_corr_graph,
        ], className='d-flex flex-wrap overflow-auto gap-2 p-2'),
    ], className='h-50'),

], className='flex-fill d-flex flex-column gap-2 p-2')


@callback(
    Output("genre-graph-card-header", "children"),
    Input("feature-dropdown", "value"),
)
def update_genre_card_header(genre):
    genre = 'duration (ms)' if genre == 'duration_ms' else genre
    return [
        "Mean and Standard Deviation of ",
        html.Span(genre.capitalize(), className='fw-bold', style={'color': 'var(--bs-primary)'}),
        " by Track Genre"
    ]


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
            layout_W34
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
        path="/2024/W34",
        name="W34",  # used as label for the main app navlink
        title="Spotify Tracks Exploration",
        description='Here, we explore various parameters of songs, such as genre, danceability, tempo, '
                    'and other relevant musical attributes. of approximately 90,000 Spotify tracks.',
        image="assets/Y24W34.jpg",  # used by the tooltip for the main app navbar
        data_source='*Data Source: '
                    '[Spotify Tracks Dataset]'
                    '(https://www.kaggle.com/datasets/maharshipandya/-spotify-tracks-dataset/data), '
                    'by MaharshiPandya*',
        disabled=False,
    )
    layout = html.Div([
        layout_W34
    ], className='h-100 d-flex')
