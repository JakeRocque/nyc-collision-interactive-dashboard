import os
from dotenv import load_dotenv

import argparse

import pandas as pd

import components.nyc_collision_map as nd
from nyc_open_data_api import NYCOpenDataAPI

from dash import Dash, dcc, html, Input, Output, State
import dash_bootstrap_components as dbc


load_dotenv()

URL = 'https://data.cityofnewyork.us/resource/h9gi-nx95.csv'
KEY = os.getenv('NYC_API_KEY')
COLUMNS = ['crash_date',
           'crash_time',
           'borough',
           'latitude',
           'longitude',
           'on_street_name',
           'contributing_factor_vehicle_1',
           'vehicle_type_code1',
           'number_of_persons_injured',
           'number_of_persons_killed']
CACHE_FILE = 'collision_data.parquet'


def parse_args():
    """
    :return: returns parsed command line arguments for dashboard configuration
    """
    parser = argparse.ArgumentParser(description='NYC Motor Vehicle Collision Dashboard')

    parser.add_argument('--url', type=str, default='https://data.cityofnewyork.us/resource/h9gi-nx95.csv',
                        help='NYC Open Data API URL')
    parser.add_argument('--key', type=str, default=os.getenv('NYC_API_KEY'),
                        help='NYC Open Data API key')
    parser.add_argument('--limit', type=int,
                        default=50000 if os.getenv('RENDER') else 250000,
                        help='Number of rows to fetch from the API')
    parser.add_argument('--yr-start', type=int, default=2024,
                        help='Default start year for the year range slider')
    parser.add_argument('--yr-end', type=int, default=2025,
                        help='Default end year for the year range slider')
    parser.add_argument('--refresh', action='store_true', default=False,
                    help='Force refresh data from API, ignoring cache')
    parser.add_argument('--port', type=int, default=8050,
                        help='Port to run the dashboard on')
    parser.add_argument('--debug', action='store_true', default=True,
                        help='Run in debug mode')
    parser.add_argument('--no-debug', action='store_false', dest='debug',
                        help='Run without debug mode')

    return parser.parse_known_args()[0]

args = parse_args()

# initialize the API
api = NYCOpenDataAPI(args.url, args.key)

# if data cached, retrieve it, else
# fetch and clean the relevant data
if os.path.exists(CACHE_FILE) and not args.refresh:
    print('Loading from cache...')
    df = pd.read_parquet(CACHE_FILE)
else:
    print('Fetching from API...')
    data = api.fetch_data(columns=COLUMNS, limit=args.limit)
    df = api.process_strings(data)
    df['crash_time'] = api.convert_time_col_to_ranges(df, 'crash_time')
    df['crash_date'] = pd.to_datetime(df['crash_date'])
    df.to_parquet(CACHE_FILE)

# initialize plotly dashboard and server
app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY], assets_folder='../frontend/assets')
server = app.server  # start server

app.layout = dbc.Container([

    # Row 1: Title
    dbc.Row(
        dbc.Col(
            html.H1('Motor Vehicle Collisions NYC, By Individual Collision',
                    className='dashboard-title')
        ), className='mb-3'
    ),

    # Store the currently toggled boroughs
    dcc.Store(id='active_boroughs', data=df['borough'].dropna().unique().tolist()),

    # Row 2: Year Range Slider
    dbc.Row(
        dbc.Col([
            html.Label('Select Year Range:', className='dashboard-label'),
            dcc.RangeSlider(
                id='year_range_slider',
                min=df['crash_date'].min().year,
                max=df['crash_date'].max().year,
                step=1,
                marks={year: str(year) for year in range(
                    df['crash_date'].min().year,
                    df['crash_date'].max().year + 1)},
                value=[args.yr_start, args.yr_end],
                tooltip={"placement": "bottom", "always_visible": True}
            )
        ], width=12), className='mb-3'
    ),

# Row 3: Full-width Map with Borough Toggle
dbc.Row(
    dbc.Col([
        dcc.Graph(id='nyc_map',
                className='graph-border',
                style={'height': '120vh'})
    ], width=12), className='mb-3'
),

    # Row 4: Sankey (left) | Histogram (right)
    dbc.Row([
        dbc.Col([
            dcc.Checklist(
                id='sankey_columns_checklist',
                options=[
                    {'label': ' Street Name', 'value': 'on_street_name'},
                    {'label': ' Contributing Factor', 'value': 'contributing_factor_vehicle_1'},
                    {'label': ' Vehicle Type', 'value': 'vehicle_type_code1'},
                    {'label': ' Time Of Collision', 'value': 'crash_time'}
                ],
                value=['contributing_factor_vehicle_1', 'vehicle_type_code1'],
                inline=True,
                className='dashboard-checklist'
            ),
            dcc.Graph(id='sankey_diagram',
                    className='graph-border',
                    style={'height': '50vh'})
        ], xs=12, lg=6),

        dbc.Col(
            dcc.Graph(id='histogram',
                    className='graph-border',
                    style={'height': '54vh'}),
            xs=12, lg=6
        )
    ], className='g-3')

], fluid=True)

