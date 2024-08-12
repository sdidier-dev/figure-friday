from dash import html, dcc, Input, Output, Dash, callback, register_page
import dash_bootstrap_components as dbc

layout = html.Div(
    [
        html.Div('This is our Analytics page',
                 className='border border-success border-3'
                 ),
        html.Div(
            [
                "Select a city: ",
                dcc.RadioItems(
                    ['New York City', 'Montreal', 'San Francisco'],
                    'Montreal',
                    id='analytics-input')
            ],
            className='flex-fill border border-success border-3'
        ),
        html.Div(
            id='analytics-output',
            className='flex-fill border border-success border-3'
        ),
    ],
    className='d-flex flex-column h-100'
)


# flex-fill
# flex-grow-1
# flex-shrink-1
@callback(
    Output('analytics-output', 'children'),
    Input('analytics-input', 'value')
)
def update_city_selected(input_value):
    return f'You selected: {input_value}'


if __name__ == "__main__":
    app = Dash(__name__, external_stylesheets=[dbc.themes.SOLAR])
    app.layout = html.Div(layout, className='vh-100')
    app.run(debug=True)
else:
    register_page(
        __name__,
        path=f"/{__name__.split('.')[-1].replace('_', '-')}",
        title='test first app page'
    )
