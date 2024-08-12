import pandas as pd

from dash import dcc, html, Input, Output, callback, no_update
from dash_bootstrap_templates import ThemeChangerAIO, template_from_url
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

# Dash components
program_details_controls = html.Div([
    html.Div('Display only top (0 = All):'),
    html.Div([
        dbc.Input(
            id='input-program-details-top-prog-area', type="number", value=5, min=0, step=1,
            style={'width': 70}, className='text-end'
        ),
        html.Div('Program Area', className='text-nowrap flex-fill'),
        dbc.Input(
            id='input-program-details-top-prog', type="number", value=5, min=0, step=1,
            style={'width': 70}, className='text-end'),
        html.Div('Program', className='text-nowrap flex-fill'),
        dbc.Input(
            id='input-program-details-top-NAICS', type="number", value=5, min=0, step=1,
            style={'width': 70}, className='text-end'),
        html.Div('NAICS Industry Secctor', className='text-nowrap flex-fill'),
    ], className='d-inline-flex align-items-center'),
    dbc.Checkbox(id="chk-program-details-hide-labels", label="Hide labels"),
])

program_details_graph = dcc.Graph(
    id='graph-program-details',
    config=dict(responsive=True),
    className='flex-fill'
)


# internal function to have nicer labels for the parcats fig
def _add_line_breaks(label, max_length=25, max_lines=None):
    new_label, length, line = label.split()[0], len(label.split()[0]), 1
    for word in label.split()[1:]:
        if length + len(' ' + word) <= max_length:
            new_label += ' ' + word
            length += len(' ' + word)
        else:
            line += 1
            if max_lines and line > max_lines:
                new_label = new_label[:-3] + '...'
                return new_label
            else:
                new_label += '<br>' + word
                length = 0
    return new_label


# Note: can't use a patch while modifying the theme, the fig must be fully regenerated
@callback(
    Output("graph-program-details", "figure"),
    Input("grid-data", "virtualRowData"),
    Input("input-program-details-top-prog-area", "value"),
    Input("input-program-details-top-prog", "value"),
    Input("input-program-details-top-NAICS", "value"),
    Input("chk-program-details-hide-labels", "value"),
    Input(ThemeChangerAIO.ids.radio("theme"), "value"),
    Input("color-mode-switch", "value"),
    prevent_initial_call=True
)
def update_program_details(virtual_data, top_prog_area, top_prog, top_naics, hide_labels, theme, switch_on):
    if not virtual_data:
        return no_update

    dims = ['Program Area', 'Program', 'NAICS Industry Sector']
    dff = pd.DataFrame(virtual_data, columns=dims + ['Investment Dollars'])
    dff = dff.groupby(dims).sum().reset_index()

    top_nb = {'Program Area': top_prog_area, 'Program': top_prog, 'NAICS Industry Sector': top_naics}

    top_cats = {}
    for dim in dims:
        df_grouped = dff[[dim, 'Investment Dollars']].groupby(dim).sum()
        df_grouped = df_grouped.sort_values('Investment Dollars', ascending=False).reset_index()

        top_cats[dim] = df_grouped[dim].head(top_nb[dim] or len(df_grouped[dim])).to_list()
        dff[dim] = dff[dim].apply(lambda row: row if row in top_cats[dim] else 'Other')

    fig = go.Figure()
    fig.add_parcats(
        dimensions=[
            {
                'label': dim,
                'values': dff[dim],
                'categoryorder': "array",
                'categoryarray': top_cats[dim] + ['Other'],
                'ticktext': ['' if hide_labels else _add_line_breaks(cat, max_lines=2) for cat in top_cats[dim]] + [
                    '' if hide_labels else 'Other']
            } for dim in ['Program Area', 'Program', 'NAICS Industry Sector']
        ],
        counts=dff['Investment Dollars'],
        line_shape='hspline',
        labelfont_size=16,
        tickfont_size=14,
        hovertemplate="<b>%{category}</b><br>"
                      "Investments: %{count:$,}<br>"
                      "%{probability:.0%} of overall investments",
        line_hovertemplate="Investments: %{count:$,}<br>"
                           "%{probability:.0%} of overall investments",
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        margin={"r": 120, "t": 20, "l": 120, "b": 10},
        template=f"{template_from_url(theme)}{'' if switch_on else '_dark'}",
    )

    return fig
