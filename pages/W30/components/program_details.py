from dash import dcc, html, Input, Output, callback, no_update
from dash_bootstrap_templates import ThemeChangerAIO, template_from_url
import dash_mantine_components as dmc
import plotly.graph_objects as go
import pandas as pd

program_details_graph = html.Div([
    dmc.LoadingOverlay(
        id="graph-program-loading-overlay",
        visible=True,
        loaderProps={"type": "bars", "color": "var(--bs-primary)"},
        overlayProps={"radius": "sm", "blur": 2},
    ),
    dcc.Graph(
        id='graph-program-details',
        responsive=True,
        className='h-100'
    )
], className='h-100', style={'position': 'relative'})


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
    Output("graph-program-loading-overlay", "visible"),
    Input("grid-data", "virtualRowData"),
    Input("input-program-details-top-prog-area", "value"),
    Input("input-program-details-top-prog", "value"),
    Input("input-program-details-top-NAICS", "value"),
    Input("chk-program-details-hide-labels", "checked"),
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
    # Note: False is to hide the loader when the fig is ready
    return fig, False