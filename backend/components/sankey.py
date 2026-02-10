import plotly.graph_objects as go
import pandas as pd


def _stack_cols(df, col_list, vals):
    """ Stack columns from input column list
        making first column src and second column targ
        then making second column src and third column targ
        and so on
        add vals to each row
    """
    # create empty dataframe
    stacked = pd.DataFrame()

    # turn all items in dataframe to string
    df = df.astype(str)

    # iterate through all columns and create dataframe with column i and column i + 1
    for i in range(len(col_list) - 1):
        stv_stacked = df[[col_list[i], col_list[i + 1]]]

        # rename columns and add values
        stv_stacked.columns = ['src', 'targ']
        stv_stacked['vals'] = vals

        # concat each iteration of columns into a stacked dataframe
        stacked = pd.concat([stacked, stv_stacked], axis=0, ignore_index=True)

    # turn valus to list and return stacked dataframe and values
    values = stacked['vals'].tolist()
    return stacked, values


def _code_mapping(df, src, targ):
    """ Map labels in src and targ to integers """

    # get distinct labels
    labels = sorted(set(list(df[src]) + list(df[targ])))

    # get integer codes
    codes = list(range(len(labels)))

    # create label to code mapping
    lc_map = dict(zip(labels, codes))

    # substitute names for codes in the dataframe
    df = df.replace({src: lc_map, targ: lc_map})

    return df, labels


def make_sankey(df, col_list, vals=None):
    """

    :param df: Dataframe containing columns in column list
    :param col_list: Target colum of labels
    :param vals: Thickness of the link for each row
    :return: Generates a Sankey diagram using columns from col_list contained in df with values from vals
    """

    # assign values to vals or if not vals are provided assign all values to 1
    if vals:
        values = df[vals]
    else:
        values = [1] * len(df)  # all 1's

    # generate stacked df and assign values using _stack_cols
    stacked, values = _stack_cols(df, col_list, values)

    # take labels from df and map them to labels
    df, labels = _code_mapping(stacked, 'src', 'targ')

    # set up Sankey diagram using stacked df, vals, and labels
    link = {'source': df['src'], 'target': df['targ'], 'value': values}
    node = {'label': labels}

    # generate Sankey diagram
    sk = go.Sankey(link=link, node=node)
    fig = go.Figure(sk)

    return fig