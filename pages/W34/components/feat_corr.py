from io import StringIO
from pprint import pprint

import numpy as np
from dash import dcc, html, Input, Output, callback, no_update
from dash_bootstrap_templates import ThemeChangerAIO, template_from_url, load_figure_template
import dash_mantine_components as dmc
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px
from dash_iconify import DashIconify

df = pd.read_csv(
    r'E:\Python\Projects\figure-friday\figure-friday\pages\W34\assets\spotify_dataset.csv',  # for dev
    # 'https://github.com/plotly/Figure-Friday/blob/main/2024/week-34/dataset.csv',
)

num_features = ['popularity', 'danceability', 'energy', 'speechiness', 'acousticness', 'instrumentalness', 'liveness',
                'valence', 'duration_ms', 'loudness', 'tempo']

heatmap_corr_graph = html.Div([
    dmc.Checkbox(
        id="heatmap-corr-chk",
        color='var(--bs-primary)',
        label="Show upper half matrix",
        labelPosition='left',
        styles={'label': {"font-size": 16}},
    ),
    dcc.Graph(
        id='heatmap-corr-graph',
        responsive=True,
        style={'min-width': 700, 'min-height': 300},
        className='h-100 flex-fill'
    )
], className='h-100 flex-fill d-flex flex-column gap-2')

detail_corr_graph = html.Div([
    html.Label("👈 Click on a value of the heatmap to see the details of the features pair correlation",
               className='ms-3'),
    html.Div([
        dmc.LoadingOverlay(
            id="detail-corr-graph-loading-overlay",
            visible=True,
            loaderProps={"type": "bars", "color": "var(--bs-primary)"},
            overlayProps={"radius": "sm", "blur": 2},
        ),
        dcc.Graph(
            id='detail-corr-graph',
            responsive=True,
            style={'min-width': 500, 'min-height': 300},
            className='h-100'
        )
    ], className='h-100 flex-fill', style={'position': 'relative'})
], className='h-100 flex-fill d-flex flex-column gap-2')


# makes the loader visible when reloading data
@callback(

    Output("detail-corr-graph-loading-overlay", "visible", allow_duplicate=True),
    Input('heatmap-corr-graph', 'clickData'),
    Input(ThemeChangerAIO.ids.radio("theme"), "value"),
    Input("color-mode-switch", "checked"),
    prevent_initial_call=True,
)
def reactivate_detail_corr_graph_loader(*_):
    return True


# Note: can't use a patch while modifying the theme, the fig must be fully regenerated
@callback(
    Output("heatmap-corr-graph", "figure"),
    Input("heatmap-corr-chk", "checked"),
    Input(ThemeChangerAIO.ids.radio("theme"), "value"),
    Input("color-mode-switch", "checked"),
)
def update_heatmap_corr(show_upper_half, theme, switch_on):
    corr_matrix = df[num_features].corr()

    if show_upper_half:
        mask = np.ones_like(corr_matrix, dtype=np.bool)
        np.fill_diagonal(mask, None)
    else:
        mask = np.tril(np.ones_like(corr_matrix, dtype=np.bool), k=-1)

    z = corr_matrix.where(mask).fillna('')

    fig = go.Figure()
    # set the layout first to get the colors from the template for the colorbar
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_showgrid=False,
        yaxis_showgrid=False,
        yaxis_autorange='reversed',
        margin={'autoexpand': True, "r": 0, "t": 0, "l": 0, "b": 0},
        template=f"{template_from_url(theme)}{'' if switch_on else '_dark'}",
    )
    positive_color = fig['layout']['template']['layout']['colorway'][0]
    negative_color = fig['layout']['template']['layout']['colorway'][1]
    zero_color = fig['layout']['template']['layout']['plot_bgcolor']
    fig.add_heatmap(
        x=z.columns, y=z.columns, z=z,
        colorscale=[(0, negative_color), (0.5, zero_color), (1, positive_color), ],
        xgap=1, ygap=1,
        text=z,
        texttemplate="%{text:.2f}",
        hovertemplate='<b>%{x}</b> vs <b>%{y}</b><br>Correlation: %{z:.2f}<extra></extra>',
        hoverongaps=False
    )
    return fig


@callback(
    Output('detail-corr-graph', 'figure'),
    Output("detail-corr-graph-loading-overlay", "visible"),
    Input('heatmap-corr-graph', 'clickData'),
    Input(ThemeChangerAIO.ids.radio("theme"), "value"),
    Input("color-mode-switch", "checked")
)
def display_click_data(click_data, theme, switch_on):
    x = click_data['points'][0]['x'] if click_data else 'energy'
    y = click_data['points'][0]['y'] if click_data else 'loudness'

    fig = px.scatter(
        df, x=x, y=y,
        marginal_x="histogram", marginal_y="histogram",
        trendline="ols", trendline_color_override='red',
        template=f"{template_from_url(theme)}{'' if switch_on else '_dark'}",
    )
    fig.update_traces(selector={'type': 'scatter'}, marker_size=2)
    fig.update_traces(selector={'type': 'scattergl'}, marker_size=2)

    # add an invisible shape line matching the trend line to add a label with the trend equation
    results = px.get_trendline_results(fig)
    const, slope = results["px_fit_results"].iloc[0].params
    x0, x1 = df[x].min(), df[x].max()
    y0, y1 = slope * x0 + const, slope * x1 + const
    fig.add_shape(
        type="line",
        x0=x0, y0=y0,
        x1=x1, y1=y1,
        line_width=0,
        label={'text': f"{slope:.2f}x{const:+.2f}",
               'font': {'size': 20, 'color': 'white', 'shadow': '2px 2px 5px black'}},
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_zeroline=False, yaxis_zeroline=False,
        xaxis_showgrid=False, yaxis_showgrid=False,
        xaxis2_showgrid=False, yaxis2_showgrid=False,
        xaxis3_showgrid=False, yaxis3_showgrid=False,
        margin={'autoexpand': True, "r": 0, "t": 0, "l": 0, "b": 0},
    )
    return fig, False