# define the callback function for nyc_map with inputs determined by borough dropdown and year slider
@app.callback(
    Output('nyc_map', 'figure'),
    [Input('year_range_slider', 'value')],
    [State('active_boroughs', 'data')]
)
def update_nyc_map(selected_years, active_boroughs):
    """
    :param selected_years: years chosen through dashboard slider
    :return: updates the nyc_map based on dashboard inputs
    """
    all_boroughs = df['borough'].dropna().unique().tolist()
    return nd.generate_nyc_map(df, 'latitude', 'longitude', yr_start=selected_years[0],
                            yr_end=selected_years[1], boroughs=all_boroughs)

@app.callback(
    Output('active_boroughs', 'data'),
    [Input('nyc_map', 'restyleData')],
    [State('active_boroughs', 'data'),
    State('nyc_map', 'figure')]
)
def update_active_boroughs(restyle_data, current_boroughs, figure):
    if not restyle_data or 'visible' not in restyle_data[0]:
        return current_boroughs

    visible = restyle_data[0]['visible']
    indices = restyle_data[1]
    traces = figure['data']

    active = current_boroughs.copy()
    for j, i in enumerate(indices):
        name = traces[i]['name']
        if visible[j] == 'legendonly' or visible[j] is False:
            active = [b for b in active if b != name]
        elif name not in active:
            active.append(name)

    return active

# define the callback function for sankey_diagram
# with inputs determined by borough dropdown, year slider, and sankey columns checklist
@app.callback(
    Output('sankey_diagram', 'figure'),
    [Input('year_range_slider', 'value'),
        Input('sankey_columns_checklist', 'value'),
        Input('active_boroughs', 'data')]
)
# define a function to actively update the histogram based on selected boroughs and years
def update_sankey_diagram(selected_years, selected_columns, active_boroughs):
    """
    :param selected_years: years chosen through dashboard slider
    :param selected_columns: columns selected for Sankey diagram
    :param active_boroughs: currently toggled boroughs
    :return: updates the sankey_diagram based on dashboard inputs
    """

    # account for if less than two variables are selected and display text asking to select more
    if len(selected_columns) < 2:
        return {
            'data': [],
            'layout': {
                'annotations': [{
                    'text': 'Sankey: Please select two or more variables',
                    'showarrow': False,
                    'font': {'size': 18}
                }],
                'xaxis': {'visible': False},
                'yaxis': {'visible': False}
            }
        }
    else:

        # return the generate sankey function with new inputs
        return nd.generate_sankey(df, cols=selected_columns,
                                    yr_start=selected_years[0], yr_end=selected_years[1],
                                    boroughs=active_boroughs)

# define the callback function for histogram with inputs determined by borough dropdown and year slider
@app.callback(
    Output('histogram', 'figure'),
    [Input('year_range_slider', 'value'),
        Input('active_boroughs', 'data')]
)
# define a function to actively update the histogram based on selected boroughs and years
def update_histogram(selected_years, active_boroughs):
    """
    :param selected_years:
    :param active_boroughs: currently toggled boroughs
    :return: updates the histogram based on dashboard inputs
    """

    # return the generate histogram function with new inputs
    return nd.generate_hist(df, cols=['number_of_persons_injured', 'number_of_persons_killed'],
                            yr_start=selected_years[0], yr_end=selected_years[1],
                            boroughs=active_boroughs)

if __name__ == "__main__":
    app.run(debug=args.debug, port=args.port, use_reloader=False)