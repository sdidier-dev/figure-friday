from io import StringIO
from pprint import pprint

from dash import dcc, html, Input, Output, callback, no_update, State, ctx, Patch
from dash_bootstrap_templates import ThemeChangerAIO, template_from_url
import dash_mantine_components as dmc
import plotly.graph_objects as go
import pandas as pd
from dash_iconify import DashIconify

df = pd.read_csv(
    r'E:\Python\Projects\figure-friday\figure-friday\pages\W34\assets\spotify_dataset.csv',  # for dev
    # 'https://github.com/plotly/Figure-Friday/blob/main/2024/week-34/dataset.csv',
)

num_features = ['popularity', 'danceability', 'energy', 'speechiness', 'acousticness', 'instrumentalness', 'liveness',
                'valence', 'duration_ms', 'loudness', 'tempo']

genre_graph_controls = html.Div([
    html.Label("Select Feature"),
    dmc.Select(
        id="feature-dropdown",
        data=num_features,
        value="popularity",
        checkIconPosition='right',
        w=200,
        comboboxProps={'transitionProps': {'duration': 300, 'transition': 'scale-y'}},
    ),
    html.Label("Sort Mean", className='ms-3'),
    dmc.ActionIcon(
        DashIconify(id='sort-btn-icon', icon='mdi:chevron-down', width=25),
        id="sort-btn",
        variant="outline",
        color='var(--bs-primary)',
    ),
], className='d-flex align-items-center gap-2 mb-2')

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
        className='h-100'
    )
], className='h-100', style={'position': 'relative'})


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
