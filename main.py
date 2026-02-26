import geopandas as gpd
import matplotlib.pyplot as plt
from adjustText import adjust_text
import pandas as pd
from scipy.spatial.distance import cdist
import numpy as np

filePath = "/workspaces/alumanimMapUsingGeopanda/data/Aluminium Can Recycling.csv"
dfRecyceling = pd.read_csv(filePath)
latLongPath = "/workspaces/alumanimMapUsingGeopanda/data/countries_latlon.csv"
dfLatLong = pd.read_csv(latLongPath)

countries = gpd.read_file("ne_110m_admin_0_countries.shp")
countries["color"] = "white"

for i in dfRecyceling["UN M49 Code"]:
    row = dfLatLong[dfLatLong["UN_A3"] == i]
    if not row.empty:
        countries.loc[countries["NAME"] == row["NAME"].values[0], "color"] = "lightblue"

fig, ax = plt.subplots(figsize=(15, 8))
countries.plot(ax=ax, color=countries["color"], edgecolor="gray")

points = []
for Country, UnCode, RecyclingRate in zip(dfRecyceling["Country"], dfRecyceling["UN M49 Code"], dfRecyceling["Recycled Rate"]):
    row = dfLatLong[dfLatLong["UN_A3"] == UnCode]
    if not row.empty:
        lon = row["lon"].values[0]
        lat = row["lat"].values[0]
        points.append((lon, lat, f"{Country} {RecyclingRate}"))

if len(points) > 0:
    coords = [(lon, lat) for lon, lat, _ in points]
    distances = cdist(coords, coords)

    texts = []
    for i, (lon, lat, label) in enumerate(points):
        nearby = np.sum(distances[i] < 50) - 1
        fontsize = max(7, 10 - nearby)
        ax.plot(lon, lat, "o", color="gray", markersize=3)
        texts.append(ax.text(lon, lat, label, fontsize=fontsize,
            bbox=dict(boxstyle="round,pad=0.3,rounding_size=0.5", facecolor="white", edgecolor="lightblue", linewidth=0.8)))

    adjust_text(texts, expand_text=(40, 40), expand_points=(40, 40), force_text=(3, 3), force_points=(3, 3))

    # draw lines from dot to label
    for text, (lon, lat, label) in zip(texts, points):
        label_x, label_y = text.get_position()
        ax.plot([lon, label_x], [lat, label_y], color="gray", lw=0.8)

ax.axis("off")
plt.savefig("map.png", dpi=300)
print("Saved map.png!")