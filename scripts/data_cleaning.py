import pandas as pd

def load_data(crash_file, bus_stop_file):
    """Load the crash and bus stop data."""
    crashes = pd.read_csv(crash_file)
    bus_stops = pd.read_csv(bus_stop_file)
    return crashes, bus_stops

def clean_data(crashes, bus_stops):
    """Clean crash and bus stop data."""
    # Drop rows with missing latitude/longitude
    crashes = crashes.dropna(subset=['LATITUDE', 'LONGITUDE'])
    bus_stops = bus_stops.dropna(subset=['Latitude', 'Longitude'])

    # Ensure consistent column names for latitude and longitude
    crashes = crashes.rename(columns={'LATITUDE': 'latitude', 'LONGITUDE': 'longitude'})
    bus_stops = bus_stops.rename(columns={'Latitude': 'latitude', 'Longitude': 'longitude'})

    return crashes, bus_stops
