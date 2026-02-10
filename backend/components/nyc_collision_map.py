from nyc_open_data_api import NYCOpenDataAPI
import plotly.express as px
import components.sankey as sk


def generate_nyc_map(df, lat, long, yr_start=2012, yr_end=2023, boroughs=None):
    """
    :param df: given pandas df containing 'borough' column
    :param lat: name of latitude column
    :param long: name of longitude column
    :param yr_start: start year of map
    :param yr_end: end year of map
    :param boroughs: selected boroughs of map
    :return: returns a plotly scatter mapbox figure centered on NYC with data filtered by params
    """

    # use class filter function to get requested data
    filtered_df = NYCOpenDataAPI.filter_by_year_and_borough(df, yr_start=yr_start, yr_end=yr_end, boroughs=boroughs)

    # find total crashes by borough for future use in annotation
    total_crashes = len(filtered_df)
    total_crashes_by_borough = {}
    for borough in boroughs:
        crashes_in_borough = len(filtered_df[filtered_df['borough'] == borough])
        total_crashes_by_borough[borough] = crashes_in_borough

    # set what info is displayed when a user hovers over each point
    hover_data = {
        'latitude': False,
        'longitude': False,
        'borough': False
    }

    # create a scatter mapbox plot with Plotly Express
    fig = px.scatter_mapbox(filtered_df, lat=lat, lon=long, zoom=10, hover_data=hover_data,
                            color='borough', hover_name='on_street_name')

    # assign custom size to points on map to reduce the size
    fig.update_traces(marker={'size': 3.25})

    # Update layout to set Mapbox style and focus on New York City
    fig.update_layout(
        mapbox_style='carto-positron',  # Use the Mapbox map style
        mapbox_zoom=10,  # Adjust zoom level as needed
        mapbox_center={'lat': 40.7128, 'lon': -74.0060},  # Coordinates for New York City
        legend=dict(
            title='Borough:',
            orientation='h',
            xanchor='center',
            x=0.5,
            yanchor='top',
            y=1.1,
            traceorder='normal'
        )
    )
    # always have at least one annotation for height calculation
    max_annotations = max(len(boroughs), 1)

    # determine the space needed for all selected boroughs annotation
    total_annotation_height = max_annotations * 0.03

    # iterate over both index and borough to use index to determine place in stack and borough for total collisions
    for i, borough in enumerate(boroughs):
        borough_crashes = total_crashes_by_borough.get(borough, 0)
        fig.add_annotation(
            text=f"{borough}: {borough_crashes}",
            x=0,
            # set the start of the stack of texts just under the total collision count and adjust distance of following
            # annotations based on total number of boroughs
            y=0.98 - total_annotation_height + i * (total_annotation_height / max_annotations),
            showarrow=False,
            font=dict(size=14, color='rgba(30, 30, 30, 1)'),
            bgcolor='rgba(255, 255, 255, 0.75)',  # set color, with opacity to 75%
            opacity=0.9
        )

    # annotate the total number of crashes
    fig.add_annotation(
        text=f"Total Collisions: {total_crashes}",
        x=0,
        y=1,
        showarrow=False,
        font=dict(size=24, color='black'),
        bgcolor='rgba(255, 255, 255, 0.75)',  # set color, with opacity to 75%
        opacity=0.9
    )
    return fig


def generate_sankey(df, cols, yr_start=2012, yr_end=2023, boroughs=None):
    """
    :param df: given pandas df containing 'borough' column
    :param cols: given list of column names of columns to group by
    :param yr_start: start year of map
    :param yr_end: end year of map
    :param boroughs: selected boroughs of map
    :return: returns a plotly sankey figure using given grouped data filtered by params
    """

    # use class filter function to get requested data
    filtered_df = NYCOpenDataAPI.filter_by_year_and_borough(df, yr_start=yr_start, yr_end=yr_end, boroughs=boroughs)

    # group data by specified columns
    grouped_df = filtered_df.groupby(cols).size().reset_index(name='count')

    # only include the top 20 counts for readability
    grouped_df = grouped_df.sort_values(by='count', ascending=False).head(10)

    fig = sk.make_sankey(grouped_df, cols, vals='count')

    return fig


def generate_hist(df, cols, yr_start=2012, yr_end=2023, boroughs=None):
    """
    :param df: given pandas df containing 'borough' column
    :param cols: given list of column names of columns to generate histogram of
    :param yr_start: start year of map
    :param yr_end: end year of map
    :param boroughs: selected boroughs of map
    :return: returns a plotly histogram figure using given columns filtered by the params
    """

    # use class filter function to get requested data
    filtered_df = NYCOpenDataAPI.filter_by_year_and_borough(df, yr_start=yr_start, yr_end=yr_end, boroughs=boroughs)

    if not isinstance(cols, list):
        cols = [cols]

    # generate a histogram figure with histograms of each element in col and normalize histograms to percentage
    fig = px.histogram(filtered_df, x=cols, histnorm='percent', barmode='overlay')

    # add a title and rename x-axis, y-axis, and legend
    fig.update_layout(title='Frequency Of Variables By Individual Vehicle Collision')
    fig.update_layout(xaxis_title='Value')
    fig.update_layout(yaxis_title='Frequency (%)')
    fig.update_layout(legend_title_text='Variable')

    # change font, and color
    fig.update_layout(title_font=dict(family='Roboto, sans-serif', size=20, color='rgba(30, 30, 30, 0.75)'),
                      title_x=0.5, title_y=0.93)

    # separate col names by each _ and capitalize each one
    renamed_cols = [col.replace('_', ' ').title() for col in cols]

    # iterate through variable names and rename them based on renamed_cols
    for i in range(len(fig.data)):
        fig.data[i].update(name=renamed_cols[i])

    return fig