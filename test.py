import geopandas as gpd
import pandas as pd

countries = gpd.read_file("ne_110m_admin_0_countries.shp")

countries["lon"] = countries.geometry.centroid.x
countries["lat"] = countries.geometry.centroid.y

# UN M49 code is already in the shapefile under this column
print(countries.columns.tolist())  # run this first to find the exact column name
countries[["NAME", "UN_A3", "lon", "lat"]].to_csv("countries_latlon.csv", index=False)
print("Saved!")