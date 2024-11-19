from pprint import pprint

from dash import html, Input, Output, dcc, callback, State, Patch, no_update
from dash_bootstrap_templates import ThemeChangerAIO, template_from_url
from datetime import timedelta, datetime, date
import dash_mantine_components as dmc
import plotly.graph_objects as go
import pandas as pd
import dash_bootstrap_components as dbc
from dash_iconify import DashIconify

from ..config_W41 import df, to_ms, transports

# add pre underlay
# add spinner
# add custom date range
# try to use patches
# add tootips? transportations maps?
# add MTA API

# bug zomming/panning with diff + pandemic date

# Used in the first select component of the title and for the hover text of the bar fig
agg1_data_select = {
    'TOTAL': 'Total',
    'YS': 'Yearly Mean',
    '2QS': 'Half-Yearly Mean',
    'QS': 'Quarterly Mean',
    'MS': 'Monthly Mean',
    'W-SAT': 'Weekly Mean',
    'D': 'Daily Mean'
}
# Used to disable agg2 values that are not compatible with agg1, ie quarterly mean by month
# Also used to return an empty fig if not compatible
disabled_options = {
    "TOTAL": [],
    "D": ['D'],
    "W-SAT": ['W-SAT', 'D'],
    "MS": ['MS', 'W-SAT', 'D'],
    "QS": ['QS', 'MS', 'W-SAT', 'D'],
    "2QS": ['2QS', 'QS', 'MS', 'W-SAT', 'D'],
    "YS": ['YS', '2QS', 'QS', 'MS', 'W-SAT', 'D'],
}
# #################### Card Header ####################
MTA_aggregate_title_controls = [
    dmc.Select(
        id="MTA-aggregate-agg1-select",
        data=[{"value": k, "label": v} for k, v in agg1_data_select.items()],
        value="TOTAL",
        size="xs", w=200,
        searchable=True, allowDeselect=False, checkIconPosition="right",
        withScrollArea=False,
        variant='unstyled',
        classNames={"input": 'fw-bold text-primary text-end text-decoration-underline'},
        styles={"input": {'font-family': 'Source Sans Pro', 'font-size': 22, 'cursor': 'pointer', 'width': None}},
        comboboxProps={"position": "bottom-end", "width": 140},
        rightSection=DashIconify(icon="mynaui:chevron-up-down"), rightSectionWidth=15,
        rightSectionPointerEvents="none",
    ),
    'of Ridership by',
    dmc.Select(
        id="MTA-aggregate-agg2-select",
        data=[
            {"value": "ALL", "label": "Overall"},
            {"value": "YS", "label": "Year"},
            {"value": "2QS", "label": "Half-Year"},
            {"value": "QS", "label": "Quarter"},
            {"value": "MS", "label": "Month"},
            {"value": "W-SAT", "label": "Week"},
            {"value": "D", "label": "Day"},
        ],
        value="QS",
        # value="MS",
        size="xs", w=150, searchable=True, allowDeselect=False, checkIconPosition="right",
        variant='unstyled',
        classNames={"input": 'fw-bold text-primary text-decoration-underline'},
        styles={"input": {'font-family': 'Source Sans Pro', 'font-size': 22, 'cursor': 'pointer'}},
        comboboxProps={"width": 140},
        leftSection=DashIconify(icon="mynaui:chevron-up-down"), leftSectionWidth=15,
        rightSection=' ', rightSectionWidth=0,
        leftSectionPointerEvents="none", rightSectionPointerEvents="none",
    )
]


@callback(
    Output('MTA-aggregate-agg2-select', 'data'),
    Output('MTA-aggregate-agg2-select', 'classNames'),
    Input('MTA-aggregate-agg1-select', "value"),
    Input('MTA-aggregate-agg2-select', "value"),
    State('MTA-aggregate-agg2-select', 'data'),
)
def update_aggregate_agg2_select_data(agg1_value, agg2_value, agg2_data):
    # disable agg2 values that are not compatible with agg1, ie quarterly mean by month
    patched_options = Patch()
    for i, option in enumerate(agg2_data):
        patched_options[i]["disabled"] = option['value'] in disabled_options[agg1_value]
    input_font_color = ' text-muted' if agg2_value in disabled_options[agg1_value] else ' text-primary'
    return patched_options, {"input": 'fw-bold text-decoration-underline' + input_font_color}


# #################### Card Body ####################
# Map Pandas period to Plotly period, use for bar xperiod
plotly_period = {
    'YS': 'M12',
    '2QS': 'M6',
    'QS': 'M3',
    'MS': 'M1',
    'W-SAT': to_ms['W-SAT'],
    'D': to_ms['D']
}

