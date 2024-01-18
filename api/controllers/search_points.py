import numpy as np
import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt
import folium
from sklearn.cluster import KMeans

def generate_clustered_grid_points(min_lat, max_lat, min_lng, max_lng, interval, num_clusters):
    # Generate grid points within the specified latitude and longitude range
    lats = np.arange(min_lat, max_lat, interval)
    lngs = np.arange(min_lng, max_lng, interval)

    # Create a list of tuples representing grid points
    grid_points = [(lat, lng) for lat in lats for lng in lngs]

    # Convert grid points to a NumPy array
    data = np.array(grid_points)

    # Apply K-Means clustering
    kmeans = KMeans(n_clusters=num_clusters, random_state=42).fit(data)

    # Get the cluster centers
    cluster_centers = kmeans.cluster_centers_

    # Convert cluster centers back to tuples
    clustered_grid_points = [tuple(center) for center in cluster_centers]

    return clustered_grid_points

def get_brazil_search_points():
    radius = 100000
    min_latitude, max_latitude = -34.8, 5.2  # Approximate latitude range of Brazil
    min_longitude, max_longitude = -74.0, -34.8  # Approximate longitude range of Brazil

    # Set the interval for grid points (adjust as needed for your precision)
    interval = 1.0  # 1 degree interval
    num_clusters = 650

    clustered_grid_points = generate_clustered_grid_points(min_latitude, max_latitude, min_longitude, max_longitude, interval, num_clusters)
    map_center = [-14.2350, -51.9253]  # Approximate center of Brazil
    mymap = folium.Map(location=map_center, zoom_start=4)

    for point in clustered_grid_points:
        print(point)
        # folium.Marker(location=point, popup='Point').add_to(mymap)
        folium.Circle(location=point, radius=radius, color='blue', fill=True, fill_color='blue', fill_opacity=0.2).add_to(mymap)

    # Save the map as an HTML file or display it in a Jupyter notebook
    mymap.save('map_with_circles.html')



