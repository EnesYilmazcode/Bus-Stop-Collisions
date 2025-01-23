import folium


def create_map(nearby_crashes, output_path='outputs/crashes_near_bus_stops.html'):
    """Create an interactive map showing crashes near bus stops."""
    # Center the map around the first crash location
    center_lat = nearby_crashes.iloc[0]['latitude']
    center_long = nearby_crashes.iloc[0]['longitude']


    map_obj = folium.Map(location=[center_lat, center_long], zoom_start=12)


    # Add crash points to the map
    for _, row in nearby_crashes.iterrows():
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=5,
            color='red',
            fill=True,
            fill_color='red',
        ).add_to(map_obj)


    # Save the map
    map_obj.save(output_path)
