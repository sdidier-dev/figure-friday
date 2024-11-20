import random

from dash import dcc, Input, Output, callback
from dash_bootstrap_templates import ThemeChangerAIO, template_from_url
import plotly.graph_objects as go
import networkx as nx

home_background_graph = dcc.Graph(
    id='home-graph',
    responsive=True,
    config={'displayModeBar': False},
    className='position-fixed z-n1 w-100 h-100',
    style={
        'background':
            'radial-gradient(ellipse 100% 50% at bottom left, '
            'var(--bs-light-bg-subtle), rgb(0 0 0 / 0%) 75%), '
            'radial-gradient(ellipse 85% 50% at 75% 50%, '
            'var(--bs-light-bg-subtle),var(--bs-light-bg-subtle) 15%, var(--bs-dark-bg-subtle) 50%)'
    }
)


@callback(
    Output('home-graph', 'figure'),
    Input(ThemeChangerAIO.ids.radio("theme"), "value"),
    Input("color-mode-switch", "checked"),
)
def update_home_graph(theme, switch_on):
    fig = go.Figure()

    # start with the layout to fetch the primary color of the template to apply it on the figures
    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis_visible=False, yaxis_visible=False,
        xaxis_range=[0.2, 2.5], yaxis_range=[-5, 2.5],
        showlegend=False,
        template=f"{template_from_url(theme)}{'' if switch_on else '_dark'}",
    )
    primary_color = fig['layout']['template']['layout']['colorway'][0]

    # generate a random network
    n = 200
    pos = {i: (abs(random.gauss()), random.gauss()) for i in range(n)}
    G = nx.soft_random_geometric_graph(n, 0.5, pos=pos, p_dist=lambda x: 0.15)

    # markers
    nodes_x, nodes_y = [], []
    for node in G.nodes:
        x, y = G.nodes[node]['pos']
        nodes_x.append(x)
        nodes_y.append(y)

    # add extra markers
    n2 = 50
    nodes_x += [abs(random.gauss()) for _ in range(n2)]
    nodes_y += [random.gauss() - 3 for _ in range(n2)]

    fig.add_scatter(
        mode='markers',
        x=nodes_x, y=nodes_y,
        marker_size=random.choices([3, 4, 5, 6, 7, 8, 9], k=n + n2),
        hoverinfo='skip'
    )

    # lines
    edges_x, edges_y = [], []
    for edge in G.edges:
        x0, y0 = G.nodes[edge[0]]['pos']
        x1, y1 = G.nodes[edge[1]]['pos']
        edges_x += [x0, x1, None]
        edges_y += [y0, y1, None]

    fig.add_scatter(
        mode='lines',
        x=edges_x, y=edges_y,
        opacity=0.3,
        line={'width': 1, 'color': primary_color},
        hoverinfo='skip'
    )

    return fig
