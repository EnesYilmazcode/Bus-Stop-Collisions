# didnt work as I wanted it to

import pandas as pd
import geopandas as gpd
import folium
from shapely.geometry import Point

# ----------------------------
# 1. Load Data with Enhanced Checks
# ----------------------------
def load_data():
    # Load crashes with error handling for coordinate columns
    try:
        crashes = pd.read_csv(
            'data/crash_collisions.csv',
            dtype={'LATITUDE': float, 'LONGITUDE': float},
            low_memory=False
        )
        bus_stops = pd.read_csv(
            'data/bus_stop_locations.csv',
            dtype={'Latitude': float, 'Longitude': float}
        )
    except KeyError as e:
        raise ValueError(f"Missing required column: {e}. Check your CSV headers.")

    # Verify coordinate ranges (NYC should be lat 40.5-40.9, lon -74.3--73.7)
    print("\nCrash coordinate ranges:")
    print(f"Latitude: {crashes['LATITUDE'].min()} to {crashes['LATITUDE'].max()}")
    print(f"Longitude: {crashes['LONGITUDE'].min()} to {crashes['LONGITUDE'].max()}")

    print("\nBus stop coordinate ranges:")
    print(f"Latitude: {bus_stops['Latitude'].min()} to {bus_stops['Latitude'].max()}")
    print(f"Longitude: {bus_stops['Longitude'].min()} to {bus_stops['Longitude'].max()}")

    return crashes, bus_stops

# ----------------------------
# 2. Clean Data with Strict Validation
# ----------------------------
def clean_data(crashes, bus_stops):
    # Clean crashes
    initial_count = len(crashes)
    crashes = crashes.dropna(subset=['LATITUDE', 'LONGITUDE']).rename(
        columns={'LATITUDE': 'crash_lat', 'LONGITUDE': 'crash_lon'}
    )
    crashes = crashes[
        (crashes['crash_lat'].between(40.5, 40.9)) & 
        (crashes['crash_lon'].between(-74.3, -73.7))
    ]
    print(f"\nRemoved {initial_count - len(crashes)} invalid crash records")

    # Clean bus stops
    initial_stops = len(bus_stops)
    bus_stops = bus_stops.dropna(subset=['Latitude', 'Longitude']).rename(
        columns={'Latitude': 'stop_lat', 'Longitude': 'stop_lon'}
    )
    bus_stops = bus_stops[
        (bus_stops['stop_lat'].between(40.5, 40.9)) & 
        (bus_stops['stop_lon'].between(-74.3, -73.7))
    ]
    print(f"Removed {initial_stops - len(bus_stops)} invalid bus stop records")

    return crashes, bus_stops

# ----------------------------
# 3. Spatial Analysis with Detailed Debugging
# ----------------------------
def get_top_bus_stops(crashes, bus_stops, distance_ft=100):
    # Convert to meters
    distance_m = distance_ft * 0.3048

    # Create geometries with validation
    def safe_create_gdf(df, x_col, y_col, crs):
        try:
            return gpd.GeoDataFrame(
                df,
                geometry=gpd.points_from_xy(df[x_col], df[y_col]),
                crs=crs
            ).to_crs('EPSG:3857')  # Ensure consistent CRS
        except ValueError as e:
            raise ValueError(f"Coordinate error: {e}. Check {x_col}/{y_col} values.")

    # Create GeoDataFrames
    crashes_gdf = safe_create_gdf(crashes, 'crash_lon', 'crash_lat', 'EPSG:4326')
    bus_stops_gdf = safe_create_gdf(bus_stops, 'stop_lon', 'stop_lat', 'EPSG:4326')

    # Create buffers
    bus_stops_gdf['buffer'] = bus_stops_gdf.geometry.buffer(distance_m)

    # Spatial join with progress indication
    print("\nPerforming spatial join...")
    crashes_near_stops = gpd.sjoin_nearest(crashes_gdf, bus_stops_gdf, how='inner', distance_col='distance')  # Use nearest join

    if crashes_near_stops.empty:
        # Diagnostic plot
        print("\nCreating diagnostic map...")
        m = folium.Map(location=[40.7128, -74.0060], zoom_start=11)
        for _, stop in bus_stops_gdf.sample(100).iterrows():
            folium.Circle(
                location=[stop['stop_lat'], stop['stop_lon']],
                radius=30.48,
                color='blue',
                fill=True
            ).add_to(m)
        for _, crash in crashes_gdf.sample(100).iterrows():
            folium.CircleMarker(
                location=[crash['crash_lat'], crash['crash_lon']],
                radius=2,
                color='red'
            ).add_to(m)
        m.save('outputs/diagnostic_map.html')
        print("Saved diagnostic map to outputs/diagnostic_map.html")
        print("Blue circles = bus stop buffers, Red dots = crash locations")

        raise ValueError(
            "No crashes found near bus stops. Possible reasons:\n"
            "1. Coordinate system mismatch\n"
            "2. Buffer too small\n"
            "3. Genuinely no nearby crashes\n"
            "Check diagnostic_map.html to verify spatial relationships"
        )

    # Count crashes per stop
    crash_counts = crashes_near_stops.groupby('index_right').size().reset_index(name='crash_count')
    bus_stops = bus_stops.merge(crash_counts, left_index=True, right_on='index_right', how='left')
    bus_stops['crash_count'] = bus_stops['crash_count'].fillna(0).astype(int)

    return bus_stops.sort_values('crash_count', ascending=False).head(10), crashes_near_stops

# ----------------------------
# 4. Create Map
# ----------------------------
def create_map(top_stops, crashes_near_stops):
    m = folium.Map(
        location=[top_stops.iloc[0]['stop_lat'], top_stops.iloc[0]['stop_lon']],
        zoom_start=15
    )

    # Add bus stops
    for _, stop in top_stops.iterrows():
        folium.Marker(
            location=[stop['stop_lat'], stop['stop_lon']],
            popup=f"Crashes: {stop['crash_count']}",
            icon=folium.Icon(color='red', icon='bus', prefix='fa')
        ).add_to(m)

    # Add crashes
    for _, crash in crashes_near_stops.iterrows():
        folium.CircleMarker(
            location=[crash['crash_lat'], crash['crash_lon']],
            radius=3,
            color='gray',
            fill=True
        ).add_to(m)

    return m

# ----------------------------
# 5. Main Execution
# ----------------------------
if __name__ == "__main__":
    crashes, bus_stops = load_data()
    crashes, bus_stops = clean_data(crashes, bus_stops)
    
    print(f"\nValid crash records remaining: {len(crashes)}")
    print(f"Valid bus stops remaining: {len(bus_stops)}")
    
    try:
        top_10_stops, crashes_near_stops = get_top_bus_stops(crashes, bus_stops)
        result_map = create_map(top_10_stops, crashes_near_stops)
        result_map.save('outputs/final_map.html')
        print("\nSuccess! Map saved to outputs/final_map.html")
    except ValueError as e:
        print(f"\nError: {e}")