import pandas as pd

def check_data_types(crash_file, bus_stop_file):
    """Check and print the column names and their data types for both CSV files."""
    # Load the crash data
    crashes = pd.read_csv(crash_file)
    print("Crash Data Columns and Data Types:")
    print(crashes.dtypes)
    print("\n")

    # Load the bus stop data
    bus_stops = pd.read_csv(bus_stop_file)
    print("Bus Stop Data Columns and Data Types:")
    print(bus_stops.dtypes)

def main():
    # File paths
    crash_file = 'data/crash_collisions.csv'
    bus_stop_file = 'data/bus_stop_locations.csv'

    # Check data types
    check_data_types(crash_file, bus_stop_file)

if __name__ == "__main__":
    main()