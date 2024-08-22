from dash import html, dcc, Dash, register_page
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash_iconify import DashIconify

layout = html.Div([
    html.H1('This is our Home page'),
    html.Div('This is our Home page content.'),
])

if __name__ == "__main__":
    app = Dash(__name__, external_stylesheets=[dbc.themes.SOLAR])
    app.layout = html.Div(layout, className='vh-100')
    app.run(debug=True)
else:
    register_page(
        __name__,
        path='/',
        name=DashIconify(icon="ic:outline-home", width=25),
        title='Welcome to Plotly Figure Friday Project !'
    )
