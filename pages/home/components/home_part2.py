from dash import html, Input, Output, callback, Patch
import dash_mantine_components as dmc
from dash_iconify import DashIconify

home_table_data = [
    {
        'week': 41, 'forum': 'https://community.plotly.com/t/figure-friday-2024-week-41/87878',
        'topic': "New York City Subway (MTA) Daily Ridership Data: Beginning 2020",
        'data source': 'https://data.ny.gov/Transportation/MTA-Daily-Ridership-Data-Beginning-2020/vxuj-8kew/about_data'
    }, {
        'week': 40, 'forum': 'https://community.plotly.com/t/figure-friday-2024-week-40/87698',
        'topic': "Eurovision Song Contest voting and contestant, 1956 to 2023",
        'data source': 'https://github.com/Spijkervet/eurovision-dataset'
    }, {
        'week': 39, 'forum': 'https://community.plotly.com/t/figure-friday-2024-week-39/87572',
        'topic': "Quadrat-based monitoring of desert grassland vegetation at the Jornada Experimental Range, "
                 "New Mexico, 1915 to 2016",
        'data source': 'https://portal.edirepository.org/nis/mapbrowse?packageid=knb-lter-jrn.210351004.2'
    }, {
        'week': 38, 'forum': 'https://community.plotly.com/t/figure-friday-2024-week-38/87432',
        'topic': "US H-1B Visa Lottery Data, 2021 to 2024",
        'data source': 'https://github.com/BloombergGraphics/2024-h1b-immigration-data'
    }, {
        'week': 37, 'forum': 'https://community.plotly.com/t/figure-friday-2024-week-37/87233',
        'topic': "Child mortality rate, under age five, 1751 to 2022",
        'data source': 'https://www.gapminder.org/data/documentation/gd005/'
    }, {
        'week': 36, 'forum': 'https://community.plotly.com/t/figure-friday-2024-week-36/87101',
        'topic': "Air Quality of Cities Around the World from 1850 to 2021",
        'data source': 'https://airqualitystripes.info/about/'
    }, {
        'week': 35, 'forum': 'https://community.plotly.com/t/figure-friday-2024-week-35/86927',
        'topic': "People Map of the US",
        'data source': 'https://github.com/the-pudding/data/tree/master/people-map'
    }, {
        'week': 34, 'forum': 'https://community.plotly.com/t/figure-friday-2024-week-34/86692',
        'topic': "Spotify Tracks Exploration",
        'data source': 'https://www.kaggle.com/datasets/maharshipandya/-spotify-tracks-dataset/data'
    }, {
        'week': 33, 'forum': 'https://community.plotly.com/t/figure-friday-2024-week-33/86587',
        'topic': "US Elections from 1976 to 2020",
        'data source': 'https://www.kaggle.com/datasets/tunguz/us-elections-dataset/data?select=1976-2020-president.csv'
    }, {
        'week': 32, 'forum': 'https://community.plotly.com/t/figure-friday-2024-week-32/86401',
        'topic': "Gender Pay Gap in Ireland",
        'data source': 'https://paygap.ie/downloads'
    }, {
        'week': 31, 'forum': 'https://community.plotly.com/t/figure-friday-2024-week-31/86264',
        'topic': "Stack Overflow Annual Developer Survey",
        'data source': 'https://survey.stackoverflow.co/'
    }, {
        'week': 30, 'forum': 'https://community.plotly.com/t/figure-friday-2024-week-30/86083',
        'topic': "Rural Investments in the US in 2024",
        'data source': 'https://www.rd.usda.gov/rural-data-gateway/rural-investments/data'
    }, {
        'week': 29, 'forum': 'https://community.plotly.com/t/figure-friday-2024-week-29/85928',
        'topic': "English Women’s Football league",
        'data source': 'https://x.com/rob_clapp'
    }, {
        'week': 28, 'forum': 'https://community.plotly.com/t/figure-friday-2024-week-28/84980',
        'topic': "Sample Superstore’s Sales and Profits",
        'data source': 'https://workout-wednesday.com/2024w28tab/'
    },
]

home_table = html.Div(
    html.Table(
        [
            html.Thead(
                html.Tr([
                    html.Th('/ WEEK', style={'padding-left': 10, 'width': 150}),
                    html.Th('/ TOPIC'),
                    html.Th('/ DATA SOURCE', style={'padding-right': 10}),
                ], style={'font-size': 18, 'font-family': 'Neue Regrade', 'border-bottom': '2px solid'})
            ),
            html.Tbody(
                [
                    html.Tr(
                        [
                            html.Td(
                                [
                                    DashIconify(icon="pepicons-pencil:square-filled", width=11, className='me-2'),
                                    html.A(row['week'], href=row['forum'], target='_blank', className='fw-bold')
                                ], style={'padding-left': 10, 'width': 150}
                            ),
                            html.Td(
                                row['topic'],
                                className='fw-bold'
                            ),
                            html.Td(
                                html.A(
                                    DashIconify(icon="iconamoon:arrow-top-right-1-thin", width=50),
                                    href=row['data source'], target='_blank'
                                ), style={'text-align': 'right'}
                            ),
                        ], style={'font-size': 20, 'font-family': 'Inter'}
                    ) for row in home_table_data]
            )  # loop for rows
        ]
    ), id='home-table', className='d-flex flex-column overflow-y-hidden',
    style={'max-height': 450, 'max-width': 1000, 'transition': 'max-height 1s'}
)

home_part2 = html.Div([
    html.Div("FIGURE FRIDAY EDITIONS", style={'font-size': 72, 'font-family': 'Neue Regrade'}),
    html.Div([
        html.Div([
            home_table,
            dmc.Button(
                "SHOW MORE", id='home-show-more-btn', fullWidth=True, variant="subtle", color='var(--bs-body-color)',
                leftSection=DashIconify(icon="bi:chevron-down", id='collapse-home-table-btn-icon'),
                style={'font-size': 18, 'font-family': 'Neue Regrade'}
            )
        ], className='d-flex flex-column'),
    ], className='d-flex justify-content-center'),
], className='d-flex flex-column p-5')


@callback(
    Output("collapse-home-table-btn-icon", "flip"),
    Output("home-table", "style"),
    Input("home-show-more-btn", "n_clicks"),
    prevent_initial_call=True
)
def collapse_home_table(n_clicks):
    table_style_patch = Patch()
    table_style_patch['max-height'] = 1500 if n_clicks % 2 else 450
    return (
        "vertical" if n_clicks % 2 else None,
        table_style_patch
    )
