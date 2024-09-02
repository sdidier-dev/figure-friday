import os

from dash import dcc, html, Input, Output, callback, page_registry, ALL, ctx
import dash_mantine_components as dmc
from dotenv import load_dotenv

load_dotenv()


def main_app_navbar():
    return html.Div([
        dmc.HoverCard([
            dmc.HoverCardTarget(
                dmc.NavLink(
                    id={'type': 'navlink', 'index': page['path']},
                    disabled=page.get('disabled', False),
                    label=page['name'],
                    # DASH_URL_BASE_PATHNAME needs a trailing '/', so must be removed from page['path']
                    href=os.getenv('DASH_URL_BASE_PATHNAME', '') + page['path'][1:],
                    color='var(--bs-primary)', variant="filled", fw=500, noWrap=True,
                ),
            ),
            dmc.HoverCardDropdown([
                html.Div(page['title'], className='border-bottom border-primary fs-4 text-center'),
                dcc.Markdown(page['description'], className='pt-2'),
                dmc.Image(radius="md", src=page['image']),
                dcc.Markdown(page.get('data_source', None), className='pt-2'),
            ], bg='var(--bs-body-bg)', w=600),
        ], withArrow=True, position="right", shadow="md", openDelay=500, zIndex=500,
            transitionProps={'duration': 300, 'transition': 'scale-x'})
        for page in page_registry.values()
        # Note: add class z-3 and background so that the controls drawer is behind the navbar when collapsed
    ], className='d-flex flex-column z-3 border-end border-primary border-2 mb-2',
        style={'width': 60, 'background': 'var(--bs-body-bg)'})


@callback(
    Output({'type': 'navlink', 'index': ALL}, 'active'),
    Input('current-url-location', 'pathname')
)
def update_active_nav_link(url):
    return [output['id']['index'] == f"/{url.split('/')[-1]}" for output in ctx.outputs_list]
