import json
import os

from datetime import timedelta, date, time, datetime
from dash import html, Input, Output, dcc, callback, State, Patch, no_update, ctx
import dash_ag_grid as dag
import pandas as pd
import dash_mantine_components as dmc
from dateutil.relativedelta import relativedelta

from ..config_W41 import df, transports, to_ms, plotly_period

# period = 6
#
# # last period
# date_range = pd.date_range(
#     start=date(df.index[-1].year - period // 12, df.index[-1].month - period % 12, 1),
#     end=date(df.index[-1].year, df.index[-1].month, 1) - timedelta(days=1)
# )
# # keep only <transports> + <transport>_pre cols and rows in date_range
# dff = df[transports + [t + '_pre' for t in transports]][df.index.isin(date_range)]
# # add dayofweek col to filter weekdays/weekend (Monday=0, Sunday=6)
# dff = dff.assign(dayofweek=dff.index.weekday)
# monthly_mean = dff.resample('MS').sum().mean()
#
# # previous period
# date_range_previous = pd.date_range(
#     start=date(df.index[-1].year - 2 * period // 12, df.index[-1].month - 2 * period % 12, 1),
#     end=date(df.index[-1].year - period // 12, df.index[-1].month - period % 12, 1) - timedelta(days=1)
# )
# dff_previous = df[transports][df.index.isin(date_range_previous)]
# monthly_mean_previous = dff_previous.resample('MS').sum().mean()
#
# dataset = pd.DataFrame({
#     'weekdays': dff[transports][dff['dayofweek'].isin([0, 1, 2, 3, 4])].mean(),
#     'weekend': dff[transports][dff['dayofweek'].isin([5, 6])].mean(),
#     'month': monthly_mean[transports],
#     'previous': monthly_mean[transports] / monthly_mean_previous[transports] - 1,
#     'pre': monthly_mean[transports] / monthly_mean[[t + '_pre' for t in transports]].set_axis(transports) - 1
# }).reset_index(names='transportation')

cell_style_compare = {
    "styleConditions": [
        {"condition": "params.value < 0", "style": {"color": "var(--bs-warning)"}},
        {"condition": "params.value >= 0", "style": {"color": "var(--bs-success)"}},
    ],
}

cell_style_daily = {
    "function": "params.value && {'font-size': 1e6 < params.value ? 18 : 1e5 < params.value ? 14 : 10 }"
}
cell_style_monthly = {
    "function": "params.value && {'font-size': 30e6 < params.value ? 18 : 30e5 < params.value ? 14 : 10 }"
}

columnDefs = [
    {'field': 'transportation', "headerClass": 'center-aligned-header', "width": 160},
    {
        'headerName': 'Ridership Mean',
        'headerClass': 'center-aligned-group-header', "suppressStickyLabel": True,
        'children': [
            {
                'headerName': 'Daily',
                'headerClass': 'center-aligned-group-header', "suppressStickyLabel": True,
                'children': [
                    {
                        'field': 'weekdays', "valueFormatter": {"function": "d3.format('.4s')(params.value)"},
                        "headerClass": 'center-aligned-header', "cellClass": 'center-aligned-cell',
                        'cellStyle': cell_style_daily
                    },
                    {
                        'field': 'weekend', "valueFormatter": {"function": "d3.format('.4s')(params.value)"},
                        "headerClass": 'center-aligned-header', "cellClass": 'center-aligned-cell',
                        'cellStyle': cell_style_daily
                    },
                ]
            },
            {
                'field': 'month', 'headerName': 'Monthly',
                "valueFormatter": {"function": "d3.format('.4s')(params.value)"},
                "headerClass": 'center-aligned-header', "cellClass": 'center-aligned-cell',
                'cellStyle': cell_style_monthly
            },
        ]
    },
    {
        'headerName': 'Monthly Mean Compared To',
        'headerClass': 'center-aligned-group-header', "suppressStickyLabel": True,
        'children': [
            {
                'field': 'previous', 'headerName': 'Previous Period',
                "valueFormatter": {"function": "d3.format('+.0%')(params.value)"},
                "headerClass": 'center-aligned-header', "cellClass": 'center-aligned-cell',
                'cellStyle': cell_style_compare, "width": 130,
            },
            {
                'field': 'pre', 'headerName': 'Pre-Pandemic',
                "valueFormatter": {"function": "d3.format('+.0%')(params.value)"},
                "headerClass": 'center-aligned-header', "cellClass": 'center-aligned-cell',
                'cellStyle': cell_style_compare, "width": 130,
            },
        ]
    }
]

