from dash import html, Input, Output, dcc, callback, State, Patch, no_update
from dash_bootstrap_templates import ThemeChangerAIO, template_from_url
from datetime import timedelta, datetime, date
import dash_mantine_components as dmc
import plotly.graph_objects as go
import pandas as pd

from ..config_W41 import df, to_ms, transports

MTA_aggregate_histogram = html.Div([
    html.Label("Select Transportations:", className='mb-2'),
    html.Div([
        dmc.ChipGroup(
            id="MTA-aggregate-chipgroup",
            multiple=True,
            children=[dmc.Chip(transport, value=transport) for transport in transports],
            value=['Subways'],
        ),
    ], className='d-flex gap-2'),

    html.Div([
        html.Label("Options:"),
        dmc.Checkbox(id="MTA-aggregate-unstack-chk", label="Unstack Transportations Bars",
                     color='var(--bs-primary)'),
        dmc.Checkbox(id="MTA-aggregate-labels-chk", label="Show Labels", color='var(--bs-primary)'),
    ], className='d-flex gap-3 my-2'),

    dcc.Graph(
        id='MTA-aggregate-graph',
        responsive=True,
        config={'displayModeBar': False},
        className='h-100 flex-fill',
    )
], className='h-100 flex-fill d-flex flex-column gap-2')


def set_xticks(xrange):
    # find x_range
    start_datetime = datetime.fromisoformat(xrange[0])
    end_datetime = datetime.fromisoformat(xrange[1])
    range_timedelta = end_datetime - start_datetime

    # 5Y <= x_range
    if timedelta(days=365 * 5) <= range_timedelta:
        xticks = dict(dtick="M12", tickformat="%Y\n ", minor_dtick="M12")

    #  3Y <= x_range < 5Y
    elif timedelta(days=365 * 3) <= range_timedelta < timedelta(days=365 * 5):
        xticks = dict(dtick="M3", tickformat="Q%q\n%Y", minor_dtick="M12")

    #  6M <= x_range < 3Y
    elif timedelta(days=30 * 6) <= range_timedelta < timedelta(days=365 * 3):
        xticks = dict(dtick="M1", tickformat="%b\nQ%q '%y", minor_dtick="M3")

    #  30D <= x_range < 6M
    elif timedelta(days=30) <= range_timedelta < timedelta(days=30 * 6):
        xticks = dict(dtick=to_ms['W'], tickformat="S%U\n%b '%y", minor_dtick="M1")

    #  7D <= x_range < 4M
    elif timedelta(days=7) <= range_timedelta < timedelta(days=30):
        xticks = dict(dtick=to_ms['D'], tickformat="%e\nS%U %b '%y", minor_dtick=to_ms['W'])

    #  1D <= x_range < 7D
    elif timedelta(days=1) <= range_timedelta < timedelta(days=7):
        xticks = dict(dtick=12 * to_ms['H'], tickformat="%p\n%e. %b '%y", minor_dtick=to_ms['D'])

    #  x_range < 1D
    else:
        xticks = dict(dtick=to_ms['H'], tickformat="%H:%M\n%p</br>%e. %b '%y", minor_dtick=12 * to_ms['H'])

    return xticks


