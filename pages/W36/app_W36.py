from dash import Dash, dcc, html, Input, Output, register_page, clientside_callback, _dash_renderer, callback
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash_iconify import DashIconify

import pages.W36.components as components
from pages.W36.config_W36 import pollution_levels

md_levels_info = [
    html.Div([
        html.Span(f'{level}:', style={'font-size': 16, 'color': pollution_levels[level]['color']}), html.Br(),
        pollution_levels[level]['description'], html.Br(), html.Br(),
    ]) for level in pollution_levels
]

bar_header_controls = [
    'Top ',
    dmc.NumberInput(
        id='pollution-top-less-bar-input', variant='unstyled', value=10, min=0, w=50,
        size='xs',
        classNames={"input": 'fw-bold fs-5 text-primary text-center text-decoration-underline'},
        styles={"input": {'font-family': 'Source Sans Pro', }},
    ),
    ' Less and ',
    dmc.NumberInput(
        id='pollution-top-most-bar-input', variant='unstyled', value=10, min=0, w=50,
        size='xs',
        classNames={"input": 'fw-bold fs-5 text-primary text-center text-decoration-underline'},
        styles={"input": {'font-family': 'Source Sans Pro'}},
    ),
    ' Most Polluted Cities in ',
    html.Span(id='pollution-bar-header-year', className='fw-bold text-primary ms-1')
]

layout_W36 = html.Div([
    # pollution levels info
    dmc.Drawer(
        md_levels_info,
        id="levels-info-drawer",
        title="Pollution Levels Description",
        zIndex=10000,
        styles={
            'title': {'flex': 1, 'text-align': 'center', 'font-size': 20, 'font-weight': 700},
            'header': {'display': 'flex', 'border-bottom': '2px solid var(--bs-secondary)'}
        },
    ),
    # Upper cards
    html.Div([
        # Map
        dbc.Card([
            dbc.CardHeader([
                dmc.Tooltip(
                    label="Pollution Levels Description",
                    position="right", withArrow=True,
                    children=dmc.ActionIcon(
                        DashIconify(icon='clarity:info-line', width=25),
                        id="level-info-map-btn",
                        variant="transparent", color='var(--bs-primary)')
                ),
                html.Div(id='pollution-map-title', className='flex-fill fs-5 text-body text-center'),
            ], className='d-flex align-items-center'),
            dbc.CardBody(components.pollution_map_graph, className='p-2'),
        ], className='flex-fill', style={'min-width': 300}),
        # Bars
        dbc.Card([
            dbc.CardHeader(bar_header_controls, id='pollution-bar-title',
                           className='d-flex justify-content-center fs-5 text-body text-nowrap'),
            dbc.CardBody(components.pollution_top_bar_graph, className='p-2'),
        ], className='flex-fill', style={'min-width': 300}),
    ], className='h-50 d-flex flex-wrap overflow-auto gap-2', style={'min-height': 400}),
    html.Span('Select the Year for the Map and the Bar Plot Above:', className='text-muted', style={'font-size': 14}),
    dcc.Slider(
        id="year-pollution-slider",
        min=1850, max=2021, step=1, value=2021,
        marks={v: {'label': str(v)} for v in [1850 + i * 25 for i in range(7)]} | {2021: {'label': "2021"}},
        tooltip={"placement": "bottom", "always_visible": True},
        className='dbc mb-2'
    ),
    # lines
    dbc.Card([
        dbc.CardHeader([
            dmc.Tooltip(
                label="Pollution Levels Description",
                position="right", withArrow=True,
                children=dmc.ActionIcon(
                    DashIconify(icon='clarity:info-line', width=25),
                    id="level-info-line-btn",
                    variant="transparent", color='var(--bs-primary)')
            ),
            html.Div([
                'Historical PM2.5 Concentration from ',
                html.Span('1850', className='fw-bold text-primary'), ' to ',
                html.Span('2021', className='fw-bold text-primary')
            ], className='flex-fill fs-5 text-body text-center'),
        ], className='d-flex align-items-center'),
        dbc.CardBody(components.pollution_historic_line, className='p-2'),
    ], className='flex-fill overflow-auto', style={'min-width': 300, 'min-height': 400}),

], className='flex-fill d-flex flex-column p-2 overflow-auto')


