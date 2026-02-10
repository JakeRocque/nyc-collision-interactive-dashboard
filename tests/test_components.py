# """
# Test each component of the NYC Collision Dashboard independently.
# Run individual test functions to isolate issues.

# Usage:
#     python tests/test_components.py api        # Test API fetch
#     python tests/test_components.py clean      # Test data cleaning
#     python tests/test_components.py map        # Test map generation
#     python tests/test_components.py sankey     # Test sankey generation
#     python tests/test_components.py hist       # Test histogram generation
#     python tests/test_components.py all        # Test everything step by step
# """

# import sys
# import os

# # Add project root to path so imports work from the tests/ folder
# PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sys.path.insert(0, PROJECT_ROOT)
# sys.path.insert(0, os.path.join(PROJECT_ROOT, 'backend'))

# import pandas as pd
# from backend.nyc_open_data_api import NYCOpenDataAPI

# URL = 'https://data.cityofnewyork.us/resource/h9gi-nx95.csv'
# KEY = 'UHuQ1JuV1fHgvlc4eWkFETreT'
# COLUMNS = ['crash_date', 'crash_time', 'borough', 'latitude', 'longitude',
#            'on_street_name', 'contributing_factor_vehicle_1',
#            'vehicle_type_code1', 'number_of_persons_injured',
#            'number_of_persons_killed']


# def test_api_fetch():
#     """Step 1: Can we fetch data from the API?"""
#     print("=" * 50)
#     print("TEST: API Fetch")
#     print("=" * 50)
#     try:
#         api = NYCOpenDataAPI(URL, KEY)
#         data = api.fetch_data(columns=COLUMNS, limit=10000)
#         print(f"✓ Fetched {len(data)} rows")
#         print(f"✓ Columns: {list(data.columns)}")
#         print(f"\nFirst 3 rows:\n{data.head(3)}")
#         print(f"\nDtypes:\n{data.dtypes}")
#         return api, data
#     except Exception as e:
#         print(f"✗ API fetch failed: {type(e).__name__}: {e}")
#         return None, None


# def test_data_cleaning(api=None, data=None):
#     """Step 2: Can we clean and process the data?"""
#     print("\n" + "=" * 50)
#     print("TEST: Data Cleaning")
#     print("=" * 50)
#     try:
#         if api is None or data is None:
#             api, data = test_api_fetch()
#             if data is None:
#                 return None, None

#         df = api.process_strings(data)
#         print(f"✓ process_strings succeeded — {len(df)} rows")

#         print(f"\nBefore time conversion (sample): {df['crash_time'].head(3).tolist()}")
#         df['crash_time'] = api.convert_time_col_to_ranges(df, 'crash_time')
#         print(f"After time conversion (sample):  {df['crash_time'].head(3).tolist()}")

#         df['crash_date'] = pd.to_datetime(df['crash_date'])
#         print(f"✓ crash_date converted to datetime")

#         print(f"\nYear range: {df['crash_date'].min().year} - {df['crash_date'].max().year}")
#         print(f"Unique boroughs: {df['borough'].unique().tolist()}")
#         print(f"Null counts:\n{df.isnull().sum()}")

#         return api, df
#     except Exception as e:
#         print(f"✗ Data cleaning failed: {type(e).__name__}: {e}")
#         import traceback; traceback.print_exc()
#         return None, None


# def test_filter(df=None):
#     """Step 2.5: Can we filter data by year and borough?"""
#     print("\n" + "=" * 50)
#     print("TEST: Filter Function")
#     print("=" * 50)
#     try:
#         if df is None:
#             _, df = test_data_cleaning()
#             if df is None:
#                 return None

#         boroughs = ['Manhattan']
#         # Use whatever years are actually in the data
#         yr_min = df['crash_date'].min().year
#         yr_max = df['crash_date'].max().year
#         print(f"Filtering: boroughs={boroughs}, years={yr_min}-{yr_max}")

#         filtered = NYCOpenDataAPI.filter_by_year_and_borough(
#             df, yr_start=yr_min, yr_end=yr_max, boroughs=boroughs
#         )
#         print(f"✓ Filtered to {len(filtered)} rows (from {len(df)})")
#         print(f"  Boroughs in result: {filtered['borough'].unique().tolist()}")

#         if len(filtered) == 0:
#             print("⚠ WARNING: Filter returned 0 rows — check borough names and year range")
#             print(f"  Available boroughs: {df['borough'].unique().tolist()}")
#             print(f"  Available years: {df['crash_date'].min().year}-{df['crash_date'].max().year}")

