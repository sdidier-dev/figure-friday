import pandas as pd
import dash_ag_grid as dag

df = pd.read_csv(
    # r'E:\Python\Projects\figure-friday\figure-friday\pages\W35\assets\people-map.csv',  # for dev
    'https://raw.githubusercontent.com/plotly/Figure-Friday/main/2024/week-35/people-map.csv',
)
df.dropna(subset=['views_sum'], inplace=True)
df.sort_values(by=['views_sum'], inplace=True, ascending=False)

columnDefs = [
    {'field': 'name_clean', 'headerName': 'People'},
    {
        'headerName': 'Place',
        'children': [{'field': 'state'}, {'field': 'city'}, {'field': 'neighborhood'}]
    },
    {'field': 'extract', 'headerName': 'Description', 'maxWidth': 1000, 'tooltipField': 'extract', 'flex': 1},
    {'field': 'views_sum', 'headerName': 'Total Views', "pinned": "right"},
]

defaultColDef = {
    'filter': True, "filterParams": {"buttons": ["reset"]}, "floatingFilter": True,
    'suppressHeaderMenuButton': True
}

dashGridOptions = {
    "headerHeight": 30,
    "floatingFiltersHeight": 30,
    'tooltipShowDelay': 1000,
}

people_grid = dag.AgGrid(
    id="people-grid",
    rowData=df.to_dict("records"),
    columnDefs=columnDefs,
    defaultColDef=defaultColDef,
    dashGridOptions=dashGridOptions,
    columnSize="autoSize",
    style={"height": None},
    className='ag-theme-alpine flex-fill'
)
