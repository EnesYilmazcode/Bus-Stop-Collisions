import pandas as pd
import folium
from folium.plugins import HeatMap


def load_data(crash_file, bus_stop_file):
    """Load the crash and bus stop data."""
    crashes = pd.read_csv(crash_file, dtype={'LATITUDE': float, 'LONGITUDE': float})
    bus_stops = pd.read_csv(bus_stop_file, dtype={'Longitude': float, 'Latitude': float})
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


def create_heatmap(crashes, bus_stops, output_path='outputs/bus_stop_crash_heatmap.html'):
    """Create an interactive heatmap showing crash densities near bus stops."""
    # Initialize the map centered around the average location of bus stops
    center_lat = bus_stops['latitude'].mean()
    center_long = bus_stops['longitude'].mean()
    map_obj = folium.Map(location=[center_lat, center_long], zoom_start=12)


    # Prepare data for the heatmap
    heat_data = [[row['latitude'], row['longitude']] for index, row in crashes.iterrows()]


    # Add the heatmap layer
    HeatMap(heat_data, radius=15).add_to(map_obj)


    # Add bus stops to the map
    for _, row in bus_stops.iterrows():
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup='Bus Stop',
            icon=folium.Icon(color='blue')
        ).add_to(map_obj)


    # Save the heatmap
    map_obj.save(output_path)


def main():
    # File paths
    crash_file = 'data/crash_collisions.csv'
    bus_stop_file = 'data/bus_stop_locations.csv'


    # Load data
    crashes, bus_stops = load_data(crash_file, bus_stop_file)


    # Clean data
    crashes, bus_stops = clean_data(crashes, bus_stops)


    # Create heatmap
    create_heatmap(crashes, bus_stops)


if __name__ == "__main__":
    main()
