import json
from pprint import pprint

from dash import Dash, dcc, html, Input, Output, register_page, clientside_callback, _dash_renderer, callback, no_update
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from dash_bootstrap_templates import ThemeChangerAIO, template_from_url

from pages.W34.components import *

md_text = """`acousticness`:  
A confidence measure ranging from 0.0 to 1.0 that indicates the likelihood of a given track being
classified as acoustic. A value of 1.0 should signify a high level of confidence that the track is indeed acoustic.

`danceability`:  
Describes how suitable a track is for dancing based on a combination of musical elements including
tempo, rhythm stability, beat strength, and overall regularity. A value of 0.0 is least danceable and 1.0 is
most danceable.

`duration_ms`:  
The track length in milliseconds.

`energy`:  
Is a measure from 0.0 to 1.0 and represents a perceptual measure of intensity and activity.
Typically, energetic tracks feel fast, loud, and noisy. For example, death metal has high energy, while a Bach prelude
scores low on the scale.

`instrumentalness`:  
Predicts whether a track contains no vocals. "Ooh" and "aah" sounds are treated as instrumental in
this context. Rap or spoken word tracks are clearly "vocal". The closer the instrumentalness value is to 1.0, the
greater likelihood the track contains no vocal content.

`liveness`:  
Detects the presence of an audience in the recording. Higher liveness values represent an increased
probability that the track was performed live. A value above 0.8 provides strong likelihood that the track is live.

`loudness`:  
The overall loudness of a track in decibels (dB).

`popularity`:  
The popularity of a track is a value between 0 and 100, with 100 being the most popular. The popularity
is calculated by algorithm and is based, in the most part, on the total number of plays the track has had and how recent
those plays are. Generally speaking, songs that are being played a lot now will have a higher popularity than songs that
were played a lot in the past. Duplicate tracks (e.g. the same track from a single and an album) are rated
independently. Artist and album popularity is derived mathematically from track popularity.

`speechiness`:  
Speechiness detects the presence of spoken words in a track. The more exclusively speech-like the
recording (e.g. talk show, audio book, poetry), the closer to 1.0 the attribute value. Values above 0.66 describe tracks
that are probably made entirely of spoken words. Values between 0.33 and 0.66 describe tracks that may contain both
music and speech, either in sections or layered, including such cases as rap music. Values below 0.33 most likely
represent music and other non-speech-like tracks.

`tempo`:  
The overall estimated tempo of a track in beats per minute (BPM). In musical terminology, tempo is the speed
or pace of a given piece and derives directly from the average beat duration.

`valence`:  
A measure from 0.0 to 1.0 describing the musical positiveness conveyed by a track. Tracks with high valence
sound more positive (e.g. happy, cheerful, euphoric), while tracks with low valence sound more negative (e.g. sad,
depressed, angry).
"""

layout_W34 = html.Div([
    # Drawer
    html.Div([
        html.Div([
            html.Div('Features Description', className='fs-5 fw-bolder text-center border-bottom border-secondary p-2'),
            # html.Div([
            #     html.Div('cool', className='border border-primary', style={'height': 100}) for i in range(15)
            #     # html.P('cool', className='border border-primary', style={'height': 100}) for i in range(15)
            # ], className='flex-fill overflow-auto border border-primary'),
            dcc.Markdown(
                # md_text,
                className='flex-fill overflow-auto border border-primary'
            ),
        ], className='d-flex flex-column h-100 border-end border-secondary mb-2 p-2', style={'width': 330}),
    ], id='drawer-div', className='d-flex justify-content-end', style={'transition': 'width 1s', 'width': 330}),

    # Controls collapse button
    html.Div([
        dmc.ActionIcon(
            DashIconify(id='collapse-drawer-btn-icon', icon='mdi:chevron-double-left', width=25),
            id="collapse-drawer-btn",
            radius='xl', variant="outline", color='var(--bs-secondary)', bg='var(--bs-body-bg)',
        )],
        className='d-flex justify-content-center pt-4 overflow-visible', style={'width': 0}
    ),

    # Main container
    html.Div([
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
    ], className='flex-fill d-flex flex-column gap-2 p-2 ms-2')

], className='flex-fill d-flex')


@callback(
    Output("collapse-drawer-btn-icon", "flip"),
    Output("drawer-div", "style"),
    Input("collapse-drawer-btn", "n_clicks"),
    prevent_initial_call=True
)
def collapse_controls(n_clicks):
    return (
        "horizontal" if n_clicks % 2 else None,
        {'transition': 'width 1s', 'width': 0 if n_clicks % 2 else 330}
    )


@callback(
    Output("genre-graph-card-header", "children"),
    Input("feature-dropdown", "value"),
)
def update_genre_card_header(genre):
    return f"Mean and Standard Deviation of {genre} by Track Genre"


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
        path="/W34",
        name="W34",  # used as label for the main app navlink
        title="Spotify Tracks Exploration",
        description='Here, we explore various parameters of songs, such as genre, danceability, tempo, '
                    'and other relevant musical attributes. of approximately 90,000 Spotify tracks.',
        image="assets/W34.jpg",  # used by the tooltip for the main app navbar
        data_source='*Data Source: '
                    '[Spotify Tracks Dataset]'
                    '(https://www.kaggle.com/datasets/maharshipandya/-spotify-tracks-dataset/data), '
                    'by MaharshiPandya*',
        disabled=False,
    )
    layout = html.Div([
        layout_W34
    ], className='h-100 d-flex')