@callback(
    Output('pollution-map-title', 'children'),
    Input('year-pollution-slider', "value"),
    Input('pollution-map-labels-chk', "checked"),
    Input("pollution-map-markers-chk", "checked"),
)
def update_pollution_map_card_header(year, show_labels, show_markers):
    text = []
    if show_markers:
        text += ['Annual Mean PM2.5 Concentration in ', html.Span(year, className='fw-bold text-primary')]
        if show_labels and year != 1850:
            text += [' and Evolution Compare to ', html.Span(year - 1, className='fw-bold text-primary')]
    elif show_labels and year != 1850:
        text += [
            'Evolution of the Annual Mean PM2.5 Concentration between ',
            html.Span(year - 1, className='fw-bold text-primary'),
            ' and ', html.Span(year, className='fw-bold text-primary')
        ]
    else:
        text.append('Annual Mean PM2.5 Concentration')
    text.append(' (µg/m³)')
    return text


@callback(
    Output('pollution-bar-header-year', 'children'),
    Input('year-pollution-slider', "value"),
)
def update_pollution_bar_card_header_year(year):
    return year


@callback(
    Output("levels-info-drawer", "opened"),
    Input("level-info-line-btn", "n_clicks"),
    Input("level-info-map-btn", "n_clicks"),
    prevent_initial_call=True,
)
def open_levels_info_drawer(*_):
    return True


if __name__ == '__main__':
    # for local development
    from dash_bootstrap_templates import ThemeChangerAIO

    _dash_renderer._set_react_version("18.2.0")

    dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"

    app = Dash(
        external_stylesheets=[dbc.themes.SOLAR, dbc_css],
        url_base_pathname='/',
    )

    app.layout = dmc.MantineProvider(
        html.Div([
            html.Div([
                dmc.Switch(
                    id='color-mode-switch',
                    offLabel=DashIconify(icon="radix-icons:moon", width=20),
                    onLabel=DashIconify(icon="radix-icons:sun", width=20),
                    size="lg", color='var(--bs-primary)',
                    styles={"track": {'border': '2px solid var(--bs-primary)'}},
                ),
                ThemeChangerAIO(
                    aio_id="theme",
                    radio_props=dict(value=dbc.themes.SOLAR),
                    button_props=dict(outline=False, color="primary"),
                ),
            ], className='d-inline-flex gap-2'),
            layout_W36
        ], className='vh-100 d-flex flex-column')
    )

    # Switch color-theme for DBC and DMC components
    clientside_callback(
        """
        (switchOn) => {
           document.documentElement.setAttribute('data-bs-theme', switchOn ? 'light' : 'dark');
           document.documentElement.setAttribute('data-mantine-color-scheme', switchOn ? 'light' : 'dark');
           return window.dash_clientside.no_update
        }
        """,
        Output("color-mode-switch", "id"),
        Input("color-mode-switch", "checked"),
    )

    app.run(debug=True)
else:
    # for the main Figure Friday app
    register_page(
        __name__,
        path="/W36",
        name="W36",  # used as label for the main app navlink
        title="Air Quality of Cities Around the World from 1850 to 2021",
        description='Air quality around the globe has gone through significant ups and downs since the Industrial '
                    'Revolution. Many factors affect the air that we breath such as the usage of coal power plants, '
                    'clean air legislation, and automobile congestion. From the Air Quality Stripes project, we will '
                    'analyse the concentration of particulate matter air pollution (PM2.5) in cities around the world.',
        image="assets/W36.jpg",  # used by the tooltip for the main app navbar
        data_source='*Data Source: [Air Quality Stripes](https://airqualitystripes.info/about/)*',
        disabled=False,
    )
    layout = html.Div([
        layout_W36
    ], className='h-100 d-flex')
