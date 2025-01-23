from data_cleaning import load_data, clean_data
from proximity_analysis import calculate_proximity
from data_visualization import create_map
import pandas as pd
from bus_stop_accident_analysis import load_data, clean_data, calculate_accidents_near_bus_stops, plot_bus_stop_accident_percentages


def main():
    # File paths
    crash_file = 'data/crash_collisions.csv'
    bus_stop_file = 'data/bus_stop_locations.csv'


    print("Loading data...")
    crashes, bus_stops = load_data(crash_file, bus_stop_file)
    print("Data loaded. Cleaning data...")
    crashes, bus_stops = clean_data(crashes, bus_stops)
    print(f"Number of crashes: {len(crashes)}")
    print(f"Number of bus stops: {len(bus_stops)}")


    print("Calculating accidents near bus stops...")
    bus_stops_with_accidents, bus_stops_without_accidents, total_bus_stops = calculate_accidents_near_bus_stops(crashes, bus_stops)


    print("Plotting results...")
    plot_bus_stop_accident_percentages(bus_stops_with_accidents, bus_stops_without_accidents, total_bus_stops)


    print("Process completed.")


if __name__ == "__main__":
    main()