# Note: can't use a Patch() while modifying the theme, the fig must be fully regenerated
@callback(
    Output('MTA-aggregate-chipgroup', 'children'),
    Output('MTA-aggregate-graph', 'figure'),
    Input('MTA-aggregate-chipgroup', "value"),
    Input(ThemeChangerAIO.ids.radio("theme"), "value"),
    Input("color-mode-switch", "checked"),
    State('MTA-aggregate-sum-select', "value"),
    State('MTA-aggregate-mean-select', "value"),
    State('MTA-aggregate-unstack-chk', 'checked'),
    State('MTA-aggregate-labels-chk', 'checked'),
    State('MTA-aggregate-graph', 'figure'),
    State('MTA-aggregate-chipgroup', 'children'),
)
def update_theme_aggregate_histogram(transports, theme, switch_on, agg_sum, agg_mean, unstack, show_labels, fig, chips):
    # Save existing x range to re-apply it at the end
    xaxis_range = None
    if fig and isinstance(fig["layout"]["xaxis"]["range"][0], str):
        xaxis_range = fig["layout"]["xaxis"]["range"]

    fig = go.Figure()

    # set the layout first to get the theme colors
    fig.update_layout(
        showlegend=False,
        bargap=0.05,
        hovermode='x unified',
        barmode='group' if unstack else 'stack',
        yaxis_title_text='Ridership',
        margin={'autoexpand': True, "r": 5, "t": 0, "l": 0, "b": 5},
        template=f"{template_from_url(theme)}{'' if switch_on else '_dark'}",
    )

    # augment colorway if < n_transport adding brighter colors of the theme colorway
    theme_colorway = fig['layout']['template']['layout']['colorway']
    augmented_colorway = list(fig['layout']['template']['layout']['colorway'])
    while len(augmented_colorway) < len(chips):
        i = len(augmented_colorway) % len(theme_colorway)
        color = tuple((int(theme_colorway[i][j + 1:j + 3], 16) for j in (0, 2, 4)))  # convert color hex to rgb
        color = '#' + ''.join([f'{min(c + 50, 255):02X}' for c in color])  # make it brighter and convert back to hex
        augmented_colorway.append(color)

    # update the colors of the chips to match the augmented_colorway
    patched_chips = Patch()
    transport_colors = {}  # map the colors to the transports to apply to the fig
    for i, chip in enumerate(chips):
        transport_colors[chip['props']['value']] = augmented_colorway[i]
        patched_chips[i]["props"]["color"] = augmented_colorway[i]

    # dff = df.assign(**{t + '_pre': (df[t] * 100 / df[t + '%']) for t in transports})

    # Note for data processing:
    # First, sum the data by 'agg_sum', to have the total ridership by week/month/quarter...
    # Then the histogram will calculate the mean by 'bins_size' depending on 'agg_mean',
    # to have the mean by week/month/quarter...
    # Except if 'agg_sum'=='TOTAL', it will be calculated directly by the histogram

    # no need to sum the data for 'TOTAL' as it will be summed by the histogram using histfunc = "sum"
    # nor by day as the data is already by day
    dff = df.groupby(pd.Grouper(key='Date', freq=agg_sum)).sum().reset_index() if agg_sum not in ['TOTAL',
                                                                                                  'D'] else df.copy()
    histfunc = "avg" if agg_sum != 'TOTAL' else "sum"

    date_min = dff['Date'].min()
    date_max = dff['Date'].max()

    # as df.groupby() by week return the last day of the week, here we get the first day for the bins_start
    bins_start = (date_min.date() - timedelta(days=date_min.isoweekday() % 7)) if agg_mean == 'W' else date_min
    bins_end = date_max
    if agg_mean == 'ALL':
        bins_size = (bins_end - bins_start).days * to_ms['D']
    elif agg_mean in ['W', 'D']:
        bins_size = to_ms[agg_mean]
    else:
        bins_size = agg_mean

    for transport in transports:
        fig.add_histogram(

            name=transport,
            x=dff['Date'],
            y=dff[transport],
            histfunc=histfunc,
            autobinx=False,
            xbins=dict(start=bins_start, end=bins_end, size=bins_size),
            marker_color=transport_colors[transport],
            texttemplate="%{y:.4s}" if show_labels and agg_mean != 'D' else None,
            xhoverformat="%x",
            hovertemplate='%{y:.4s}',
        )


    # set title if aggregate all dataset
    title = None
    if agg_mean == 'ALL':
        start = datetime.strftime(date_min, "%m/%d/%Y")
        end = datetime.strftime(date_max, "%m/%d/%Y")
        title = f"OVERALL ({start} - {end})"

    # set the ticks depending on the range
    xticks = set_xticks(xaxis_range if xaxis_range else [date_min.isoformat(), date_max.isoformat()])

    fig.update_xaxes(
        title_text=title,
        color=fig['layout']['template']['layout']['font']['color'],
        range=xaxis_range,
        showticklabels=(agg_mean != 'ALL'),
        ticklabelmode="period",
        ticks="inside" if (agg_mean != 'ALL') else "",
        dtick=xticks["dtick"],
        tickformat=xticks["tickformat"],
        tickwidth=2,
        minor=dict(ticks="outside", dtick=xticks["minor_dtick"], tickwidth=2, ticklen=30),
        rangeslider_visible=(agg_mean != 'ALL'),
    )

    return patched_chips, fig


