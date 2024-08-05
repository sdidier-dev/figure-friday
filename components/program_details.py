import json
from io import StringIO
from pprint import pprint

from dash import Dash, dcc, html, Input, Output, State, callback, Patch, no_update
import dash_bootstrap_components as dbc
import dash_ag_grid as dag

import plotly.express as px
import plotly.graph_objects as go

import pandas as pd

fig = go.Figure()
fig.add_icicle(
    root_color="lightgrey",
    branchvalues='total',
    hoverinfo="skip",
    texttemplate="<b>%{label}</b><br>"
                 "Investments: %{value:$.4s} (%{percentRoot} of total)",
)
fig.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',

    margin={"r": 0, "t": 30, "l": 0, "b": 0},
)

graph_program_details = dcc.Graph(
    id='graph-program-details',
    figure=fig,
    config=dict(responsive=True),
    className='flex-fill'
)

levels = ['total', 'Program Area', 'Program', 'NAICS Industry Sector']
value_column = 'Investment Dollars'

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)


@callback(
    Output("graph-program-details", "figure"),
    Input("grid-data", "virtualRowData"),
    prevent_initial_call=True
)
def update_program_details(virtual_data):
    if virtual_data:
        dff = pd.DataFrame(virtual_data)

        # Trick adding a col 'total' used as root col
        dff['total'] = 'Total'
        data = {k: [] for k in ['ids', 'parents', 'labels', 'values']}

        for i in range(len(levels)):
            dfg = dff[[*levels[:i + 1], value_column]].groupby(levels[:i + 1]).sum().reset_index()
            dfg_dict = dfg.to_dict('list')
            # Ids concatenate values from root to level[i]
            data['ids'] += ['-'.join(ls) for ls in zip(*[dfg_dict[level] for level in levels[:i + 1]])]
            # Parent concatenate values from root to level[i-1] (must match the Ids !)
            data['parents'] += [
                '-'.join(ls) for ls in zip(*[dfg_dict[level] for level in levels[:i]])
            ] if i != 0 else ['']
            data['labels'] += dfg_dict[levels[i]]
            data['values'] += dfg_dict[value_column]

        patched_fig = Patch()
        patched_fig['data'][0]['ids'] = data['ids']
        patched_fig['data'][0]['parents'] = data['parents']
        patched_fig['data'][0]['labels'] = data['labels']
        patched_fig['data'][0]['values'] = data['values']
        return patched_fig
        # fig_program_details = go.Figure()
        # fig_program_details.add_icicle(
        #     ids=data['ids'],
        #     labels=data['labels'],
        #     parents=data['parents'],
        #     values=data['values'],
        #     root_color="lightgrey",
        #     branchvalues='total',
        #     # marker=dict(
        #     #     colors=data['color'],
        #     #     colorscale='RdBu',
        #     #     cmid=average_score
        #     # ),
        #     # hovertemplate='<b>%{label} </b> <br> Sales: %{value}<br> Success rate: %{color:.2f}',
        #     text=['cool'] * len(data['ids']),
        #     texttemplate="<b>%{label}</b><br>"
        #                  "Investments: %{value:$.4s} (%{percentRoot} of total)",
        #     # 'Program Area', 'Program', 'NAICS Industry Sector'
        #     # `currentPath`, `root`, `entry`, `percentRoot`, `percentEntry`, `percentParent`, `label` and `value`
        # )
        # pprint(fig_program_details['data'][0]['value'])
        # return fig_program_details
    return no_update
