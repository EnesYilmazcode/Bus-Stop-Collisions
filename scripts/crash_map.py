import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import folium


def get_locations_for_top_bus_stops(bus_stops, top_ids):
    """Extract the latitude and longitude of the top bus stop IDs."""
    return bus_stops[bus_stops['StopID'].isin(top_ids)][['StopID', 'latitude', 'longitude']]


def plot_crashes_and_top_bus_stops(crashes, top_bus_stop_locations, distance=150):
    """Plot crashes and top bus stops on a map with circular buffers."""
    # Initialize the map centered on the average location of the top bus stops
    map_center = [top_bus_stop_locations['latitude'].mean(), top_bus_stop_locations['longitude'].mean()]
    crash_map = folium.Map(location=map_center, zoom_start=13)

    # Add circular buffers for the top bus stops
    for _, row in top_bus_stop_locations.iterrows():
        folium.Circle(
            location=[row['latitude'], row['longitude']],
            radius=distance * 0.3048,  # Convert feet to meters
            color="blue",
            fill=True,
            fill_opacity=0.3,
            popup=f"Bus Stop ID: {row['StopID']}"
        ).add_to(crash_map)

    # Add crashes to the map
    for _, row in crashes.iterrows():
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            icon=folium.Icon(color="red", icon="info-sign"),
            popup="Crash"
        ).add_to(crash_map)

    # Save the map
    crash_map.save("crashes_near_top_bus_stops.html")
    print("Map saved as 'crashes_near_top_bus_stops.html'.")


def main():
    # File paths
    crash_file = 'data/crash_collisions.csv'
    bus_stop_file = 'data/bus_stop_locations.csv'

    # Load data
    crashes = pd.read_csv(crash_file, dtype={'LATITUDE': float, 'LONGITUDE': float}, low_memory=False)
    bus_stops = pd.read_csv(bus_stop_file, dtype={'Longitude': float, 'Latitude': float}, low_memory=False)

    # Clean data
    crashes = crashes.dropna(subset=['LATITUDE', 'LONGITUDE']).rename(columns={'LATITUDE': 'latitude', 'LONGITUDE': 'longitude'})
    bus_stops = bus_stops.dropna(subset=['Latitude', 'Longitude']).rename(columns={'Latitude': 'latitude', 'Longitude': 'longitude'})

    # Top bus stop IDs
    top_ids = [2008, 1788, 1586, 1927, 1618, 1604, 148, 2663, 3059, 3183]

    # Get hardcoded locations for the top bus stops
    top_bus_stop_locations = get_locations_for_top_bus_stops(bus_stops, top_ids)

    # Plot crashes and top bus stops
    plot_crashes_and_top_bus_stops(crashes, top_bus_stop_locations)


if __name__ == "__main__":
    main()
