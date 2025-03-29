import os
from collections import defaultdict

from dash import dcc, html, Input, Output, callback, page_registry, ALL, ctx
import dash_mantine_components as dmc
from dotenv import load_dotenv

load_dotenv()


def main_app_navbar():
    # Group pages by year
    pages_by_year = defaultdict(list)

    for page in page_registry.values():
        # Extract year from path (format: '/YYYY/Wxx')
        path_parts = page['path'].strip('/').split('/')
        if len(path_parts) >= 2 and path_parts[0].startswith('20'):  # Ensure it's a year/week path
            year = path_parts[0]
            pages_by_year[year].append(page)

    # Sort years in descending order (newest first)
    sorted_years = sorted(pages_by_year.keys(), reverse=True)

    accordion_items = []

    for year in sorted_years:
        year_pages = sorted(pages_by_year[year], key=lambda p: p['path'], reverse=True)

        nav_links = []
        for page in year_pages:
            nav_links.append(
                dmc.HoverCard(
                    [
                        dmc.HoverCardTarget(
                            dmc.NavLink(
                                id={'type': 'navlink', 'index': page['path']},
                                disabled=page.get('disabled', False),
                                label=page['name'],
                                href=os.getenv('DASH_URL_BASE_PATHNAME', '/') + page['path'].lstrip('/'),
                                color='var(--bs-primary)', variant="filled", fw=500, noWrap=True,
                                styles={"body": {"textAlign": "center"}}
                            ),
                        ),
                        dmc.HoverCardDropdown(
                            [
                                html.Div(page['title'], className='border-bottom border-primary fs-4 text-center'),
                                dcc.Markdown(page.get('description', ''), className='pt-2'),
                                dmc.Image(
                                    radius="md",
                                    src=os.getenv('DASH_URL_BASE_PATHNAME', '/') + page['image']
                                ) if page.get('image') else None,
                                dcc.Markdown(page.get('data_source', ''), className='pt-2'),
                            ],
                            bg='var(--bs-body-bg)',
                            w=600
                        ),
                    ],
                    withArrow=True,
                    position="right",
                    shadow="md",
                    openDelay=500,
                    zIndex=500,
                    transitionProps={'duration': 300, 'transition': 'scale-x'}
                )
            )

        accordion_items.append(
            dmc.AccordionItem(
                [
                    dmc.AccordionControl(f"{year}"),
                    dmc.AccordionPanel(nav_links)
                ],
                value=year
            )
        )

    return html.Div([
        dmc.Accordion(
            accordion_items,
            value=sorted_years if sorted_years else [],  # Open the most recent year by default
            multiple=True,
            styles={'control': {'padding': '0px 10px'}, 'label': {'padding': '8px 0px'}, 'content': {'padding': 0}}
        )
    ], className='d-flex flex-column bg-body z-3 border-end border-primary border-2 mb-2',
        style={'width': 80, 'min-width': 80, 'flex-shrink': 0,
               'background': 'var(--bs-body-bg)', 'overflow-y': 'auto'},
    )


@callback(
    Output({'type': 'navlink', 'index': ALL}, 'active'),
    Input('current-url-location', 'pathname')
)
def update_active_nav_link(url):
    # Update to handle the new URL structure (year/week)
    current_path = '/' + url.strip('/')
    return [output['id']['index'] == current_path for output in ctx.outputs_list]
