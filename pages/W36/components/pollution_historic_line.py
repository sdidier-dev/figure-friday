import json
from pprint import pprint

import numpy as np
from dash_bootstrap_templates import ThemeChangerAIO, template_from_url
from dash import dcc, html, Input, Output, callback, no_update, State, ctx
import dash_mantine_components as dmc
import plotly.graph_objects as go
import pandas as pd

from pages.W36.config import df, pollution_levels

min_data = {'cities': df.idxmin(axis='columns').to_list(), 'val': df.min(axis='columns').to_list()}
max_data = {'cities': df.idxmax(axis='columns').to_list(), 'val': df.max(axis='columns').to_list()}

pollution_historic_line = html.Div([
    dmc.MultiSelect(
        id='pollution-historic-line-multiSelect',
        data=df.columns,
        value=['Paris, France', 'Moscow, Russia'],
        placeholder="Select the Cities (can also be selected by clicking on the upper views 👆)",
        hidePickedOptions=True,
        searchable=True,
        nothingFoundMessage="Nothing Found!",
    ),
    html.Div([
        'Show:',
        dmc.Tooltip(
            label="Minima and Maxima Values though each Year",
            position="bottom", withArrow=True,
            children=dmc.Checkbox(
                id="pollution-historic-line-extremes-chk",
                label="Extreme Values", checked=True, color='var(--bs-primary)')
        ),
        dmc.Tooltip(
            label="Ranges of the Pollution Levels",
            position="bottom", withArrow=True,
            children=dmc.Checkbox(
                id="pollution-historic-line-levels-chk",
                label="Pollution Level Zones", checked=True, color='var(--bs-primary)')
        ),
        dmc.Tooltip(
            label="Percentage in each Pollution Level of the Selected Cities Together",
            position="bottom", withArrow=True,
            children=dmc.Checkbox(
                id="pollution-historic-percent-levels-chk",
                label="Percentages in each Level", checked=True, color='var(--bs-primary)')
        ),
        dmc.Tooltip(
            label="All Cities Displayed in the Background",
            position="bottom", withArrow=True,
            children=dmc.Checkbox(
                id="pollution-historic-line-shadows-chk",
                label="Countries' Shadows", color='var(--bs-primary)')
        ),
    ], className='d-flex align-items-center gap-4'),

    dcc.Graph(
        id='pollution-historic-line-graph',
        responsive=True,
        config={'displayModeBar': False},
        style={'min-width': 300, 'min-height': 300},
        className='h-100 flex-fill'
    )
], className='h-100 flex-fill d-flex flex-column gap-2')


@callback(
    Output('pollution-historic-line-multiSelect', 'value'),
    Input('pollution-map-graph', 'clickData'),
    Input('pollution-top-bar-graph', 'clickData'),
    State('pollution-historic-line-multiSelect', 'value'),
)
def add_clicked_cities(click_data_map, click_data_bar, selected_cities):
    if ctx.triggered_id == 'pollution-map-graph':
        if click_data_map and click_data_map['points'][0]['customdata'][0] not in selected_cities:
            selected_cities.append(click_data_map['points'][0]['customdata'][0])
    elif click_data_bar and click_data_bar['points'][0]['y'] not in selected_cities:
        selected_cities.append(click_data_bar['points'][0]['y'])
    return selected_cities