#         return filtered
#     except Exception as e:
#         print(f"✗ Filter failed: {type(e).__name__}: {e}")
#         import traceback; traceback.print_exc()
#         return None


# def test_map(df=None):
#     """Step 3: Can we generate the NYC map?"""
#     print("\n" + "=" * 50)
#     print("TEST: NYC Map")
#     print("=" * 50)
#     try:
#         if df is None:
#             _, df = test_data_cleaning()
#             if df is None:
#                 return

#         from components import nyc_collision_map as nd

#         yr_min = df['crash_date'].min().year
#         yr_max = df['crash_date'].max().year
#         boroughs = [b for b in df['borough'].unique() if pd.notna(b)][:2]
#         print(f"Generating map: boroughs={boroughs}, years={yr_min}-{yr_max}")

#         fig = nd.generate_nyc_map(df, 'latitude', 'longitude',
#                                   yr_start=yr_min, yr_end=yr_max, boroughs=boroughs)
#         print(f"✓ Map generated successfully")
#         print(f"  Traces: {len(fig.data)}")
#         print(f"  Annotations: {len(fig.layout.annotations)}")

#         fig.show()
#         print("✓ Map opened in browser")
#     except Exception as e:
#         print(f"✗ Map generation failed: {type(e).__name__}: {e}")
#         import traceback; traceback.print_exc()


# def test_sankey(df=None):
#     """Step 4: Can we generate the Sankey diagram?"""
#     print("\n" + "=" * 50)
#     print("TEST: Sankey Diagram")
#     print("=" * 50)
#     try:
#         if df is None:
#             _, df = test_data_cleaning()
#             if df is None:
#                 return

#         from components import nyc_collision_map as nd

#         yr_min = df['crash_date'].min().year
#         yr_max = df['crash_date'].max().year
#         boroughs = [b for b in df['borough'].unique() if pd.notna(b)][:2]
#         cols = ['contributing_factor_vehicle_1', 'vehicle_type_code1']
#         print(f"Generating sankey: cols={cols}, boroughs={boroughs}")

#         # First test the groupby step alone
#         filtered = NYCOpenDataAPI.filter_by_year_and_borough(
#             df, yr_start=yr_min, yr_end=yr_max, boroughs=boroughs
#         )
#         grouped = filtered.groupby(cols).size().reset_index(name='count')
#         grouped = grouped.sort_values(by='count', ascending=False).head(10)
#         print(f"✓ Grouped data ({len(grouped)} rows):\n{grouped.head()}")

#         fig = nd.generate_sankey(df, cols=cols, yr_start=yr_min, yr_end=yr_max, boroughs=boroughs)
#         print(f"✓ Sankey generated successfully")

#         fig.show()
#         print("✓ Sankey opened in browser")
#     except Exception as e:
#         print(f"✗ Sankey generation failed: {type(e).__name__}: {e}")
#         import traceback; traceback.print_exc()


# def test_histogram(df=None):
#     """Step 5: Can we generate the histogram?"""
#     print("\n" + "=" * 50)
#     print("TEST: Histogram")
#     print("=" * 50)
#     try:
#         if df is None:
#             _, df = test_data_cleaning()
#             if df is None:
#                 return

#         from components import nyc_collision_map as nd

#         yr_min = df['crash_date'].min().year
#         yr_max = df['crash_date'].max().year
#         boroughs = [b for b in df['borough'].unique() if pd.notna(b)][:2]
#         cols = ['number_of_persons_injured', 'number_of_persons_killed']
#         print(f"Generating histogram: cols={cols}, boroughs={boroughs}")

#         # Test the melt step alone first
#         filtered = NYCOpenDataAPI.filter_by_year_and_borough(
#             df, yr_start=yr_min, yr_end=yr_max, boroughs=boroughs
#         )
#         print(f"  Filtered rows: {len(filtered)}")
#         print(f"  Sample values (injured): {filtered['number_of_persons_injured'].head().tolist()}")
#         print(f"  Sample values (killed):  {filtered['number_of_persons_killed'].head().tolist()}")
#         print(f"  Dtypes: injured={filtered['number_of_persons_injured'].dtype}, "
#               f"killed={filtered['number_of_persons_killed'].dtype}")

#         fig = nd.generate_hist(df, cols=cols, yr_start=yr_min, yr_end=yr_max, boroughs=boroughs)
#         print(f"✓ Histogram generated successfully")
#         print(f"  Traces: {len(fig.data)}")

#         fig.show()
#         print("✓ Histogram opened in browser")
#     except Exception as e:
#         print(f"✗ Histogram generation failed: {type(e).__name__}: {e}")
#         import traceback; traceback.print_exc()


