import numpy as np
from dash_bootstrap_templates import ThemeChangerAIO, template_from_url
from dash import dcc, html, Input, Output, callback
import dash_mantine_components as dmc
import plotly.graph_objects as go

from ..config import df_cities, pollution_levels


# internal function to wrap 'description' text for hover
def _add_line_breaks(text, max_length=50):
    if not isinstance(text, str):
        return ''
    new_text, length = text.split()[0], len(text.split()[0])
    for word in text.split()[1:]:
        if length + len(f' {word}') <= max_length:
            new_text += f' {word}'
            length += len(f' {word}')
        else:
            new_text += f'<br>{word}'
            length = 0
    return new_text


# internal function to get the pollution level from the PM2.5 value
def _get_level(val):
    for level, level_param in pollution_levels.items():
        if val <= level_param['max']:
            return level


pollution_map_graph = html.Div([
    html.Div([
        'Options:',
        dmc.Tooltip(
            label="The Size of the Marker is proportional to the Pollution Value and the Color is linked to the "
                  "Pollution Level Category",
            position="bottom", withArrow=True,
            children=dmc.Checkbox(
                id="pollution-map-markers-chk",
                label="Labels", checked=True, color='var(--bs-primary)')
        ),
        dmc.Tooltip(
            label="The Labels show the Evolution of the Pollution Value compare to the Previous Year",
            position="bottom", withArrow=True,
            children=dmc.Checkbox(
                id="pollution-map-labels-chk",
                label="Labels", checked=True, color='var(--bs-primary)')
        ),
    ], className='d-flex gap-4'),
    dcc.Graph(
        id='pollution-map-graph',
        responsive=True,
        config={'displayModeBar': False},
        style={'min-width': 300, 'min-height': 300},
        className='h-100 flex-fill'
    )
], className='h-100 flex-fill d-flex flex-column gap-2')


@callback(
    Output('pollution-map-graph', 'figure'),
    Input('year-pollution-slider', "value"),
    Input('pollution-map-labels-chk', "checked"),
    Input("pollution-map-markers-chk", "checked"),
    Input(ThemeChangerAIO.ids.radio("theme"), "value"),
    Input("color-mode-switch", "checked")
)
def update_pollution_map(year, show_labels, show_markers, theme, switch_on):
    # add cols depending on year to the global df_cities that will also be used by top_bar graph
    df_cities['level'] = df_cities[year].apply(lambda row: _get_level(row))
    df_cities['description'] = df_cities['level'].apply(
        lambda row: _add_line_breaks(pollution_levels[row]['description']))
    df_cities['color'] = df_cities['level'].apply(lambda row: pollution_levels[row]['color'])
    df_cities['delta'] = (df_cities[year].to_numpy() - df_cities[year - 1].to_numpy()
                          ).round(2) if year != 1850 else np.nan

    fig = go.Figure()

    # add one trace by pollution level
    if show_markers:
        for level, level_param in pollution_levels.items():
            dff_cities = df_cities[df_cities['level'] == level]
            fig.add_scattermap(
                name=level,
                lat=dff_cities['lat'], lon=dff_cities['lon'],
                marker_size=dff_cities[year].apply(lambda row: max(row // 1.5, 7)),
                marker_color=level_param['color'],
                customdata=list(zip(dff_cities.index, dff_cities[year], dff_cities['delta'], dff_cities['level'],
                                    dff_cities['description'])),
                hovertemplate='<b>%{customdata[0]}</b><br><br>'
                              'Annual Mean PM2.5 Concentration: <b>%{customdata[1]:.2f} µg/m³</b><br>'
                              'Compare to the previous year: '
                              f"<b>{'%{customdata[2]:+}' if year != 1850 else 'Nan'} µg/m³</b><br><br>"
                              'Pollution Level: <b>%{customdata[3]}</b><br>'
                              '<i>%{customdata[4]}</i><br>'
                              '<extra></extra>',
            )

    # add 2 additional traces for the labels as it is not currently possible to provide a list to scattermap text params
    # to customize labels individually
    if show_labels and year != 1850:
        for trace in ['+', '-']:
            dff_cities = df_cities[df_cities['delta'] > 0] if trace == '+' else df_cities[df_cities['delta'] <= 0]
            textfont_color = 'red' if trace == '+' else ('green' if switch_on else 'lime')

            fig.add_scattermap(
                lat=dff_cities['lat'], lon=dff_cities['lon'],
                mode='text',
                text=dff_cities['delta'], texttemplate='%{text:+}', textfont={'color': textfont_color, 'weight': 700},
                hoverinfo="none",
                customdata=list(zip(dff_cities.index, dff_cities[year], dff_cities['delta'], dff_cities['level'],
                                    dff_cities['description'])),
                hovertemplate='<b>%{customdata[0]}</b><br><br>'
                              'Annual Mean PM2.5 Concentration: <b>%{customdata[1]:.2f} µg/m³</b><br>'
                              'Compare to the previous year: '
                              f"<b>{'%{customdata[2]:+}' if year != 1850 else 'Nan'} µg/m³</b><br><br>"
                              'Pollution Level: <b>%{customdata[3]}</b><br>'
                              '<i>%{customdata[4]}</i><br>'
                              '<extra></extra>' if show_markers else '',
                hoverlabel_bgcolor=dff_cities['color'],
                showlegend=False,
            )

    # add an empty map if no markers nor labels
    if not show_markers and (not show_labels or year == 1850):
        fig.add_scattermap()

    fig.update_layout(
        legend={
            'title_text': 'Pollution Levels',
            'orientation': 'h', 'y': 0,
            'itemsizing': 'constant',
        },
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        map_style='carto-voyager-nolabels' if switch_on else 'carto-darkmatter-nolabels',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        template=f"{template_from_url(theme)}{'' if switch_on else '_dark'}",
    )

    return fig
