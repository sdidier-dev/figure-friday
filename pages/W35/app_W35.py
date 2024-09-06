from pprint import pprint

from dash_bootstrap_templates import ThemeChangerAIO, template_from_url
from dash import Dash, html, dcc, Input, Output, register_page, clientside_callback, _dash_renderer, callback, \
    no_update, State
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd

df = pd.read_csv(
    r'E:\Python\Projects\figure-friday\figure-friday\pages\W35\assets\people-map.csv',  # for dev
    # 'https://raw.githubusercontent.com/plotly/Figure-Friday/main/2024/week-35/people-map.csv',
)
df.dropna(subset=['views_sum'], inplace=True)


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


df_splits = [0, 100000, 1000000, 10000000, 100000000]

fig = go.Figure()
for i in range(len(df_splits) - 1):
    dff = df[(df_splits[i] < df['views_sum']) & (df['views_sum'] <= df_splits[i + 1])]

    place, extract = [], []
    for index, row in dff.iterrows():
        text = ''
        if pd.notna(row['neighborhood']):
            text += row['neighborhood'] + '-'
        text += row['city']
        if pd.notna(row['state']):
            text += ', ' + row['state']
        place.append(text)
        extract.append(_add_line_breaks(row['extract']))

    fig.add_scattermap(
        name=f"-{df_splits[i + 1]:,}" if df_splits[i] == 0 else f"+{df_splits[i]:,}",
        lat=dff['lat'],
        lon=dff['lng'],
        customdata=list(zip(place, dff['views_sum'], extract)),

        mode='markers+text',
        marker_size=(i ** 2 + 1) * 2,
        marker_opacity=0.3,
        marker_color='blue',
        text=dff["name_clean"],
        textfont_size=(i * 3 + 10),
        hovertemplate='<b>%{text}</b><br>'
                      '<i>Formerly %{customdata[0]}</i><br><br>'
                      '<b>%{customdata[1]:,}</b> total views<br><br>'
                      '%{customdata[2]}'
                      '<extra></extra>',
    )

fig.update_layout(
    legend_title_text='Total Views',
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    map={
        'center': {'lat': 40, 'lon': -115},
        'zoom': 2.8,
        'style': 'carto-voyager-nolabels'
        # 'style':basic, carto-darkmatter, carto-darkmatter-nolabels, carto-positron, carto-positron-nolabels,
        # carto-voyager, carto-voyager-nolabels, dark, light, open-street-map, outdoors, satellite, satellite-streets,
        # streets, white-bg
    },

)

layout_W35 = html.Div([
    dcc.Graph(
        id='people-map-graph',
        figure=fig,
        responsive=True,
        style={'min-width': 500, 'min-height': 300},
        className='h-100 flex-fill'
    ),

    # dbc.Card([
    #     dbc.CardHeader(id='genre-graph-card-header', className='fs-5 text-body text-center'),
    #     dbc.CardBody([
    #         genre_graph_controls,
    #         genre_graph
    #     ], className='p-2'),
    # ], className='h-50', style={'min-width': 700, 'min-height': 300}),

    # dbc.Card([
    #     dbc.CardHeader("Track Features Correlation", className='fs-5 text-body text-center'),
    #     dbc.CardBody([
    #         heatmap_corr_graph,
    #         detail_corr_graph,
    #     ], className='d-flex flex-wrap overflow-auto gap-2 p-2'),
    # ], className='h-50'),

], className='flex-fill d-flex flex-column gap-2 p-2 overflow-auto')

# @callback(
#     Output('people-map-graph', 'id'),
#     Input('people-map-graph', 'relayoutData'),
# )
# def display_relayout_data(relayout_data):
#     pprint(relayout_data)
#     return no_update


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
            layout_W35
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
        path="/W35",
        name="W35",  # used as label for the main app navlink
        title="People Map of the US",
        description='What if we replace the names of US cities by the name of their most Wikipedia’ed resident '
                    '(from July 2015 through May 2019): people born in, lived in, or connected to a place?',
        # image="assets/W35.jpg",  # used by the tooltip for the main app navbar
        data_source='*Data Source: '
                    '[People Map](https://github.com/the-pudding/data/tree/master/people-map), '
                    'from [The Pudding](https://pudding.cool/)*',
        disabled=False,
    )
    layout = html.Div([
        layout_W35
    ], className='h-100 d-flex')
