from dash import html, dcc

md_text1 = """
Plotly launched a weekly initiative: 
[Figure Friday](https://community.plotly.com/t/announcing-plotly-weekly-data-viz-projects-figure-friday/84953) !

Each Friday, a new dataset is released with a sample figure. The aim is to gain insights from the data creating amazing
visualisations.

Everyone is welcome to participate, on the Forum or on the [Plotly Discord channel](https://discord.gg/Pa8scsgepB),
to share ideas, results and foster collaboration with the community, providing support or seeking help, to grow
together.

After one week, just before the release of the new dataset, everyone can join
the [Figure Friday Session](https://us06web.zoom.us/meeting/register/tZIuceqhqT4iHNS1T-23AWqtxmFKaCRlwTUq#/registration)
on Zoom to share and watch final creations and have final feedbacks and conclusion about the good, the bad (and the
ugly?) of the current week project.
"""

home_part1 = html.Div([
    html.Div("FIGURE",
             style={'font-size': 180, 'font-family': 'Neue Regrade', 'line-height': 180},
             className='text-end'),
    html.Div("FRIDAY",
             style={'font-size': 180, 'font-family': 'Neue Regrade', 'line-height': 180},
             className='text-end'),
    dcc.Markdown(md_text1, style={'width': 420, 'font-size': 20}),
], className='d-inline-flex flex-column align-items-end p-5')