@callback(
    Output('pollution-historic-line-graph', 'figure'),
    Input('pollution-historic-line-multiSelect', "value"),
    Input('pollution-historic-line-extremes-chk', "checked"),
    Input('pollution-historic-line-levels-chk', "checked"),
    Input('pollution-historic-percent-levels-chk', "checked"),
    Input('pollution-historic-line-shadows-chk', "checked"),
    Input(ThemeChangerAIO.ids.radio("theme"), "value"),
    Input("color-mode-switch", "checked"),
)
def update_pollution_bar(selected_cities, show_extremes, show_levels, show_pencent, show_shadows, theme, switch_on):
    fig = go.Figure()
    range_max = 0  # to set the Y axis range depending on the displayed data

    # main plots
    for city in selected_cities:
        range_max = max(range_max, df[city].max())
        fig.add_scatter(
            name=city,
            x=df.index, y=df[city],
            line_shape='spline',
            hovertemplate='%{y:.2f}',
            zorder=3
        )

    if show_extremes:
        range_max = max(max_data['val'])
        fig.add_scatter(
            name='Min',
            x=df.index, y=min_data['val'],
            line={'color': 'green', 'dash': 'dot', 'shape': 'spline'},
            customdata=min_data['cities'],
            hovertemplate='%{y:.2f}<extra><b>%{fullData.name}</b> - %{customdata}</extra>',
            zorder=2,
        )
        fig.add_scatter(
            name='Max',
            x=df.index, y=max_data['val'],
            line={'color': 'red', 'dash': 'dot', 'shape': 'spline'},
            customdata=max_data['cities'],
            hovertemplate='%{y:.2f}<extra><b>%{fullData.name}</b> - %{customdata}</extra>',
            zorder=2
        )

    if show_shadows:
        range_max = max(max_data['val'])
        for city in df.columns:
            if city not in selected_cities:
                fig.add_scatter(
                    x=df.index, y=df[city],
                    line_color='rgba(150,150,150,0.5)',
                    # line_color='LightGrey' if switch_on else 'DarkSlateGrey',
                    line_shape='spline',
                    hoverinfo="skip",
                    showlegend=False,
                    zorder=1
                )

    # add a margin to the y max range (also used to position the 'very Unhealthy' label
    range_max += 10

    # add zone labels and zone areas
    if show_levels or show_pencent:
        for level, level_params in pollution_levels.items():
            if level != 'Hazardous':
                # get the upper bound
                val_max = level_params['max'] if level != 'Very Unhealthy' else range_max

                # add zones only if selected
                if show_levels:
                    fig.add_hrect(
                        y0=level_params['min'], y1=val_max,
                        line_width=0,
                        fillcolor=level_params['color'],
                        opacity=0.3,
                        layer="below",
                    )

                # add zones labels
                fig.add_annotation(
                    xref="paper",
                    x=1, y=(val_max + level_params['min']) / 2,
                    align="right",
                    text=level if level != 'Unhealthy for Sensitive Groups' else 'Unhealthy for<br>Sensitive Groups',
                    font_color=level_params['color'],
                    font_weight=700,
                    showarrow=False,
                )

    # add percentage
    if show_pencent:
        # make buckets of years in each level per cities
        bins = [v['min'] for v in pollution_levels.values()]
        labels = list(pollution_levels.keys())[:-1]  # remove 'Hazardous'
        # buckets dataframe
        df_levels = pd.DataFrame()
        for city in selected_cities:
            df_levels = pd.concat([
                df_levels,
                df.groupby(pd.cut(df[city], bins=bins, labels=labels), observed=True).size()
            ], axis='columns')

        # get the sum for each level through all selected cities
        df_levels['sum'] = df_levels.sum(axis=1)
        total = df_levels['sum'].sum()

        # add percentage areas with labels
        for level, value in zip(df_levels['sum'].index, df_levels['sum'].to_numpy()):
            percent = value / total
            fig.add_shape(
                type="rect",
                xref="paper", x0=0, x1=percent,
                y0=pollution_levels[level]['min'],
                y1=pollution_levels[level]['max'] if level != 'Very Unhealthy' else range_max,
                line_width=0,
                fillcolor=pollution_levels[level]['color'],
                opacity=0.2,
                label={'text': percent, 'font_color': pollution_levels[level]['color'], 'texttemplate': '%{x1:.1%}'},
                layer="below",
            )

    fig.update_layout(
        legend={'orientation': 'h', 'y': -0.05},
        xaxis_showgrid=False,

        yaxis_showgrid=False,
        yaxis_range=[0, range_max],
        yaxis_title_text='PM2.5 Concentration (µg/m³)',
        margin={'autoexpand': True, "r": 0, "t": 0, "l": 0, "b": 0},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        hovermode='x',
        template=f"{template_from_url(theme)}{'' if switch_on else '_dark'}",
    )

    return fig
