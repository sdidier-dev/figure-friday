from dash import html, Input, Output, dcc, callback, State, Patch, no_update
from dash_bootstrap_templates import ThemeChangerAIO, template_from_url
from datetime import timedelta, datetime, date
import dash_mantine_components as dmc
import plotly.graph_objects as go
import pandas as pd

from ..config_W41 import df, to_ms, transports

# dff = df.assign(
#     year=df['Date'].apply(lambda date: str(datetime.strptime(date, '%m/%d/%Y').year)),
#     month=df['Date'].apply(lambda date: str(datetime.strptime(date, '%m/%d/%Y').month)),
#     week=df['Date'].apply(lambda date: str(datetime.strptime(date, '%m/%d/%Y').isocalendar().week)),
#     weekday=df['Date'].apply(lambda date: datetime.strptime(date, '%m/%d/%Y').weekday()),
# )

# dff = df[['Date', 'Subways']].assign(
#     **{'Subways_pre': (df['Subways'] * 100 / df['Subways%'])}
#     # Subways_pre=df['Subways'] * 100 / df['Subways%']
# )
#
# # dff = dff.groupby(pd.Grouper(key='Date', freq='MS')).sum().reset_index()
# dff['Subways_diff%'] = dff['Subways'] / dff['Subways_pre'] - 1
#
# # dff = pd.DataFrame(df['Date'])
# # for t in transports:
# #     dff[t + '_diff'] = df[t + '%'] - 100
#
# fig = go.Figure()
#
# # dff_neg = dff[dff['Subways_diff%'] < 0]
# fig.add_bar(
#     x=dff['Date'],
#     y=dff['Subways_diff%'],
#     # marker_color='red',
#     # name='expenses'
# )
#
# # dff_pos = dff[dff['Subways_diff%'] >= 0]
# # fig.add_bar(
# #     x=dff_pos['Date'],
# #     y=dff_pos['Subways_diff%'],
# #     marker_color='green',
# #     name='revenue'
# # )
#
# fig.update_layout(
#     # showlegend=False,
#     bargap=0,
#     bargroupgap=0,
#     # hovermode='x unified',
#     # barmode='group' if unstack else 'stack',
#     # yaxis_title_text='Ridership',
#     # margin={'autoexpand': True, "r": 5, "t": 0, "l": 0, "b": 5},
#     # template=f"{template_from_url(theme)}{'' if switch_on else '_dark'}",
# )

MTA_pre_pandemic_bar = html.Div([
    dcc.Graph(
        id='MTA-pre-pandemic-graph',
        responsive=True,
        config={'displayModeBar': False},
        className='h-100 flex-fill',
        # figure=fig
    )
], className='h-100 flex-fill d-flex flex-column gap-2')


# Note: can't use a Patch() while modifying the theme, the fig must be fully regenerated
@callback(
    Output('MTA-pre-pandemic-graph', 'figure'),
    Input(ThemeChangerAIO.ids.radio("theme"), "value"),
    Input("color-mode-switch", "checked"),
)
def update_theme_pre_pandemic_bar(theme, switch_on):
    dff = df.assign(
        **{t+'_pre': (df[t] * 100 / df[t+'%']) for t in transports}
    )
    dff = dff.groupby(pd.Grouper(key='Date', freq='MS')).sum().reset_index()

    dff['Subways_diff%'] = dff['Subways'] / dff['Subways_pre'] - 1

    fig = go.Figure()

    fig.add_bar(
        x=dff['Date'],
        y=dff['Subways_diff%'],
        # marker_color='red',
        # name='expenses'
    )

    fig.update_layout(
        showlegend=False,
        bargap=0,
        bargroupgap=0,
        # hovermode='x unified',
        # barmode='group' if unstack else 'stack',
        # yaxis_title_text='Ridership',
        margin={'autoexpand': True, "r": 5, "t": 0, "l": 0, "b": 5},
        template=f"{template_from_url(theme)}{'' if switch_on else '_dark'}",
    )
    return fig

# @callback(
#     Output('MTA-aggregate-graph', 'figure', allow_duplicate=True),
#     Input('MTA-aggregate-unstack-chk', 'checked'),
#     prevent_initial_call=True,
# )
# def update_bar_stack(unstack):
#     patched_figure = Patch()
#     patched_figure["layout"]["barmode"] = 'group' if unstack else 'stack'
#     return patched_figure


# months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
#           'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
#
# y1 = [20, 14, 25, 16, 18, 22, 19, 15, 12, 16, 14, 17]
# y2 = [19, 14, 22, 14, 16, 19, 15, 14, 10, 12, 12, 16]
#
# fig = go.Figure()
#
# fig.add_trace(go.Bar(
#     x=months,
#     y=[y + 5 for y in y1],
#     offsetgroup="1"
#
# ))
# fig.add_trace(go.Bar(
#     x=months,
#     y=[y + 5 for y in y2],
#     offsetgroup="2"
#
# ))
# fig.add_trace(go.Bar(
#     x=months,
#     y=y1,
#     offsetgroup="1"
# ))
# fig.add_trace(go.Bar(
#     x=months,
#     y=y2,
#     offsetgroup="2"
#
# ))