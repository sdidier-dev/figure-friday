from dash_bootstrap_templates import ThemeChangerAIO, template_from_url
from dash import dcc, html, Input, Output, callback, State, Patch
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import plotly.graph_objects as go
import pandas as pd

df = pd.read_csv(
    # r'E:\Python\Projects\figure-friday\figure-friday\pages\W34\assets\spotify_dataset.csv',  # for dev
    'https://raw.githubusercontent.com/plotly/Figure-Friday/main/2024/week-34/dataset.csv',
)

md_text = """`acousticness`:  
A confidence measure ranging from 0.0 to 1.0 that indicates the **likelihood of a given track being
classified as acoustic**. A value of 1.0 should signify a high level of confidence that the track is indeed acoustic.

`danceability`:  
Describes how **suitable** a track is for **dancing** based on a combination of musical elements including
tempo, rhythm stability, beat strength, and overall regularity. A value of 0.0 is least danceable and 1.0 is
most danceable.

`duration_ms`:  
The **track length** in milliseconds.

`energy`:  
Is a measure from 0.0 to 1.0 and represents a **perceptual measure of intensity and activity**.
Typically, energetic tracks feel fast, loud, and noisy. For example, death metal has high energy, while a Bach prelude
scores low on the scale.

`instrumentalness`:  
Predicts whether a track **contains no vocals**. "Ooh" and "aah" sounds are treated as instrumental in
this context. Rap or spoken word tracks are clearly "vocal". The closer the instrumentalness value is to 1.0, the
greater likelihood the track contains no vocal content.

`liveness`:  
**Detects the presence of an audience in the recording**. Higher liveness values represent an increased
probability that the track was performed live. A value above 0.8 provides strong likelihood that the track is live.

`loudness`:  
The **overall loudness** of a track in decibels (dB).

`popularity`:  
**The popularity of a track is a value between 0 and 100**, with 100 being the most popular. The popularity
is **calculated by algorithm** and is based, in the most part, on the total number of plays the track has had and how recent
those plays are. Generally speaking, songs that are being played a lot now will have a higher popularity than songs that
were played a lot in the past. Duplicate tracks (e.g. the same track from a single and an album) are rated
independently. Artist and album popularity is derived mathematically from track popularity.

`speechiness`:  
Speechiness detects the **presence of spoken words** in a track. The more exclusively speech-like the
recording (e.g. talk show, audio book, poetry), the closer to 1.0 the attribute value. Values above 0.66 describe tracks
that are probably made entirely of spoken words. Values between 0.33 and 0.66 describe tracks that may contain both
music and speech, either in sections or layered, including such cases as rap music. Values below 0.33 most likely
represent music and other non-speech-like tracks.

`tempo`:  
The **overall estimated tempo** of a track in beats per minute (BPM). In musical terminology, tempo is the speed
or pace of a given piece and derives directly from the average beat duration.

`valence`:  
A measure from 0.0 to 1.0 describing the **musical positiveness** conveyed by a track. Tracks with high valence
sound more positive (e.g. happy, cheerful, euphoric), while tracks with low valence sound more negative (e.g. sad,
depressed, angry).
"""

num_features = ['acousticness', 'danceability', 'duration_ms', 'energy', 'instrumentalness', 'liveness', 'loudness',
                'popularity', 'speechiness', 'tempo', 'valence']

genre_graph_controls = html.Div([
    dmc.Drawer(
        dcc.Markdown(md_text),
        id="features-description-drawer",
        title="Features Description",
        styles={
            'title': {'flex': 1, 'text-align': 'center', 'font-size': 20, 'font-weight': 700},
            'header': {'display': 'flex', 'border-bottom': '2px solid var(--bs-secondary)'}
        },
        zIndex=10000,
    ),
    html.Label("Select Feature"),
    dmc.ActionIcon(
        DashIconify(icon='clarity:info-line', width=25),
        id="features-description-btn",
        variant="transparent", color='var(--bs-primary)',
    ),
    dmc.Select(
        id="feature-dropdown",
        data=num_features,
        value="popularity",
        checkIconPosition='right',
        w=200,
        comboboxProps={'transitionProps': {'duration': 300, 'transition': 'scale-y'}},
    ),
    html.Label("Sort Mean", className='ms-3 me-2'),
    dmc.ActionIcon(
        DashIconify(id='sort-btn-icon', icon='mdi:chevron-down', width=25),
        id="sort-btn",
        variant="outline", color='var(--bs-primary)',
    ),
], className='d-flex align-items-center mb-2')

