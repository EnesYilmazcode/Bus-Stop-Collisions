import pandas as pd
import folium

def get_locations_for_top_bus_stops(bus_stops, top_ids):
    """Extract the latitude and longitude of the top bus stop IDs."""
    # Replace 'Shelter_ID' with the correct column name from your CSV file
    return bus_stops[bus_stops['Shelter_ID'].isin(top_ids)][['Shelter_ID', 'latitude', 'longitude']]

def plot_crashes_and_top_bus_stops(crashes, top_bus_stop_locations, distance=150):
    """Plot crashes and top bus stops on a map with circular buffers."""
    # Drop rows with NaN values in latitude or longitude
    top_bus_stop_locations = top_bus_stop_locations.dropna(subset=['latitude', 'longitude'])

    # Check if there are any valid locations left
    if top_bus_stop_locations.empty:
        raise ValueError("No valid bus stop locations with latitude and longitude data.")

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
            popup=f"Bus Stop ID: {row['Shelter_ID']}"  # Update the column name here
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

def save_bus_stops_data(bus_stops, output_file='bus_stops_data.csv'):
    """Save the bus stops data to a CSV file."""
    bus_stops.to_csv(output_file, index=False)
    print(f"Bus stops data saved as '{output_file}'.")

def main():
    # File paths
    crash_file = 'data/crash_collisions.csv'
    bus_stop_file = 'data/bus_stop_locations.csv'

    # Load data with explicit data types
    crashes = pd.read_csv(crash_file, dtype={
        'CRASH DATE': 'object',
        'CRASH TIME': 'object',
        'BOROUGH': 'object',
        'ZIP CODE': 'object',  # Specify ZIP CODE as object
        'LATITUDE': 'float64',
        'LONGITUDE': 'float64',
        'LOCATION': 'object',
        'ON STREET NAME': 'object',
        'CROSS STREET NAME': 'object',
        'OFF STREET NAME': 'object',
        'NUMBER OF PERSONS INJURED': 'float64',
        'NUMBER OF PERSONS KILLED': 'float64',
        'NUMBER OF PEDESTRIANS INJURED': 'int64',
        'NUMBER OF PEDESTRIANS KILLED': 'int64',
        'NUMBER OF CYCLIST INJURED': 'int64',
        'NUMBER OF CYCLIST KILLED': 'int64',
        'NUMBER OF MOTORIST INJURED': 'int64',
        'NUMBER OF MOTORIST KILLED': 'int64',
        'CONTRIBUTING FACTOR VEHICLE 1': 'object',
        'CONTRIBUTING FACTOR VEHICLE 2': 'object',
        'CONTRIBUTING FACTOR VEHICLE 3': 'object',
        'CONTRIBUTING FACTOR VEHICLE 4': 'object',
        'CONTRIBUTING FACTOR VEHICLE 5': 'object',
        'COLLISION_ID': 'int64',
        'VEHICLE TYPE CODE 1': 'object',
        'VEHICLE TYPE CODE 2': 'object',
        'VEHICLE TYPE CODE 3': 'object',
        'VEHICLE TYPE CODE 4': 'object',
        'VEHICLE TYPE CODE 5': 'object'
    }, low_memory=False)

    bus_stops = pd.read_csv(bus_stop_file, dtype={
        'the_geom': 'object',
        'BoroCode': 'int64',
        'BoroName': 'object',
        'BoroCD': 'int64',
        'CounDist': 'int64',
        'AssemDist': 'int64',
        'StSenDist': 'int64',
        'CongDist': 'int64',
        'Shelter_ID': 'object',  # Ensure this matches the column name in your CSV
        'Corner': 'object',
        'On_Street': 'object',
        'Cross_Stre': 'object',
        'Longitude': 'float64',
        'Latitude': 'float64',
        'NTAName': 'object',
        'FEMAFldz': 'object',
        'FEMAFldT': 'object',
        'HrcEvac': 'float64'
    }, low_memory=False)

    # Clean data
    crashes = crashes.dropna(subset=['LATITUDE', 'LONGITUDE']).rename(columns={'LATITUDE': 'latitude', 'LONGITUDE': 'longitude'})
    bus_stops = bus_stops.dropna(subset=['Latitude', 'Longitude']).rename(columns={'Latitude': 'latitude', 'Longitude': 'longitude'})

    # Top bus stop IDs
    top_ids = [2008, 1788, 1586, 1927, 1618, 1604, 148, 2663, 3059, 3183]

    # Get hardcoded locations for the top bus stops
    top_bus_stop_locations = get_locations_for_top_bus_stops(bus_stops, top_ids)

    # Debugging: Check if top_bus_stop_locations is empty
    if top_bus_stop_locations.empty:
        print("Warning: No valid bus stop locations found for the provided top IDs.")
        print("Check the following top IDs:", top_ids)
        print("Available bus stop IDs:", bus_stops['Shelter_ID'].unique())
        return  # Exit the main function if no valid locations are found

    # Plot crashes and top bus stops
    plot_crashes_and_top_bus_stops(crashes, top_bus_stop_locations)

    # Save bus stops data for analysis
    save_bus_stops_data(bus_stops)

if __name__ == "__main__":
    main()