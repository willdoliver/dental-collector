import os
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
import folium
import traceback, logging
from shapely.geometry import Point
from sklearn.cluster import KMeans
from api.helpers.logger_message_helper import LoggerMessageHelper
from api.helpers.logfile_helper import LogfileHelper

class SearchPointsHelper():
    def get_brazil_search_points(self):
        try:
            radius = 100000
            min_latitude, max_latitude = -34.8, 5.2  # Approximate latitude range of Brazil
            min_longitude, max_longitude = -74.0, -34.8  # Approximate longitude range of Brazil

            # Set the interval for grid points (adjust as needed for your precision)
            interval = 1.0  # 1 degree interval
            num_clusters = 1300

            clustered_grid_points = SearchPointsHelper.__generate_clustered_grid_points(min_latitude, max_latitude, min_longitude, max_longitude, interval, num_clusters)
            map_center = [-14.2350, -51.9253]  # Approximate center of Brazil
            mymap = folium.Map(location=map_center, zoom_start=4)

            brazil_points = SearchPointsHelper.__point_is_in_brazil(clustered_grid_points)

            for point in brazil_points:
                folium.Marker(location=point, popup=point).add_to(mymap)
                folium.Circle(location=point, radius=radius, color='green', fill=True, fill_color='green', fill_opacity=0.2).add_to(mymap)

            # Save the map as an HTML file or display it in a Jupyter notebook
            mymap.save('map_with_circles.html')
            return brazil_points

        except Exception as e:
                full_traceback = traceback.format_exc()
                logging.error(f"Exception occurred: {full_traceback}")

                LoggerMessageHelper.log_message(
                    LogfileHelper.get_log_file('unimed'),
                    f'except get_brazil_search_points error: {full_traceback}'
                )
    def __generate_clustered_grid_points(min_lat, max_lat, min_lng, max_lng, interval, num_clusters):
        # Generate grid points within the specified latitude and longitude range
        lats = np.arange(min_lat, max_lat, interval)
        lngs = np.arange(min_lng, max_lng, interval)

        # Create a list of tuples representing grid points
        grid_points = [(lat, lng) for lat in lats for lng in lngs]

        # Convert grid points to a NumPy array
        data = np.array(grid_points)

        # Apply K-Means clustering
        kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init='auto').fit(data)

        # Get the cluster centers
        cluster_centers = kmeans.cluster_centers_

        # Convert cluster centers back to tuples
        clustered_grid_points = [tuple(center) for center in cluster_centers]

        return clustered_grid_points

    def __point_is_in_brazil(points):
        try:
            # Function to check if a point is within Brazil
            def is_in_brazil(point):
                point = Point(point)
                return brazil_borders.geometry.contains(point).any()

            sep = os.path.sep
            # Load a GeoDataFrame of Brazil's borders
            brazil_borders = gpd.read_file(os.getcwd() + f"{sep}api{sep}uploads{sep}ne_10m_admin_0_countries{sep}ne_10m_admin_0_countries.shp")
            brazil_points = []
            false_positives_blocks = [
                (-11.7, -66),
                (-14, -60.5),
                (-30, -58),
                (-4, -70),
            ]

            for point in points:
                if point[0] <= false_positives_blocks[0][0] and point[1] <= false_positives_blocks[0][1]:
                    print(point, ' - ', false_positives_blocks[0])
                elif point[0] <= false_positives_blocks[1][0] and point[1] <= false_positives_blocks[1][1]:
                    print(point, ' - ', false_positives_blocks[1])
                elif point[0] <= false_positives_blocks[2][0] and point[1] <= false_positives_blocks[2][1]:
                    print(point, ' - ', false_positives_blocks[2])
                elif point[0] >= false_positives_blocks[3][0] and point[1] <= false_positives_blocks[3][1]:
                    print(point, ' - ', false_positives_blocks[3])
                else:
                    if is_in_brazil([point[1], point[0]]):
                        brazil_points.append(point)

            return brazil_points
        except Exception as e:
                full_traceback = traceback.format_exc()
                logging.error(f"Exception occurred: {full_traceback}")

                LoggerMessageHelper.log_message(
                    LogfileHelper.get_log_file('unimed'),
                    f'except point_is_in_brazil error: {full_traceback}'
                )
