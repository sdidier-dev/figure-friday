from dash_bootstrap_templates import ThemeChangerAIO, template_from_url
from dash import dcc, html, Input, Output, callback, no_update
import dash_mantine_components as dmc
import plotly.graph_objects as go
import pandas as pd

dff_splits = [0, 100000, 1000000, 10000000, 100000000]

# internal function to wrap 'extract' text for hover
def _add_line_breaks(text, max_length=50):
    if not isinstance(text, str):
        return ''
    new_text, length = text.split()[0], len(text.split()[0])
    for word in text.split()[1:]:
        if length + len(' ' + word) <= max_length:
            new_text += ' ' + word
            length += len(' ' + word)
        else:
            new_text += '<br>' + word
            length = 0
    return new_text


people_map_graph = html.Div([
    html.Div([
        dmc.Checkbox(id="people-map-labels-chk", label="Hide Labels", color='var(--bs-primary)'),
        dmc.Checkbox(id="people-map-markers-chk", label="Hide Markers", color='var(--bs-primary)'),
    ], className='d-flex gap-4'),
    dcc.Graph(
        id='people-map-graph',
        responsive=True,
        style={'min-width': 500, 'min-height': 300},
        className='h-100 flex-fill'
    )
], className='h-100 flex-fill d-flex flex-column gap-2')


@callback(
    Output('people-map-graph', 'figure'),
    Input("people-grid", "virtualRowData"),
    Input('people-map-labels-chk', "checked"),
    Input("people-map-markers-chk", "checked"),
    Input(ThemeChangerAIO.ids.radio("theme"), "value"),
    Input("color-mode-switch", "checked")
)
def update_map(virtual_data, hide_labels, hide_markers, theme, switch_on):
    if not virtual_data:
        return no_update

    dff = pd.DataFrame(virtual_data)
    fig = go.Figure()

    # set the layout first to get the colors from the template for the colorbar
    fig.update_layout(
        legend_title_text='Total Views',
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        map={
            'center': {'lat': 40, 'lon': -115}, 'zoom': 2.8,
            'style': 'carto-voyager-nolabels' if switch_on else 'carto-darkmatter-nolabels'
        },
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        template=f"{template_from_url(theme)}{'' if switch_on else '_dark'}",
    )
    marker_color = fig['layout']['template']['layout']['colorway'][0]

    for i in range(len(dff_splits) - 1):
        dff_split = dff[(dff_splits[i] < dff['views_sum']) & (dff['views_sum'] <= dff_splits[i + 1])]

        # format  text to display on hover
        place, extract = [], []
        for index, row in dff_split.iterrows():
            text = ''
            if pd.notna(row['neighborhood']):
                text += row['neighborhood'] + '-'
            text += row['city']
            if pd.notna(row['state']):
                text += ', ' + row['state']
            place.append(text)
            extract.append(_add_line_breaks(row['extract']))

        mode = []
        if not hide_markers:
            mode.append('markers')
        if not hide_labels:
            mode.append('text')

        fig.add_scattermap(
            name=f"-{dff_splits[i + 1]:,}" if i != len(dff_splits) - 2 else f"+{dff_splits[i]:,}",
            lat=dff_split['lat'],
            lon=dff_split['lng'],
            customdata=list(zip(place, dff_split['views_sum'], extract)),

            mode='+'.join(mode) if mode else 'none',
            marker={'size': (i ** 2 + 1) * 2, 'opacity': 0.3, 'color': marker_color},
            text=dff_split["name_clean"],
            textfont_size=(i * 3 + 10), textfont_weight=700,
            hovertemplate='<b>%{text}</b><br>'
                          '<i>Formerly known as %{customdata[0]}</i><br><br>'
                          '<b>%{customdata[1]:,}</b> total views<br><br>'
                          '%{customdata[2]}'
                          '<extra></extra>',
        )
    return fig