MTA_aggregate_bar = html.Div([
    html.Label("Select Transportations:", className='mb-2'),
    html.Div([
        dmc.ChipGroup(
            id="MTA-aggregate-chipgroup",
            multiple=True,
            children=[dmc.Chip(transport, value=transport, color='var(--bs-primary)') for transport in transports],
            value=['Subways'],
        ),
    ], className='d-flex gap-2'),

    html.Div([
        html.Label("Options:"),
        html.Div([
            html.Div([
                dmc.Checkbox(id="MTA-aggregate-pre-chk", label="Show Pre-Pandemic Comparable Period Ridership",
                             color='var(--bs-primary)', checked=False),
                dmc.RadioGroup(
                    dmc.Group([
                        dmc.Radio(label='Underlay', value='underlay', color='var(--bs-primary)'),
                        dmc.Radio(label='Difference', value='diff', color='var(--bs-primary)'),
                        dmc.Radio(label='Percentage', value='percent', color='var(--bs-primary)')
                    ]),
                    id="MTA-aggregate-pre-radiogroup",
                    value="underlay", size="sm",
                ),
            ], className='d-flex gap-3'),
            html.Div([
                dmc.Checkbox(id="MTA-aggregate-unstack-chk", label="Unstack Transportations Bars",
                             color='var(--bs-primary)', checked=False),
                dmc.Checkbox(id="MTA-aggregate-labels-chk", label="Show Labels",
                             color='var(--bs-primary)', checked=False),
                dmc.Checkbox(id="MTA-aggregate-pandemic-date-chk", label="Show Official Pandemic Declaration Date",
                             color='var(--bs-primary)', checked=False),
            ], className='d-flex gap-3'),
        ], className='d-flex flex-column gap-2'),
    ], className='d-flex gap-3 my-2'),

    dcc.Graph(
        id='MTA-aggregate-graph',
        responsive=True,
        config={'displayModeBar': False},
        className='h-100 flex-fill',
    )
], className='h-100 flex-fill d-flex flex-column gap-2')


def set_xticks(xrange, agg2_value):
    # find x_range
    start_datetime = datetime.fromisoformat(xrange[0])
    end_datetime = datetime.fromisoformat(xrange[1])
    range_timedelta = end_datetime - start_datetime

    # 6Y <= x_range or grouped by year or semester
    if timedelta(days=365 * 10) <= range_timedelta or agg2_value == 'YS':
        xticks = dict(dtick="M12", tickformat="%Y\n ", minor_dtick="M12")

    # 6Y <= x_range or grouped by year or semester
    elif (timedelta(days=365 * 6) <= range_timedelta < timedelta(days=365 * 10)) or agg2_value == "2QS":
        xticks = dict(dtick="M6", tickformat="H%h\n%Y", minor_dtick="M12")

    # 3Y <= x_range < 6Y or grouped by quarter
    elif (timedelta(days=365 * 3) <= range_timedelta < timedelta(days=365 * 6)) or agg2_value == "QS":
        xticks = dict(dtick="M3", tickformat="Q%q\n%Y", minor_dtick="M12")

    # 6M <= x_range < 3Y or grouped by month
    elif (timedelta(days=30 * 6) <= range_timedelta < timedelta(days=365 * 3)) or agg2_value == "MS":
        xticks = dict(dtick="M1", tickformat="%b\nQ%q '%y", minor_dtick="M3")

    # 30D <= x_range < 6M or grouped by week
    elif (timedelta(days=30) <= range_timedelta < timedelta(days=30 * 6)) or agg2_value == "W-SAT":
        xticks = dict(dtick=to_ms['W-SAT'], tickformat="S%U\n%b '%y", minor_dtick="M1")

    # x_range < 30D or grouped by day
    else:
        xticks = dict(dtick=to_ms['D'], tickformat="%e\nS%U %b '%y", minor_dtick=to_ms['W-SAT'])

    return xticks


