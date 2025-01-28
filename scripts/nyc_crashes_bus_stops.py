import pandas as pd
import geopandas as gpd
import folium
from folium.plugins import HeatMap
import matplotlib.pyplot as plt

def create_crash_bus_map(crash_file, bus_stop_file, output_file='nyc_crash_map.html'):
    # Read data
    crashes = pd.read_csv(crash_file)
    bus_stops = pd.read_csv(bus_stop_file)

    # Clean and filter coordinates
    crashes = crashes.dropna(subset=['LATITUDE', 'LONGITUDE'])
    bus_stops = bus_stops.dropna(subset=['Latitude', 'Longitude'])

    # Create map centered on NYC
    m = folium.Map(location=[40.7128, -74.0060], zoom_start=10)

    # Prepare crash heatmap data
    heat_data = crashes[['LATITUDE', 'LONGITUDE']].values.tolist()
    HeatMap(heat_data).add_to(m)

    # Add bus stop markers with injury data
    add_bus_stop_markers(bus_stops, crashes, m)

    # Save map
    m.save(output_file)
    print(f"Map saved to {output_file}")

def get_injury_data_within_proximity(crashes, bus_stop, proximity_radius=0.0004):
    """Get injury data for crashes within a specified proximity of a bus stop."""
    # Calculate distance
    nearby_crashes = crashes[
        (abs(crashes['LATITUDE'] - bus_stop['Latitude']) < proximity_radius) &
        (abs(crashes['LONGITUDE'] - bus_stop['Longitude']) < proximity_radius)
    ]

    # Count injuries by type
    pedestrian_injuries = nearby_crashes['NUMBER OF PEDESTRIANS INJURED'].sum()
    cyclist_injuries = nearby_crashes['NUMBER OF CYCLIST INJURED'].sum()
    motorist_injuries = nearby_crashes['NUMBER OF MOTORIST INJURED'].sum()

    # Create a dictionary for injuries
    injury_counts = {
        'Pedestrian': pedestrian_injuries,
        'Cyclist': cyclist_injuries,
        'Motorist': motorist_injuries
    }

    total_injuries = sum(injury_counts.values())
    
    # Calculate percentages
    injury_percentages = {injury: (count / total_injuries * 100).round(2) if total_injuries > 0 else 0 for injury, count in injury_counts.items()}

    return injury_counts, injury_percentages

def add_bus_stop_markers(bus_stops, crashes, map_object):
    """Add bus stop markers with injury data to the map."""
    for _, stop in bus_stops.iterrows():
        injury_counts, injury_percentages = get_injury_data_within_proximity(crashes, stop)

        # Prepare injury data for popup
        injury_info = ', '.join(
            [f"{injury}: {count} ({percentage}%)" for injury, count, percentage in zip(injury_counts.keys(), injury_counts.values(), injury_percentages.values())]
        )

        folium.Marker(
            location=[stop['Latitude'], stop['Longitude']],
            popup=f"Bus Stop ID: {stop['Shelter_ID']}<br>Injuries: {injury_info}",
            icon=folium.Icon(color='blue', icon='bus')
        ).add_to(map_object)

def calculate_bus_stop_injury_distribution(bus_stops, crashes):
    """Calculate the percentage distribution of injuries for bus stops within a 150-foot radius."""
    total_injury_counts = {'Pedestrian': 0, 'Cyclist': 0, 'Motorist': 0}

    for _, stop in bus_stops.iterrows():
        injury_counts, _ = get_injury_data_within_proximity(crashes, stop, proximity_radius=0.0004)
        for injury_type in total_injury_counts.keys():
            total_injury_counts[injury_type] += injury_counts.get(injury_type, 0)

    total_injuries = sum(total_injury_counts.values())
    
    # Calculate percentages
    injury_percentages = {injury: (count / total_injuries * 100).round(2) if total_injuries > 0 else 0 for injury, count in total_injury_counts.items()}

    return injury_percentages

def calculate_overall_injury_distribution(crashes):
    """Calculate the percentage distribution of injuries from the crash dataset."""
    overall_counts = {
        'Pedestrian': crashes['NUMBER OF PEDESTRIANS INJURED'].sum(),
        'Cyclist': crashes['NUMBER OF CYCLIST INJURED'].sum(),
        'Motorist': crashes['NUMBER OF MOTORIST INJURED'].sum()
    }
    
    total_injuries = sum(overall_counts.values())
    
    # Calculate percentages
    injury_percentages = {injury: (count / total_injuries * 100).round(2) if total_injuries > 0 else 0 for injury, count in overall_counts.items()}

    return injury_percentages

def main():
    crash_file = 'data/crash_collisions.csv'
    bus_stop_file = 'data/bus_stop_locations.csv'
    crashes = pd.read_csv(crash_file)
    bus_stops = pd.read_csv(bus_stop_file)

    # Calculate distributions
    bus_stop_distribution = calculate_bus_stop_injury_distribution(bus_stops, crashes)
    overall_distribution = calculate_overall_injury_distribution(crashes)

    # Print the distributions
    print("Injury Percentage Distribution within 150 feet of Bus Stops:")
    print(bus_stop_distribution)
    print("\nOverall Injury Percentage Distribution from Crash Dataset:")
    print(overall_distribution)

    # Visualize the distributions using a bar chart
    labels = list(bus_stop_distribution.keys())
    bus_stop_values = list(bus_stop_distribution.values())
    overall_values = list(overall_distribution.values())

    x = range(len(labels))

    # Change colors to blue and orange for better accessibility
    plt.bar(x, bus_stop_values, width=0.4, label='Bus Shelters', color='blue', align='center')
    plt.bar([p + 0.4 for p in x], overall_values, width=0.4, label='Overall', color='orange', align='center')

    # Add percentage labels on top of the bars with larger font size
    for i, value in enumerate(bus_stop_values):
        plt.text(i, value + 1, f"{value}%", ha='center', va='bottom', fontsize=12, fontweight='bold')  # Adjust fontsize and fontweight

    for i, value in enumerate(overall_values):
        plt.text(i + 0.4, value + 1, f"{value}%", ha='center', va='bottom', fontsize=12, fontweight='bold')  # Adjust fontsize and fontweight

    plt.xlabel('Injury Type', fontsize=14, fontweight='bold')  # Larger font for x-axis label
    plt.ylabel('Percentage of Injuries', fontsize=14, fontweight='bold')  # Larger font for y-axis label
    plt.title('Injury Percentage Distribution Comparison', fontsize=16, fontweight='bold')  # Larger font for title
    plt.xticks([p + 0.2 for p in x], labels, fontsize=12)  # Larger font for x-tick labels
    plt.legend(fontsize=12)  # Larger font for legend
    plt.show()

if __name__ == "__main__":
    main()