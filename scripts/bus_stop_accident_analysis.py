import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt


def load_data(crash_file, bus_stop_file):
    """Load the crash and bus stop data."""
    crashes = pd.read_csv(crash_file, dtype={'LATITUDE': float, 'LONGITUDE': float}, low_memory=False)
    bus_stops = pd.read_csv(bus_stop_file, dtype={'Longitude': float, 'Latitude': float}, low_memory=False)
    return crashes, bus_stops


def clean_data(crashes, bus_stops):
    """Clean crash and bus stop data."""
    crashes = crashes.dropna(subset=['LATITUDE', 'LONGITUDE'])
    bus_stops = bus_stops.dropna(subset=['Latitude', 'Longitude'])
    crashes = crashes.rename(columns={'LATITUDE': 'latitude', 'LONGITUDE': 'longitude'})
    bus_stops = bus_stops.rename(columns={'Latitude': 'latitude', 'Longitude': 'longitude'})
    return crashes, bus_stops


def calculate_accidents_near_bus_stops(crashes, bus_stops, distance=100):
    """Calculate the percentage of bus stops with accidents within a specified distance."""
    # Convert to GeoDataFrames
    crashes_gdf = gpd.GeoDataFrame(crashes, geometry=gpd.points_from_xy(crashes.longitude, crashes.latitude), crs="EPSG:4326")
    bus_stops_gdf = gpd.GeoDataFrame(bus_stops, geometry=gpd.points_from_xy(bus_stops.longitude, bus_stops.latitude), crs="EPSG:4326")


    # Reproject to a projected CRS (e.g., UTM)
    crashes_gdf = crashes_gdf.to_crs(epsg=3857)
    bus_stops_gdf = bus_stops_gdf.to_crs(epsg=3857)


    # Buffer bus stops by the distance in meters (1 foot = 0.3048 meters)
    distance_meters = distance * 0.3048
    bus_stops_gdf['geometry'] = bus_stops_gdf.geometry.buffer(distance_meters)


    # Perform a spatial join to find crashes within the buffer
    joined = gpd.sjoin(crashes_gdf, bus_stops_gdf, how='inner', predicate='within')


    # Mark bus stops that have accidents
    bus_stops['has_accident'] = bus_stops.index.isin(joined['index_right'].unique())


    # Calculate percentages
    total_bus_stops = len(bus_stops)
    bus_stops_with_accidents = bus_stops['has_accident'].sum()
    bus_stops_without_accidents = total_bus_stops - bus_stops_with_accidents


    return bus_stops_with_accidents, bus_stops_without_accidents, total_bus_stops




def plot_bus_stop_accident_percentages(bus_stops_with_accidents, bus_stops_without_accidents, total_bus_stops):
    """Plot the percentages of bus stops with and without accidents."""
    labels = ['With Accidents', 'Without Accidents']
    sizes = [bus_stops_with_accidents, bus_stops_without_accidents]
    percentages = [size / total_bus_stops * 100 for size in sizes]


    plt.figure(figsize=(8, 5))
    plt.bar(labels, percentages, color=['red', 'green'])
    plt.ylabel('Percentage of Bus Stops (%)')
    plt.title('Percentage of Bus Stops with Accidents within 100 Feet')
    plt.ylim(0, 100)
    plt.grid(axis='y')


    for i, v in enumerate(percentages):
        plt.text(i, v + 1, f"{v:.2f}%", ha='center')


    plt.show()


def main():
    # File paths
    crash_file = 'data/crash_collisions.csv'
    bus_stop_file = 'data/bus_stop_locations.csv'


    # Load and clean data
    crashes, bus_stops = load_data(crash_file, bus_stop_file)
    crashes, bus_stops = clean_data(crashes, bus_stops)


    # Calculate accidents near bus stops
    bus_stops_with_accidents, bus_stops_without_accidents, total_bus_stops = calculate_accidents_near_bus_stops(crashes, bus_stops)


    # Plot the results
    plot_bus_stop_accident_percentages(bus_stops_with_accidents, bus_stops_without_accidents, total_bus_stops)


if __name__ == "__main__":
    main()


