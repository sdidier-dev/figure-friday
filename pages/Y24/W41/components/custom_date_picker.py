from datetime import timedelta, datetime

from dash import html, Input, Output, callback, State, no_update, dcc
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from ..config_Y24W41 import df


def get_date_picker(type, selected_range):
    params = dict(
        id="custom-date-picker",
        type="range",
        label=html.Label("Date range:", style={'font-size': 16, 'line-height': 20}),
        description=dmc.RadioGroup(
            dmc.Group([
                html.Label("Calendar type:"),
                dmc.Radio(label='Day', value='day',
                          color='var(--bs-primary)', size="xs", styles={'label': {'padding-left': 5}}),
                dmc.Radio(label='Month', value='month',
                          color='var(--bs-primary)', size="xs", styles={'label': {'padding-left': 5}}),
                dmc.Radio(label='Year', value='year',
                          color='var(--bs-primary)', size="xs", styles={'label': {'padding-left': 5}}),
            ]),
            id="custom-date-picker-radiogroup",
            value=type
        ),
        leftSection=DashIconify(icon="fa:calendar", width=16), leftSectionPointerEvents="none",
        minDate=df.index.min(), maxDate=df.index.max(),
        numberOfColumns=1 if type == 'year' else 3,
        allowSingleDateInRange=True,
        value=selected_range,
        valueFormat="YYYY" if type == 'year' else "MMMM YYYY" if type == 'month' else "MMM. D, YYYY",
        classNames={'input': 'text-center'}
    )

    if type == 'year':
        date_picker = dmc.YearPickerInput(**params)
    elif type == 'month':
        date_picker = dmc.MonthPickerInput(**params)
    else:
        date_picker = dmc.DatePickerInput(**params)

    return [date_picker, dcc.Store(id='custom-date-picker-range-store', data=selected_range)]


def get_corrected_range(type, current_range, min_date, max_date):
    # if 'month'/'year' modify the selected range to have the full range, keeping the range in [min_date, max_date]
    # ie if 'month' and current_range = ['2020-03-15', '2024-10-07'] => corrected_range = ['2020-03-01', '2024-10-31']

    start_datetime, end_datetime = [datetime.fromisoformat(current_range[0]), datetime.fromisoformat(current_range[1])]
    min_datetime, max_datetime = [datetime.fromisoformat(min_date), datetime.fromisoformat(max_date)]

    if type == 'year':
        return [datetime(start_datetime.year, 1, 1), datetime(end_datetime.year + 1, 1, 1) - timedelta(days=1)]
    elif type == 'month':
        start = datetime(start_datetime.year, start_datetime.month, 1)
        if end_datetime.month == 12:
            end = datetime(end_datetime.year + 1, 1, 1) - timedelta(days=1)
        else:
            end = datetime(end_datetime.year, end_datetime.month + 1, 1) - timedelta(days=1)

        date_min = datetime(min_datetime.year, min_datetime.month, 1)
        date_max = datetime(max_datetime.year, max_datetime.month + 1, 1) - timedelta(days=1)

        return [max(date_min, start), min(date_max, end)]
    else:
        return [max(min_datetime, start_datetime), min(max_datetime, end_datetime)]


custom_date_picker = html.Div(
    id='custom-date-picker-container',
    children=get_date_picker('day', [df.index.min(), df.index.max()]),
    style={'width': 280}
)


@callback(
    Output('custom-date-picker-container', 'children'),
    Input('custom-date-picker-radiogroup', 'value'),
    State('custom-date-picker', 'value'),
    State('custom-date-picker', 'minDate'),
    State('custom-date-picker', 'maxDate'),
    prevent_initial_call=True,
)
def change_date_picker_type(type, current_range, min_date, max_date):
    if not current_range[0] or not current_range[1]:
        return get_date_picker(type, [df.index.min(), df.index.max()])

    modified_range = get_corrected_range(type, current_range, min_date, max_date)
    return get_date_picker(type, modified_range)


@callback(
    Output('custom-date-picker', 'value'),
    Output('custom-date-picker-range-store', 'data'),
    Input('custom-date-picker', 'value'),
    State('custom-date-picker-range-store', 'data'),
    State('custom-date-picker-radiogroup', 'value'),
    State('custom-date-picker', 'minDate'),
    State('custom-date-picker', 'maxDate'),
    prevent_initial_call=True,
)
def correct_date_range(current_range, store_data, type, min_date, max_date):
    if not current_range[0] or not current_range[1]:
        return no_update, no_update

    current_range_datetime = [datetime.fromisoformat(current_range[0]), datetime.fromisoformat(current_range[1])]
    store_data_datetime = [datetime.fromisoformat(store_data[0]), datetime.fromisoformat(store_data[1])]
    corrected_range = get_corrected_range(type, current_range, min_date, max_date)

    return (corrected_range if current_range_datetime != corrected_range else no_update,
            corrected_range if store_data_datetime != corrected_range else no_update)