# def test_all():
#     """Run all tests in order."""
#     api, data = test_api_fetch()
#     if data is None:
#         print("\n⚠ Stopping — API fetch failed")
#         return

#     api, df = test_data_cleaning(api, data)
#     if df is None:
#         print("\n⚠ Stopping — data cleaning failed")
#         return

#     filtered = test_filter(df)
#     if filtered is None:
#         print("\n⚠ Stopping — filter failed")
#         return

#     test_map(df)
#     test_sankey(df)
#     test_histogram(df)

#     print("\n" + "=" * 50)
#     print("ALL TESTS COMPLETE")
#     print("=" * 50)


# if __name__ == "__main__":
#     commands = {
#         'api': test_api_fetch,
#         'clean': test_data_cleaning,
#         'filter': test_filter,
#         'map': test_map,
#         'sankey': test_sankey,
#         'hist': test_histogram,
#         'all': test_all,
#     }

#     if len(sys.argv) < 2 or sys.argv[1] not in commands:
#         print(__doc__)
#         print(f"Available tests: {', '.join(commands.keys())}")
#     else:
#         commands[sys.argv[1]]()

"""
Run from project root: python tests/debug_data.py
"""
import sys, os
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'backend'))

import pandas as pd
from backend.nyc_open_data_api import NYCOpenDataAPI
import plotly
print(f"Plotly version: {plotly.__version__}")

URL = 'https://data.cityofnewyork.us/resource/h9gi-nx95.csv'
KEY = 'UHuQ1JuV1fHgvlc4eWkFETreT'
COLUMNS = ['crash_date','crash_time','borough','latitude','longitude',
           'on_street_name','contributing_factor_vehicle_1',
           'vehicle_type_code1','number_of_persons_injured','number_of_persons_killed']

api = NYCOpenDataAPI(URL, KEY)

# 1. Raw fetch
print("\n--- RAW FETCH ---")
data = api.fetch_data(columns=COLUMNS, limit=50)
print(f"Type: {type(data)}")
print(f"Shape: {data.shape}")
print(f"Columns: {list(data.columns)}")
print(f"\nFirst 3 rows:\n{data.head(3).to_string()}")

# 2. Check for nulls in key columns
print("\n--- NULL COUNTS ---")
print(data.isnull().sum())

# 3. Check dtypes
print("\n--- DTYPES ---")
print(data.dtypes)

# 4. After cleaning
print("\n--- AFTER CLEANING ---")
df = api.process_strings(data)
df['crash_date'] = pd.to_datetime(df['crash_date'])
print(f"Boroughs: {df['borough'].unique().tolist()}")
print(f"Year range: {df['crash_date'].min()} to {df['crash_date'].max()}")
print(f"Lat sample: {df['latitude'].head(5).tolist()}")
print(f"Lon sample: {df['longitude'].head(5).tolist()}")
print(f"Lat dtype: {df['latitude'].dtype}")
print(f"Lon dtype: {df['longitude'].dtype}")

# 5. Test filter
print("\n--- FILTER TEST ---")
boroughs = [b for b in df['borough'].unique() if pd.notna(b)]
print(f"Valid boroughs: {boroughs}")
yr_min = df['crash_date'].min().year
yr_max = df['crash_date'].max().year
print(f"Filtering years {yr_min}-{yr_max}, boroughs={boroughs[:1]}")
filtered = NYCOpenDataAPI.filter_by_year_and_borough(df, yr_start=yr_min, yr_end=yr_max, boroughs=boroughs[:1])
print(f"Filtered rows: {len(filtered)}")
print(f"Filtered lat nulls: {filtered['latitude'].isnull().sum()}")
print(f"Filtered lon nulls: {filtered['longitude'].isnull().sum()}")

# 6. Quick map test
print("\n--- MAP TEST ---")
try:
    import plotly.express as px
    test_df = filtered.dropna(subset=['latitude', 'longitude']).head(20)
    print(f"Test df rows: {len(test_df)}, lat dtype: {test_df['latitude'].dtype}")
    fig = px.scatter_map(test_df, lat='latitude', lon='longitude', zoom=10)
    fig.show()
    print("✓ scatter_map works")
except Exception as e:
    print(f"✗ scatter_map failed: {e}")
    try:
        fig = px.scatter_mapbox(test_df, lat='latitude', lon='longitude', zoom=10)
        fig.update_layout(mapbox_style='carto-positron')
        fig.show()
        print("✓ scatter_mapbox works (use old API)")
    except Exception as e2:
        print(f"✗ scatter_mapbox also failed: {e2}")