@callback(
    Output('MTA-aggregate-graph', 'figure', allow_duplicate=True),
    Input('MTA-aggregate-sum-select', "value"),
    Input('MTA-aggregate-mean-select', "value"),
    State('MTA-aggregate-labels-chk', 'checked'),
    State('MTA-aggregate-graph', 'figure'),
    prevent_initial_call=True,
)
def update_aggregate_bars(agg_sum, agg_mean, show_labels, fig):
    patched_figure = Patch()

    # Note for data processing:
    # First, sum the data by 'agg_sum', to have the total ridership by week/month/quarter...
    # Then the histogram will calculate the mean by 'bins_size' depending on 'agg_mean',
    # to have the mean by week/month/quarter...
    # Except if 'agg_sum'=='TOTAL', it will be calculated directly by the histogram

    # no need to sum the data for 'TOTAL' as it will be summed by the histogram using histfunc = "sum"
    # nor by day as the data is already by day
    dff = df.groupby(pd.Grouper(key='Date', freq=agg_sum)).sum() if agg_sum not in ['TOTAL', 'D'] else df.copy()
    if agg_sum not in ['TOTAL', 'D']:
        dff.reset_index(inplace=True)
    histfunc = "avg" if agg_sum != 'TOTAL' else "sum"

    date_min = dff['Date'].min()
    date_max = dff['Date'].max()

    bins_start = (date_min - timedelta(days=date_min.isoweekday() % 7)) if agg_mean == 'W' else date(date_min.year, 1,
                                                                                                     1)
    bins_end = date_max
    if agg_mean == 'ALL':
        bins_size = (bins_end.date() - bins_start).days * to_ms['D']
    elif agg_mean in ['W', 'D']:
        bins_size = to_ms[agg_mean]
    else:
        bins_size = agg_mean

    for i in range(len(fig['data'])):
        transport = fig["data"][i]['name']
        patched_figure["data"][i]["x"] = dff['Date']
        patched_figure["data"][i]["y"] = dff[transport]
        patched_figure["data"][i]["histfunc"] = histfunc
        patched_figure["data"][i]["xbins"] = {'start': bins_start, 'end': bins_end, 'size': bins_size}
        patched_figure["data"][i]["texttemplate"] = "%{y:.4s}" if show_labels and agg_mean != 'D' else None

        # Modify the xaxis if agg_mean == 'ALL' or not
    title = None
    if agg_mean == 'ALL':
        start = datetime.strftime(date_min, "%m/%d/%Y")
        end = datetime.strftime(date_max, "%m/%d/%Y")
        title = f"OVERALL ({start} - {end})"

    patched_figure["layout"]["xaxis"]["title"]["text"] = title
    patched_figure["layout"]["xaxis"]["showticklabels"] = (agg_mean != 'ALL')
    patched_figure["layout"]["xaxis"]["ticks"] = "inside" if (agg_mean != 'ALL') else ""
    patched_figure["layout"]["xaxis"]["rangeslider"]["visible"] = (agg_mean != 'ALL')

    return patched_figure


@callback(
    Output('MTA-aggregate-graph', 'figure', allow_duplicate=True),
    Input('MTA-aggregate-labels-chk', 'checked'),
    State('MTA-aggregate-mean-select', "value"),
    State('MTA-aggregate-graph', 'figure'),
    prevent_initial_call=True,
)
def update_bar_labels(show_labels, agg_mean, fig):
    patched_figure = Patch()
    for i in range(len(fig['data'])):
        patched_figure["data"][i]["texttemplate"] = "%{y:.4s}" if show_labels and agg_mean != 'D' else None
    return patched_figure


@callback(
    Output('MTA-aggregate-graph', 'figure', allow_duplicate=True),
    Input('MTA-aggregate-unstack-chk', 'checked'),
    prevent_initial_call=True,
)
def update_bar_stack(unstack):
    patched_figure = Patch()
    patched_figure["layout"]["barmode"] = 'group' if unstack else 'stack'
    return patched_figure


@callback(
    Output('MTA-aggregate-graph', 'figure', allow_duplicate=True),
    Input('MTA-aggregate-graph', 'relayoutData'),  # Triggered by zooming/panning on figure
    State('MTA-aggregate-graph', 'figure'),
    prevent_initial_call=True,
)
def update_xticks(_, fig):
    if not fig:
        return no_update

    xticks = set_xticks(fig["layout"]["xaxis"]["range"])

    patched_figure = Patch()
    patched_figure["layout"]["xaxis"]["dtick"] = xticks["dtick"]
    patched_figure["layout"]["xaxis"]["tickformat"] = xticks["tickformat"]
    patched_figure["layout"]["xaxis"]["minor"]["dtick"] = xticks["minor_dtick"]

    return patched_figure