defaultColDef = {
    "wrapHeaderText": True,
    "width": 100,
}

dashGridOptions = {
    "domLayout": "autoHeight",
    'headerHeight': 25,
    "rowHeight": 30
}

MTA_key_figures_grid = html.Div([

    html.Div([
        html.Div([
            html.Div([
                'Key Figures over the Last Period of',
                dmc.NumberInput(
                    id='MTA-key-figures-input',
                    value=6, min=1, max=24,
                    variant='unstyled', size='xs', w=50,
                    stepHoldDelay=500, stepHoldInterval=100,
                    classNames={"input": 'fw-bold fs-4 text-primary text-center text-decoration-underline pb-1'},
                    styles={"input": {'font-family': 'Source Sans Pro'}},
                ),
                'Month',
            ], className='d-flex fs-5 text-body'),
            html.Span(id='MTA-key-figures-span', className='ms-2 fs-6')
        ], className='d-flex justify-content-between align-items-center p-1'),

        dag.AgGrid(
            id="MTA-key-figures-grid",
            columnDefs=columnDefs,
            defaultColDef=defaultColDef,
            dashGridOptions=dashGridOptions,
            style={
                "height": None, 'width': 722,
                'box-shadow': '0 0 10px var(--bs-primary)',
                'border-color': 'var(--bs-primary)'
            }
        )
    ]),
],
    className='d-flex justify-content-center w-100 pb-2',
    style={
        'background-image': 'url("assets/subway.png")',
        'background-position': 'top 40px right',
        'background-repeat': 'no-repeat',
        'background-size': 'cover',
    }
)


@callback(
    Output('MTA-key-figures-grid', 'rowData'),
    Output('MTA-key-figures-span', 'children'),
    Input('MTA-key-figures-input', 'value'),
)
def change_date_picker_type(period):
    # last period
    date_range = pd.date_range(
        start=date(df.index[-1].year, df.index[-1].month, 1) - relativedelta(months=period),
        end=date(df.index[-1].year, df.index[-1].month, 1) - timedelta(days=1)
    )
    # keep only <transports> + <transport>_pre cols and rows in date_range
    dff = df[transports + [t + '_pre' for t in transports]][df.index.isin(date_range)]
    # add dayofweek col to filter weekdays/weekend (Monday=0, Sunday=6)
    dff = dff.assign(dayofweek=dff.index.weekday)
    monthly_mean = dff.resample('MS').sum().mean()

    # previous period
    date_range_previous = pd.date_range(
        start=date(df.index[-1].year, df.index[-1].month, 1) - relativedelta(months=2 * period),
        end=date(df.index[-1].year, df.index[-1].month, 1) - relativedelta(months=period) - timedelta(days=1)
    )
    dff_previous = df[transports][df.index.isin(date_range_previous)]
    monthly_mean_previous = dff_previous.resample('MS').sum().mean()

    dataset = pd.DataFrame({
        'weekdays': dff[transports][dff['dayofweek'].isin([0, 1, 2, 3, 4])].mean(),
        'weekend': dff[transports][dff['dayofweek'].isin([5, 6])].mean(),
        'month': monthly_mean[transports],
        'previous': monthly_mean[transports] / monthly_mean_previous[transports] - 1,
        'pre': monthly_mean[transports] / monthly_mean[[t + '_pre' for t in transports]].set_axis(transports) - 1
    }).reset_index(names='transportation')

    start_str = datetime.strftime(date_range[0], "%m/%d/%Y")
    end_str = datetime.strftime(date_range[-1], "%m/%d/%Y")
    return dataset.to_dict("records"), f'({start_str} - {end_str})'
