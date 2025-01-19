from data_cleaning import load_data, clean_data
from proximity_analysis import calculate_proximity
from data_visualization import create_map

def main():
    # File paths
    crash_file = 'data/crash_collisions.csv'
    bus_stop_file = 'data/bus_stop_locations.csv'

    # Load data
    crashes, bus_stops = load_data(crash_file, bus_stop_file)

    # Clean data
    crashes, bus_stops = clean_data(crashes, bus_stops)

    # Analyze proximity
    nearby_crashes = calculate_proximity(crashes, bus_stops)

    # Create visualization
    create_map(nearby_crashes)

if __name__ == "__main__":
    main()
