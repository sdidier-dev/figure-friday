import pandas as pd
from datetime import timedelta

from dash import html, Input, Output, dcc, callback, State, Patch, no_update
from dash_bootstrap_templates import ThemeChangerAIO, template_from_url
import dash_mantine_components as dmc
import plotly.graph_objects as go

from ..config_W41 import df, transports, to_ms, assets_dir

# hyperparameters fine-tuned with optuna optimization using cross validation
# and 'mean absolute percentage error' as metric
forecaster_params = {
    'Subways': {
        'detrender-passthrough': True, 'deseasonalizer-sp': 12, 'deseasonalizer-passthrough': True,
        'scaler-passthrough': False, 'p': 14, 'd': 1, 'q': 4
    },
    'Buses': {
        'detrender-passthrough': False, 'deseasonalizer-sp': 7, 'deseasonalizer-passthrough': False,
        'scaler-passthrough': False, 'p': 2, 'd': 1, 'q': 11
    },
    'LIRR': {
        'detrender-passthrough': True, 'deseasonalizer-sp': 14, 'deseasonalizer-passthrough': True,
        'scaler-passthrough': True, 'p': 11, 'd': 1, 'q': 6
    },
    'Metro-North': {
        'detrender-passthrough': False, 'deseasonalizer-sp': 8, 'deseasonalizer-passthrough': True,
        'scaler-passthrough': True, 'p': 4, 'd': 1, 'q': 5
    },
    'Access-A-Ride': {
        'detrender-passthrough': False, 'deseasonalizer-sp': 1, 'deseasonalizer-passthrough': False,
        'scaler-passthrough': False, 'p': 6, 'd': 1, 'q': 7
    },
    'Bridges and Tunnels': {
        'detrender-passthrough': False, 'deseasonalizer-sp': 1, 'deseasonalizer-passthrough': False,
        'scaler-passthrough': False, 'p': 14, 'd': 1, 'q': 14
    },
    'Staten Island Railway': {
        'detrender-passthrough': False, 'deseasonalizer-sp': 6, 'deseasonalizer-passthrough': False,
        'scaler-passthrough': True, 'p': 6, 'd': 1, 'q': 8
    },
}

MTA_pred_line = html.Div([
    html.Div([
        dmc.ChipGroup(
            id="MTA-pred-chipgroup",
            children=[dmc.Chip(transport, value=transport, color='var(--bs-primary)') for transport in transports],
            value='Subways',
        )], className='d-flex flex-wrap gap-2'
    ),
    html.Div([
        dmc.RadioGroup(
            dmc.Group([
                dmc.Tooltip(
                    dmc.Radio(label='Current Prediction', value='current',
                              color='var(--bs-primary)', styles={'label': {'padding-left': 5}}),
                    multiline=True, withArrow=True, arrowSize=6, w=300, position="top",
                    label="Uses the full data available to forecast the daily ridership for the next 30 days "
                          "(of the last data point).",
                    classNames={
                        'tooltip': 'bg-body text-body border border-primary',
                        'arrow': 'bg-body border-bottom border-end border-primary'
                    },
                ),
                dmc.Tooltip(
                    dmc.Radio(label='Backtesting:', value='back',
                              color='var(--bs-primary)', styles={'label': {'padding-left': 5}}),
                    multiline=True, withArrow=True, arrowSize=6, w=500, position="top", bg='var(--bs-body-bg)',
                    label="Backtesting is used to evaluate the performance of the model. "
                          "The dataset is split in Train and Test sets. The Train set is used to fit an ARIMA model, "
                          "then the model is used to make predictions for the 30 following days. Those predictions are "
                          "compared to the Test set, unknown by the model, using the Mean Absolute Percentage Error "
                          "(MAPE) metric to assess the model performance. We can evaluate the model using different "
                          "splits, called Folds. Here we are using 10 Folds with a Step of 7 days",
                    classNames={
                        'tooltip': 'bg-body text-body border border-primary',
                        'arrow': 'bg-body border-bottom border-end border-primary'
                    },
                ),

            ]),
            id="MTA-pred-radiogroup",
            value="current"
        ),
        html.Span(' Fold #', id='MTA-pred-back-span', className='ms-2'),
        dmc.NumberInput(
            id='MTA-pred-back-input',
            value=-9, min=-9, max=0,
            size='xs', w=50,
            stepHoldDelay=500, stepHoldInterval=100,
        ),
    ], className='d-flex align-items-center gap-1 ps-2'),

    html.Div([
        dmc.LoadingOverlay(
            id="MTA-pred-graph-loading-overlay",
            visible=True,
            loaderProps={"type": "bars", "color": "var(--bs-primary)"},
            overlayProps={"radius": "sm", "blur": 2},
        ),
        dcc.Graph(
            id='MTA-pred-graph',
            responsive=True,
            config={'displayModeBar': False},
            className='h-100',
        ),
    ], className='h-100 m-2', style={'position': 'relative'}),

], className='h-100 flex-fill d-flex flex-column gap-1')


