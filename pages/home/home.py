from dash import html, dcc, Dash, register_page
import dash_bootstrap_components as dbc

layout = html.Div([
    html.H1('This is our Home page'),
    html.Div('This is our Home page content.'),
])

if __name__ == "__main__":
    app = Dash(__name__, external_stylesheets=[dbc.themes.SOLAR])
    app.layout = html.Div(layout, className='vh-100')
    app.run(debug=True)
else:
    register_page(__name__, path='/', title='test home page')