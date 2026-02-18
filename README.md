# NYC Vehicle Collision Dashboard

Comprehensive dashboard of all vehicle collisions across the five boroughs of New York City from 2012 to present day.
Deployed at: 
https://nyc-collision-dashboard.onrender.com

## Overview

This project pulls live data from https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Crashes/h9gi-nx95/about_data

## Features

- **Interactive Map** — Plots individual collision locations across NYC with borough-level toggling via the map legend
- **Sankey Diagram** — Visualizes relationships between any combination of street name, contributing factor, vehicle type, and time of collision
- **Frequency Histogram** — Displays the severity distribution of crashes by injuries and fatalities
- **Year Range Slider** — Filter all visualizations by a custom year range
- **Live Data** — Fetches directly from the NYC Open Data API with retry logic and caching

## Tech Stack

- **Backend:** Python, Flask (via Dash), Pandas
- **Frontend:** Dash, Plotly, Dash Bootstrap Components
- **Data Source:** NYC Open Data Vehicle Collisions API
- **Deployment:** Render

### Command Line Options

| Flag | Default | Description |
|------|---------|-------------|
| `--limit` | 250000 | Number of rows to fetch from the API |
| `--yr-start` | 2024 | Default start year for the slider |
| `--yr-end` | 2025 | Default end year for the slider |
| `--port` | 8050 | Port to run the dashboard on |
| `--refresh` | False | Force re-fetch from API, ignoring cache |
| `--no-debug` | — | Run without debug mode |

### Example

```bash
python backend/main.py --limit 500000 --yr-start 2020 --yr-end 2025 --port 8080
```

## Project Structure

```
vehicle-collision-dash/
├── backend/
│   ├── main.py                  # Dashboard entry point and layout
│   ├── nyc_open_data_api.py     # API client with retry logic and caching
│   └── components/
│       ├── nyc_collision_map.py  # Map, Sankey, and histogram generators
│       └── sankey.py             # Sankey diagram builder
├── frontend/
│   └── assets/
│       └── style.css            # Dashboard styles
├── .env                         # API key (not committed)
├── .gitignore
├── requirements.txt
└── README.md
```

## License

MIT