# makes the loader visible when reloading data
@callback(
    Output("MTA-pred-graph-loading-overlay", "visible", allow_duplicate=True),
    Input('MTA-pred-chipgroup', "value"),
    Input(ThemeChangerAIO.ids.radio("theme"), "value"),
    Input("color-mode-switch", "checked"),
    prevent_initial_call=True,
)
def reactivate_graph_loader(*_):
    return True


# Note: can't use a Patch() while modifying the theme, the fig must be fully regenerated
# here we also update the transportation chips to match the fig colorway
@callback(
    Output('MTA-pred-chipgroup', 'children'),
    Output('MTA-pred-graph', 'figure'),
    Output("MTA-pred-graph-loading-overlay", "visible"),
    Input("MTA-pred-chipgroup", "value"),
    Input('MTA-pred-radiogroup', "value"),
    Input("MTA-pred-back-input", "value"),
    Input(ThemeChangerAIO.ids.radio("theme"), "value"),
    Input("color-mode-switch", "checked"),
    State('MTA-pred-chipgroup', 'children'),
)
def change_pred_graph(selected_transport, pred_type, selected_fold, theme, switch_on, chips):
    fig = go.Figure()

    # set the layout first to get the theme colors
    fig.update_layout(
        legend={'orientation': 'h', 'y': 1},
        margin={'autoexpand': True, "r": 5, "t": 0, "l": 0, "b": 5},
        template=f"{template_from_url(theme)}{'' if switch_on else '_dark'}",
        hovermode='x unified',
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

    y = df[selected_transport]

    # load pre-computed predictions
    df_folds_pred = pd.read_csv(f'{assets_dir}/pred/folds_{selected_transport}.csv', index_col='Date', parse_dates=True)
    df_folds_MAPE = pd.read_csv(f'{assets_dir}/pred/folds_MAPE.csv', index_col='Folds')
    df_actual_pred = pd.read_csv(f'{assets_dir}/pred/actual_pred.csv', index_col='Date', parse_dates=True)

    # make fig
    if pred_type == 'current':
        # Current Ridership
        fig.add_scatter(
            name='Last 100 Days Ridership',
            x=y[-100:].index, y=y[-100:],
            line_color=transport_colors[selected_transport],
            hovertemplate="%{y:.4s}"
        )
        # Ridership prediction
        fig.add_scatter(
            name='Next 30 Days Predictions',
            x=df_actual_pred.index, y=df_actual_pred[selected_transport],
            line={'color': transport_colors[selected_transport], 'dash': "dash"},
            hovertemplate="%{y:.4s}"
        )
    else:
        # bar plot for MAPE Score
        fold_number = len(df_folds_pred.columns)
        MAPE_x = []

        for fold in range(-fold_number+1, 1):
            folds_end_dates = df_folds_pred[f"fold_{-fold}"].dropna().index[-1]
            # MAPE_x.append(folds_end_dates)
            MAPE_x.append(folds_end_dates - timedelta(days=7))

        fig.add_bar(
            name="MAPE Score",
            x=MAPE_x,
            y=df_folds_MAPE[selected_transport],
            marker=dict(
                color=transport_colors[selected_transport],
                opacity=[1 if fold == selected_fold else 0.5 for fold in range(-fold_number+1, 1)]
            ),

            xperiod=to_ms['W-SAT'],
            xperiodalignment="middle",
            showlegend=False,
            texttemplate="%{y:.3f}",
            textfont_color=fig['layout']['template']['layout']['font']['color'],
            customdata=list(range(-fold_number+1, 1)),  # used to select the corresponding fold on bar click
            hoverinfo="none",
        )

        # Folds line plots
        y_fold_pred = df_folds_pred[f"fold_{-selected_fold}"].dropna()
        y_split_index_position = y.index.get_indexer([y_fold_pred.index[0]])[0]

        fig.add_scatter(
            name='Train (from 2020-03-01)',
            x=y[-150:y_split_index_position].index, y=y[-150:y_split_index_position],
            line_color=transport_colors[selected_transport],
            yaxis="y2",
            hovertemplate="%{y:.4s}"
        )
        fig.add_scatter(
            name='Test',
            x=y_fold_pred.index, y=y[y_split_index_position:],
            opacity=0.5,
            line_color=transport_colors[selected_transport],
            yaxis="y2",
            hovertemplate="%{y:.4s}"
        )
        fig.add_scatter(
            name='Prediction',
            x=y_fold_pred.index, y=y_fold_pred,
            line={'color': transport_colors[selected_transport], 'dash': "dash"},
            yaxis="y2",
            hovertemplate="%{y:.4s}"
        )

        fig.update_layout(
            yaxis={'title_text': "MAPE", 'domain': [0, 0.3], 'dtick': 0.1},
            yaxis2={'title_text': "Ridership", 'domain': [0.45, 1]},
        )

        # add annotation for the MAPE plot title
        fig.add_annotation(
            showarrow=False,
            text='MAPE Score (the lower, the better)<br>'
                 'Tip: The bars can also be clicked to select the corresponding fold',
            font_size=14,
            xref="paper", xanchor="center", x=0.5,
            yref="y domain", yanchor="bottom", y=1,
        )

        # add vline and annotation for last date of the data
        # Note: the annotation param of vline doesn't work with dates for x
        # also note, the x type hint doesn't accept string, but safe to ignore

        # noinspection PyTypeChecker
        fig.add_vline(
            x=y.index[-1],
            line={'color': fig['layout']['template']['layout']['font']['color'], 'dash': "dash"},
            yref="y2"
        )
        fig.add_annotation(
            showarrow=False,
            text='Last date of current data',
            textangle=-90,
            font_shadow="0px 0px 5px black",
            xref="x", x=y.index[-1], xanchor="left",
            yref="y2 domain", yanchor="middle", y=0.5,
        )

    # Note: False is to hide the loader when the fig is ready
    return patched_chips, fig, False


@callback(
    Output("MTA-pred-back-span", "style"),
    Output("MTA-pred-back-input", "disabled"),
    Input('MTA-pred-radiogroup', "value"),
)
def update_disable_back_input(pred_type):
    return ({'font-size': 14, 'color': 'var(--mantine-color-dimmed)' if pred_type == 'current' else ''},
            pred_type == 'current')


@callback(
    Output('MTA-pred-back-input', 'value'),
    Input('MTA-pred-graph', 'clickData'),
    prevent_initial_call=True,
)
def update_fold_selection(click_data):
    if 'customdata' in click_data['points'][0]:
        return click_data['points'][0]['customdata']
    return no_update
