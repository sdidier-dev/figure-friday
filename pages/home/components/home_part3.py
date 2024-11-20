from dash import dcc, html
import dash_bootstrap_components as dbc
from dash_iconify import DashIconify

md_text2 = """
While there are a few apps missing, I’m excited to share more with you soon!

All of my applications are organized within a global app using Dash’s multi-page layout. 
You can explore the code in my [GitHub repository](https://github.com/sdidier-dev/figure-friday). 
Each app is located under the **_/pages_** directory and is designed to run independently using the **_app_W*.py_** 
files.

I encourage you to dive in and use any part of the code that inspires you! Your feedback, whether it’s 
positive or constructive, is always appreciated.

**Note that this project is deployed on a home made Kubernetes cluster hosted on-premises using 3 Raspberry Pi 😁**
"""

contact_me_card = dbc.Card(
    [
        dbc.CardHeader(
            "CONTACT ME",
            className='bg-transparent border-bottom border-primary mx-4 text-center',
            style={'font-size': 18, 'font-family': 'Neue Regrade'}
        ),
        dbc.CardBody(
            [
                html.A(
                    DashIconify(icon="simple-icons:plotly", width=25),
                    href="https://community.plotly.com/u/skiks/summary", target="_blank"
                ),
                html.A(
                    DashIconify(icon="mdi:github", width=30),
                    href="https://github.com/sdidier-dev", target="_blank"
                ),
                html.A(
                    DashIconify(icon="ic:baseline-discord", width=30),
                    href="https://discordapp.com/users/1097920999426633848", target="_blank"
                ),
                html.A(
                    DashIconify(icon="ic:baseline-email", width=30),
                    href="mailto:sdidier.dev@gmail.com"
                )
            ], className='d-flex justify-content-evenly')
    ], className='contact-me-card bg-transparent mt-4 p-3', color="primary",
)

home_part3 = html.Div([
    html.Div([
        html.Div("MY APPS", style={'font-size': 72, 'font-family': 'Neue Regrade'}),

        html.Span([
            DashIconify(
                icon="fa-solid:hand-point-left",
                width=40
            ),
            html.Div(
                "You’ll find all the apps I’ve crafted, easily accessible through the left sidebar.",
                style={'font-size': 20, 'margin-left': 10}
            )
        ], className='d-flex align-items-center', style={'position': 'relative', 'left': -35}),

        dcc.Markdown(md_text2, style={'font-size': 20}),

        contact_me_card
    ], style={'width': 450}),

    html.Div(className='flex-fill')  # empty div to fill the remaining space

], className='d-flex p-5')
