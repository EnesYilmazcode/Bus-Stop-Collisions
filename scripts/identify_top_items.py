import pandas as pd
import folium
from tqdm import tqdm
from folium.plugins import MarkerCluster, HeatMap
import gc  # For garbage collection
from folium import Icon

def load_data(crash_file, bus_stop_file):
    """Load the crash and bus stop data."""
    print("Loading data...")
    crashes = pd.read_csv(crash_file, dtype={'LATITUDE': float, 'LONGITUDE': float}, low_memory=False)
    bus_stops = pd.read_csv(bus_stop_file, dtype={'Longitude': float, 'Latitude': float}, low_memory=False)
    print("Data loaded successfully!")
    return crashes, bus_stops

def clean_data(crashes, bus_stops):
    """Clean crash and bus stop data."""
    print("Cleaning data...")
    crashes = crashes.dropna(subset=['LATITUDE', 'LONGITUDE'])
    bus_stops = bus_stops.dropna(subset=['Latitude', 'Longitude'])
    crashes = crashes.rename(columns={'LATITUDE': 'latitude', 'LONGITUDE': 'longitude'})
    bus_stops = bus_stops.rename(columns={'Latitude': 'latitude', 'Longitude': 'longitude'})
    print("Data cleaned successfully!")
    return crashes, bus_stops

def get_locations_for_top_bus_stops(bus_stops, top_ids):
    """Extract the latitude and longitude of the top bus stop IDs."""
    return bus_stops[bus_stops['Shelter_ID'].isin(top_ids)][['Shelter_ID', 'latitude', 'longitude']]

def plot_crashes_and_top_bus_stops(crashes, top_bus_stop_locations, distance=150):
    """Plot crashes and top bus stops on a map with circular buffers."""
    # Drop rows with NaN values in latitude or longitude
    top_bus_stop_locations = top_bus_stop_locations.dropna(subset=['latitude', 'longitude'])

    if top_bus_stop_locations.empty:
        raise ValueError("No valid bus stop locations with latitude and longitude data.")

    # Create base map with a tile layer that has minimal text
    map_center = [top_bus_stop_locations['latitude'].mean(), top_bus_stop_locations['longitude'].mean()]
    crash_map = folium.Map(location=map_center, zoom_start=13, tiles='CartoDB positron')

    # Add bus stop buffers
    print("Adding bus stop buffers...")
    for _, row in tqdm(top_bus_stop_locations.iterrows(), total=len(top_bus_stop_locations), desc="Bus Stops"):
        folium.Circle(
            location=[row['latitude'], row['longitude']],
            radius=distance * 0.3048,
            color="blue",
            fill=False,
            fill_opacity=0,
            popup=f"Bus Stop ID: {row['Shelter_ID']}"
        ).add_to(crash_map)

        # Add bus stop icon
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            icon=folium.Icon(icon='cloud', color='blue'),  # Change 'cloud' to a bus stop icon
            popup=f"Bus Stop ID: {row['Shelter_ID']}"
        ).add_to(crash_map)

    # Prepare data for heatmap
    heat_data = [[row['latitude'], row['longitude']] for index, row in crashes.iterrows()]

    # Add heatmap layer
    HeatMap(heat_data, radius=15).add_to(crash_map)

    # Save the map
    print("Saving map...")
    crash_map.save("crashes_near_top_bus_stops_heatmap.html")
    print("Map saved successfully!")

def main():
    # File paths
    crash_file = 'data/crash_collisions.csv'
    bus_stop_file = 'data/bus_stop_locations.csv'

    # Load and clean data
    crashes, bus_stops = load_data(crash_file, bus_stop_file)
    crashes, bus_stops = clean_data(crashes, bus_stops)

    # Top bus stop IDs
    top_ids = ['BR0216', 'MN0287', 'MN01369', 'QN04932', 
              'QN05032', 'MN0116', 'MN01137', 
              'MN01674', 'SI05204', "MN01376"]

    # Get locations for the top bus stops
    top_bus_stop_locations = get_locations_for_top_bus_stops(bus_stops, top_ids)

    # Plot crashes and bus stops
    plot_crashes_and_top_bus_stops(crashes, top_bus_stop_locations)

if __name__ == "__main__":
    main()