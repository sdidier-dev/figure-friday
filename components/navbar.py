import os

from dash import html, Input, Output, callback, page_registry, ALL, ctx
import dash_mantine_components as dmc
from dotenv import load_dotenv

load_dotenv()


def main_app_navbar():
    return html.Div([
        dmc.HoverCard([
            dmc.HoverCardTarget(
                dmc.NavLink(
                    id={'type': 'navlink', 'index': page['path']},
                    label=page['name'],
                    # DASH_URL_BASE_PATHNAME needs a trailing '/', so must be removed from page['path']
                    href=os.getenv('DASH_URL_BASE_PATHNAME') + page['path'][1:],
                    # description=page['title'],
                    color='var(--bs-primary)', variant="filled", fw=500, noWrap=True,
                ),
            ),
            dmc.HoverCardDropdown([
                html.Div(page['title'], className='fs-4 text-center'),
                dmc.Image(radius="md", src=page['image']),
            ], bg='var(--bs-body-bg)'),
        ], withArrow=True, position="right", shadow="md", openDelay=500,
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
