import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import folium

def load_data(crash_file, bus_stop_file):
    """Load the crash and bus stop data."""
    crashes = pd.read_csv(crash_file, dtype={'LATITUDE': str, 'LONGITUDE': str}, low_memory=False)
    bus_stops = pd.read_csv(bus_stop_file, dtype={'Latitude': float, 'Longitude': float})
    return crashes, bus_stops

def clean_data(crashes, bus_stops):
    """Clean crash and bus stop data."""
    # Convert latitude and longitude to numeric, forcing errors to NaN
    crashes['LATITUDE'] = pd.to_numeric(crashes['LATITUDE'], errors='coerce')
    crashes['LONGITUDE'] = pd.to_numeric(crashes['LONGITUDE'], errors='coerce')
    
    # Drop rows with NaN values
    crashes = crashes.dropna(subset=['LATITUDE', 'LONGITUDE'])
    bus_stops = bus_stops.dropna(subset=['Latitude', 'Longitude'])
    
    crashes = crashes.rename(columns={'LATITUDE': 'latitude', 'LONGITUDE': 'longitude'})
    bus_stops = bus_stops.rename(columns={'Latitude': 'latitude', 'Longitude': 'longitude'})
    return crashes, bus_stops

def create_proximity_map(crashes, bus_stops, distance_ft=100):
    """Create a map showing the top 10 bus stops with the most crashes within a specified distance."""
    # Convert distance to meters
    distance_m = distance_ft * 0.3048

    # Create GeoDataFrames
    crashes_gdf = gpd.GeoDataFrame(crashes, geometry=gpd.points_from_xy(crashes.longitude, crashes.latitude), crs="EPSG:4326")
    bus_stops_gdf = gpd.GeoDataFrame(bus_stops, geometry=gpd.points_from_xy(bus_stops.longitude, bus_stops.latitude), crs="EPSG:4326")

    # Reproject to a projected CRS (e.g., EPSG:3857)
    crashes_gdf = crashes_gdf.to_crs(epsg=3857)
    bus_stops_gdf = bus_stops_gdf.to_crs(epsg=3857)

    # Create buffers around bus stops
    bus_stops_gdf['buffer'] = bus_stops_gdf.geometry.buffer(distance_m)

    # Spatial join to find crashes within the buffer
    crashes_near_stops = gpd.sjoin(crashes_gdf, bus_stops_gdf, how='inner', predicate='within')

    # Count crashes per bus stop
    crash_counts = crashes_near_stops.groupby('index_right').size().reset_index(name='crash_count')
    bus_stops_gdf = bus_stops_gdf.merge(crash_counts, left_index=True, right_on='index_right', how='left')
    bus_stops_gdf['crash_count'] = bus_stops_gdf['crash_count'].fillna(0).astype(int)

    # Get top 10 bus stops with the most crashes
    top_bus_stops = bus_stops_gdf.sort_values('crash_count', ascending=False).head(10)

    # Create a map centered around the first bus stop
    map_center = [top_bus_stops.iloc[0]['latitude'], top_bus_stops.iloc[0]['longitude']]
    map_obj = folium.Map(location=map_center, zoom_start=14)

    # Add bus stops to the map
    for _, row in top_bus_stops.iterrows():
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=f"Bus Stop: {row['crash_count']} crashes",
            icon=folium.Icon(color='red')
        ).add_to(map_obj)

        # Add crash markers as triangles
        crashes_in_buffer = crashes_near_stops[crashes_near_stops['index_right'] == row.name]
        for _, crash in crashes_in_buffer.iterrows():
            folium.RegularPolygonMarker(
                location=[crash['latitude'], crash['longitude']],
                number_of_sides=3,
                radius=5,
                color='blue',
                fill=True,
                fill_color='blue',
                fill_opacity=0.6
            ).add_to(map_obj)

    # Save the map
    map_obj.save('outputs/top_bus_stops_with_crashes.html')
    print("Map saved as 'outputs/top_bus_stops_with_crashes.html'.")

def main():
    # File paths
    crash_file = 'data/crash_collisions.csv'
    bus_stop_file = 'data/bus_stop_locations.csv'

    # Load and clean data
    crashes, bus_stops = load_data(crash_file, bus_stop_file)
    crashes, bus_stops = clean_data(crashes, bus_stops)

    # Create the proximity map
    create_proximity_map(crashes, bus_stops)

if __name__ == "__main__":
    main()