# Note: can't use a Patch() while modifying the theme, the fig must be fully regenerated
# here we also update the transportation chips to match the fig colorway
@callback(
    Output('MTA-aggregate-chipgroup', 'children'),
    Output('MTA-aggregate-graph', 'figure'),
    Input('MTA-aggregate-chipgroup', "value"),
    Input(ThemeChangerAIO.ids.radio("theme"), "value"),
    Input("color-mode-switch", "checked"),
    Input('MTA-aggregate-agg1-select', "value"),
    Input('MTA-aggregate-agg2-select', "value"),

    Input('MTA-aggregate-pre-chk', 'checked'),
    Input('MTA-aggregate-pre-radiogroup', 'value'),

    Input('MTA-aggregate-unstack-chk', 'checked'),
    State('MTA-aggregate-labels-chk', 'checked'),
    State('MTA-aggregate-pandemic-date-chk', 'checked'),

    State('MTA-aggregate-graph', 'figure'),
    State('MTA-aggregate-chipgroup', 'children'),

)
def update_theme_aggregate_bar(
        selected_transports, theme, switch_on, agg1_value, agg2_value, pre_show, pre_type, unstack, show_labels,
        pandemic_date_show, fig, chips,
):
    # Save existing x range to re-apply it at the end
    xaxis_range = None
    if fig and isinstance(fig["layout"]["xaxis"]["range"][0], str):
        xaxis_range = fig["layout"]["xaxis"]["range"]

    fig = go.Figure()

    # set the layout first to get the theme colors
    fig.update_layout(
        showlegend=False,
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

    # if agg2 is not compatible with agg1 return empty fig, ie quarterly mean by month
    if agg2_value in disabled_options[agg1_value]:
        return patched_chips, fig

    # Data pre-processing
    # First aggregation by agg1_value to have weekly/monthly... values
    # Except for 'TOTAL' that will be summed below and 'D' as data is already by day
    dff = df.resample(agg1_value).sum() if agg1_value not in ['TOTAL', 'D'] else df.copy()

    # Second aggregation to have the mean by agg2_value or the sum if agg1_value == 'TOTAL'
    if agg1_value == 'TOTAL':
        dff = dff.resample(agg2_value).sum() if agg2_value != 'ALL' else dff.sum()
    else:
        dff = dff.resample(agg2_value).mean() if agg2_value != 'ALL' else dff.mean()

    # add percent of pre-pandemic
    if pre_show and pre_type == 'percent':
        if agg2_value != 'ALL':
            dff = dff.assign(**{t + '_percent': dff[t] / dff[t + '_pre'] for t in transports})
        else:
            for t in transports:
                dff[t + '_percent'] = dff[t] / dff[t + '_pre']

    # Used to format x text on hover
    agg1_label_hover = agg1_data_select[agg1_value]
    pre_hover = ''
    if pre_show and pre_type != 'underlay':
        pre_hover = '<br>(Pre-Pandemic Difference)' if pre_type == 'diff' else '<br>(Pre-Pandemic Percentage)'

    xhoverformat = {
        'ALL': 'Overall ' + agg1_label_hover + pre_hover,
        'YS': agg1_label_hover + " - <b>%Y</b>" + pre_hover,
        '2QS': agg1_label_hover + " - <b>H%h '%y</b>" + pre_hover,
        'QS': agg1_label_hover + " - <b>Q%q '%y</b>" + pre_hover,
        'MS': agg1_label_hover + " - <b>%b '%y</b>" + pre_hover,
        'W-SAT': agg1_label_hover + " - <b>S%U %b '%y</b>" + pre_hover,
        'D': agg1_label_hover + " - <b>%e %b '%y</b>" + pre_hover
    }

    # Add traces
    if not (pre_show and pre_type == 'underlay'):
        # Pre-Pandemic difference/percentage using barmode='group'/'stack': no need to deal with offset/base/width
        fig.update_layout(barmode='group' if unstack else 'stack', bargap=0.1)

        y_format = "%{y:.0%}" if pre_show and pre_type == 'percent' else "%{y:.4s}"

        for transport in selected_transports:
            col = transport
            if pre_show:
                col += '_diff' if pre_type == 'diff' else '_percent'

            fig.add_bar(
                name=transport,
                xperiod=plotly_period[agg2_value] if agg2_value != 'ALL' else None,
                x=dff.index if agg2_value != 'ALL' else [1],
                y=dff[col] if agg2_value != 'ALL' else [dff[col]],
                marker_color=transport_colors[transport],
                marker_line_width=0,
                textposition="outside" if unstack else "inside",
                texttemplate=y_format if show_labels else None,
                xhoverformat=xhoverformat[agg2_value],
                hovertemplate=f"{(xhoverformat[agg2_value] + '<br>') if agg2_value == 'ALL' else ''}<b>{y_format}</b>",
            )

        # Add Pre-Pandemic baseline
        if pre_show:
            fig.add_hline(
                y=0 if pre_type == 'diff' else 1,
                annotation_position='top left',
                annotation_text='Pre-Pandemic Baseline',
                line={'color': fig['layout']['template']['layout']['font']['color'], 'dash': "dash"}
            )

    else:
        # Pre-Pandemic underlay using barmode='overlay': need to deal with offset/base/width
        fig.update_layout(barmode='overlay', bargap=0)
        fig.update_yaxes(rangemode="nonnegative")

        base = [0] * len(dff.index)
        pre_base = [0] * len(dff.index)

        # get bars width
        xperiod_width = to_ms[agg2_value] if agg2_value != 'ALL' else 1
        xperiod_n_bars = len(selected_transports) if unstack else 1
        width = (0.8 if unstack else 0.6) * xperiod_width / xperiod_n_bars

        for i, transport in enumerate(selected_transports):
            # get bars offset
            if unstack:
                offset = -0.5 * len(selected_transports) * width + i * width
                pre_offset = -0.45 * xperiod_width + i * width
            else:
                offset = -0.5 * width
                pre_offset = -0.45 * xperiod_width

            y = dff[transport] if agg2_value != 'ALL' else [dff[transport]]
            hovertemplate = "<b>%{customdata:.4s}</b>"
            if agg2_value == 'ALL':
                hovertemplate = xhoverformat[agg2_value] + '<br>' + hovertemplate

            # actual data bars
            fig.add_bar(
                zorder=1,
                name=transport,
                xperiod=plotly_period[agg2_value] if agg2_value != 'ALL' else None,
                x=dff.index if agg2_value != 'ALL' else [1],
                y=y,
                offset=offset, base=base, width=width,

                marker_color=transport_colors[transport],
                marker_line_width=0,
                textposition="outside" if unstack else "inside",
                texttemplate="%{y:.4s}" if show_labels else None,
                xhoverformat=xhoverformat[agg2_value],
                # note: can't use %{y} using 'overlay' and 'base' in hovertemplate, as y is actually y + base
                customdata=y,
                hovertemplate=hovertemplate,
            )
            if not unstack:
                base = [sum(i) for i in zip(base, y)]

            # pre-pandemic bars
            pre_y = dff[transport + '_pre'] if agg2_value != 'ALL' else [dff[transport + '_pre']]
            fig.add_bar(
                visible=pre_show,
                name='Pre-Pandemic' if agg2_value != 'ALL' else transport + ' (Pre-Pandemic)',
                xperiod=plotly_period[agg2_value] if agg2_value != 'ALL' else None,
                x=dff.index if agg2_value != 'ALL' else [1],
                y=pre_y,
                offset=pre_offset, base=pre_base, width=width,
                marker=dict(
                    color=transport_colors[transport],
                    line={'color': transport_colors[transport], 'width': 2},
                    # Trick to add transparency to the color marker only, not the border,
                    # as marker_opacity applies to both
                    pattern={
                        'fillmode': "replace", 'shape': "/", 'solidity': 1,
                        'fgcolor': transport_colors[transport], 'fgopacity': 0.5
                    }
                ),
                textposition="outside" if unstack else "inside",
                texttemplate="%{y:.4s}" if show_labels else None,
                xhoverformat=xhoverformat[agg2_value],
                # note: can't use %{y} using 'overlay' and 'base' in hovertemplate, as y is actually y + base
                customdata=pre_y,
                hovertemplate=hovertemplate,
            )
            if not unstack:
                pre_base = [sum(i) for i in zip(pre_base, pre_y)]

    # Xaxis setting
    if agg2_value == 'ALL':
        start = datetime.strftime(df.index.min(), "%m/%d/%Y")
        end = datetime.strftime(df.index.max(), "%m/%d/%Y")
        date_delta = df.index.max() - df.index.min()
        x_title = f"OVERALL ({date_delta.days // 365} years, {date_delta.days % 365} days)<br>{start} - {end}"

        fig.update_xaxes(
            title_text=x_title,
            color=fig['layout']['template']['layout']['font']['color'],
            showticklabels=False,
            fixedrange=True
        )
        fig.update_yaxes(fixedrange=True)
    else:
        date_min = dff.index.min()
        date_max = dff.index.max()

        # set the ticks depending on the range and agg2_value
        xticks = set_xticks(xaxis_range if xaxis_range else [date_min.isoformat(), date_max.isoformat()],
                            agg2_value)

        fig.update_xaxes(
            color=fig['layout']['template']['layout']['font']['color'],
            range=xaxis_range,
            ticklabelmode="period",
            ticks="inside",
            dtick=xticks["dtick"],
            tickformat=xticks["tickformat"],
            tickwidth=2,
            minor=dict(ticks="outside", dtick=xticks["minor_dtick"], tickwidth=2, ticklen=30),
            rangeslider_visible=True,
        )

    # Layout and yaxis setting
    y_title = 'Ridership'
    if pre_show and pre_type != 'underlay':
        y_title += f"  <i>(Pre-Pandemic {'Difference' if pre_type == 'diff' else 'Percentage'})</i>"
    fig.update_yaxes(
        title_text=y_title,
        tickformat=".0%" if pre_show and pre_type == 'percent' else "s",
    )

    fig.update_layout(
        hovermode='x unified' if agg2_value != 'ALL' else None,
        margin={'autoexpand': True, "r": 5, "t": 0, "l": 0, "b": 5},
        template=f"{template_from_url(theme)}{'' if switch_on else '_dark'}",
    )

    # add vline and annotation for pandemic declaration date
    # Note: the annotation param of vline doesn't work with dates for x
    fig.add_vline(
        visible=pandemic_date_show,
        x='2020-03-11',
        line={'color': fig['layout']['template']['layout']['font']['color'], 'dash': "dash"}
    )
    fig.add_annotation(
        visible=pandemic_date_show,
        showarrow=False,
        text='Official declaration of COVID-19 pandemic',
        textangle=-90,
        font_shadow="0px 0px 5px black",
        xref="x", x='2020-03-11', xshift=10,
        yref="paper", y=0.5,
        hovertext='<b>2020-03-11</b> Official World Health Organization declaration of a global COVID-19 pandemic',
    )
    return patched_chips, fig


@callback(
    Output('MTA-aggregate-unstack-chk', 'disabled'),
    Output('MTA-aggregate-unstack-chk', 'checked'),
    Input('MTA-aggregate-pre-chk', 'checked'),
    Input('MTA-aggregate-pre-radiogroup', 'value'),
    State('MTA-aggregate-unstack-chk', 'checked'),
    prevent_initial_call=True,
)
def update_disabled_unstack_chk(pre_show, pre_type, unstack):
    return (pre_show and pre_type == 'percent',
            True if pre_show and pre_type == 'percent' and not unstack else no_update)  # force unstack if percent


@callback(
    Output('MTA-aggregate-graph', 'figure', allow_duplicate=True),
    Input('MTA-aggregate-labels-chk', 'checked'),
    State('MTA-aggregate-pre-chk', 'checked'),
    State('MTA-aggregate-pre-radiogroup', 'value'),
    State('MTA-aggregate-graph', 'figure'),
    prevent_initial_call=True,
)
def update_bar_labels(show_labels, pre_show, pre_type, fig):
    y_format = "%{y:.0%}" if pre_show and pre_type == 'percent' else "%{y:.4s}"
    patched_figure = Patch()
    for i in range(len(fig['data'])):
        patched_figure["data"][i]["texttemplate"] = y_format if show_labels else None
    return patched_figure


@callback(
    Output('MTA-aggregate-graph', 'figure', allow_duplicate=True),
    Input('MTA-aggregate-graph', 'relayoutData'),  # Triggered by zooming/panning on figure
    Input('MTA-aggregate-agg2-select', 'value'),
    State('MTA-aggregate-graph', 'figure'),
    prevent_initial_call=True,
)
def update_xticks(_, agg2_value, fig):
    if not fig or agg2_value == 'ALL':
        return no_update

    if fig and isinstance(fig["layout"]["xaxis"]["range"][0], str):
        xaxis_range = fig["layout"]["xaxis"]["range"]
    else:
        xaxis_range = [df.index.min().isoformat(), df.index.max().isoformat()]

    xticks = set_xticks(xaxis_range, agg2_value)

    patched_figure = Patch()
    patched_figure["layout"]["xaxis"]["dtick"] = xticks["dtick"]
    patched_figure["layout"]["xaxis"]["tickformat"] = xticks["tickformat"]
    patched_figure["layout"]["xaxis"]["minor"]["dtick"] = xticks["minor_dtick"]
    return patched_figure


@callback(
    Output('MTA-aggregate-graph', 'figure', allow_duplicate=True),
    Input('MTA-aggregate-pandemic-date-chk', 'checked'),
    State('MTA-aggregate-graph', 'figure'),
    prevent_initial_call=True,
)
def update_pandemic_date_visible(pandemic_date_show, fig):
    patched_figure = Patch()
    # show/hide line
    for i, shape in enumerate(fig['layout']['shapes']):
        if shape['x0'] == '2020-03-11':
            patched_figure['layout']['shapes'][i]['visible'] = pandemic_date_show
    # show/hide annotation
    for i, annotation in enumerate(fig['layout']['annotations']):
        if annotation['x'] == '2020-03-11':
            patched_figure['layout']['annotations'][i]['visible'] = pandemic_date_show

    return patched_figure