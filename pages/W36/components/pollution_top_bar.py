from dash_bootstrap_templates import ThemeChangerAIO, template_from_url
from dash import dcc, Input, Output, callback
import plotly.graph_objects as go
import pandas as pd

from ..config import df_cities

pollution_top_bar_graph = dcc.Graph(
    id='pollution-top-bar-graph',
    responsive=True,
    config={'displayModeBar': False},
    style={'min-width': 300, 'min-height': 300},
    className='h-100 flex-fill'
)


@callback(
    Output('pollution-top-bar-graph', 'figure'),
    Input('year-pollution-slider', "value"),
    Input('pollution-top-less-bar-input', "value"),
    Input('pollution-top-most-bar-input', "value"),
    Input(ThemeChangerAIO.ids.radio("theme"), "value"),
    Input("color-mode-switch", "checked"),
)
def update_pollution_bar(year, top_less, top_most, theme, switch_on):
    dff_cities = pd.concat([df_cities.sort_values(year).head(top_less), df_cities.sort_values(year).tail(top_most)])

    fig = go.Figure()
    fig.add_bar(
        x=dff_cities[year], y=dff_cities.index,
        orientation='h',
        marker_color=dff_cities['color'],
        marker_opacity=0.5,
        text=dff_cities[year],
        texttemplate="%{text:.2f}",
        textfont_color=dff_cities['color'],
        hoverinfo="none",
    )
    fig.update_layout(
        xaxis_title_text='PM2.5 Concentration (µg/m³)',
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        template=f"{template_from_url(theme)}{'' if switch_on else '_dark'}",
    )
    return fig