genre_graph = html.Div([
    dmc.LoadingOverlay(
        id="genre-graph-loading-overlay",
        visible=True,
        loaderProps={"type": "bars", "color": "var(--bs-primary)"},
        overlayProps={"radius": "sm", "blur": 2},
    ),
    dcc.Graph(
        id='genre-graph',
        responsive=True,
        config={'displayModeBar': False},
        className='h-100'
    )
], className='h-100', style={'position': 'relative'})


# also used in the Track Features Correlation card
@callback(
    Output("features-description-drawer", "opened"),
    Input("features-description-btn", "n_clicks"),
    Input("features-description-btn2", "n_clicks"),
    prevent_initial_call=True,
)
def open_features_description_drawer(*_):
    return True


# makes the loader visible when reloading data
@callback(
    Output("genre-graph-loading-overlay", "visible", allow_duplicate=True),
    Input("feature-dropdown", "value"),
    Input(ThemeChangerAIO.ids.radio("theme"), "value"),
    Input("color-mode-switch", "checked"),
    prevent_initial_call=True,
)
def reactivate_genre_graph_loader(*_):
    return True


@callback(
    Output("sort-btn-icon", "icon"),
    Output("genre-graph", "figure", allow_duplicate=True),
    Input("sort-btn", "n_clicks"),
    State("sort-btn-icon", "icon"),
    prevent_initial_call=True
)
def update_sort(_, current_icon):
    icon = 'up' if current_icon == 'mdi:chevron-down' else 'up-down' if current_icon == 'mdi:chevron-up' else 'down'
    xaxis_categoryorder = (
        'total ascending' if icon == 'up' else
        'total descending' if icon == 'down' else
        None
    )
    patched_fig = Patch()
    patched_fig['layout']['xaxis']['categoryorder'] = xaxis_categoryorder
    return f"mdi:chevron-{icon}", patched_fig


@callback(
    Output("genre-graph", "figure", allow_duplicate=True),
    Output("genre-graph-loading-overlay", "visible", allow_duplicate=True),
    Input('feature-dropdown', "value"),
    prevent_initial_call=True
)
def update_genre_fig_data(feat):
    data = [{
        'mean': df[(df['track_genre'] == cat)][feat].mean(),
        'std': df[(df['track_genre'] == cat)][feat].std()
    } for cat in df['track_genre'].unique()]

    patched_fig = Patch()
    patched_fig['data'][0]['y'] = [d['mean'] for d in data]
    patched_fig['data'][0]['error_y'] = {'type': 'data', 'array': [d['std'] for d in data]}
    return patched_fig, False


# Note: can't use a patch while modifying the theme, the fig must be fully regenerated
# This callback is also used to init the fig
@callback(
    Output("genre-graph", "figure"),
    Output("genre-graph-loading-overlay", "visible"),
    Input(ThemeChangerAIO.ids.radio("theme"), "value"),
    Input("color-mode-switch", "checked"),
    State('feature-dropdown', "value"),
    State("sort-btn-icon", "icon"),
)
def update_genre_fig_template(theme, switch_on, feat, sort_icon):
    data = [{
        'cat': cat,
        'mean': df[(df['track_genre'] == cat)][feat].mean(),
        'std': df[(df['track_genre'] == cat)][feat].std()
    } for cat in df['track_genre'].unique()]

    xaxis_categoryorder = (
        'total ascending' if sort_icon == 'mdi:chevron-up' else
        'total descending' if sort_icon == 'mdi:chevron-down' else
        None
    )

    fig = go.Figure()
    fig.add_scatter(
        x=[d['cat'] for d in data],
        y=[d['mean'] for d in data],
        error_y={'type': 'data', 'array': [d['std'] for d in data]},
        mode='markers',
        hovertemplate='<b>%{x}</b><br>Mean: %{y:.2f}<br>Standard Deviation: ±%{error_y.array:.2f}<extra></extra>',
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_categoryorder=xaxis_categoryorder,
        xaxis_autorange=False,
        xaxis_range=[-1, len(df['track_genre'].unique()) + 1],
        xaxis_showgrid=False,
        yaxis_gridcolor="grey",
        yaxis_zerolinecolor="grey",
        margin={'autoexpand': True, 'l': 0, 'r': 0, 't': 0, 'b': 150},
        template=f"{template_from_url(theme)}{'' if switch_on else '_dark'}",
    )
    # Note: False is to hide the loader when the fig is ready
    return fig, False
