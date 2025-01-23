import geopandas as gpd
from shapely.geometry import Point


def calculate_proximity(crashes, bus_stops):
    """Analyze proximity of crashes to bus stops."""
    # Convert to GeoDataFrames
    crashes['geometry'] = crashes.apply(lambda row: Point(row['longitude'], row['latitude']), axis=1)
    bus_stops['geometry'] = bus_stops.apply(lambda row: Point(row['longitude'], row['latitude']), axis=1)


    crashes_gdf = gpd.GeoDataFrame(crashes, geometry='geometry', crs="EPSG:4326")
    bus_stops_gdf = gpd.GeoDataFrame(bus_stops, geometry='geometry', crs="EPSG:4326")


    # Reproject to a projected CRS (e.g., UTM)
    crashes_gdf = crashes_gdf.to_crs(epsg=3857)  # Change EPSG code as needed
    bus_stops_gdf = bus_stops_gdf.to_crs(epsg=3857)  # Change EPSG code as needed


    # Perform spatial join to find crashes within a certain distance from bus stops
    nearby_crashes = gpd.sjoin_nearest(crashes_gdf, bus_stops_gdf, how='inner', distance_col='distance')


    # Ensure latitude and longitude are included in the result
    nearby_crashes['latitude'] = nearby_crashes.geometry.y
    nearby_crashes['longitude'] = nearby_crashes.geometry.x


    return nearby_crashes
