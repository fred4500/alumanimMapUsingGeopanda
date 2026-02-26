import geopandas as gpd
import matplotlib.pyplot as plt
from adjustText import adjust_text
import pandas as pd
from scipy.spatial.distance import cdist
import numpy as np
import config

#BEFORE RUNNINF FOR THE FIRST TIME RUN THIS IN THE TERMINAL:
#pip install geopandas matplotlib adjustText pandas scipy numpy
#run by typing this in to the terminal:
#python main.py

dfRecyceling = pd.read_csv(config.filePath)
latLongPath = "/workspaces/alumanimMapUsingGeopanda/data/countries_latlon.csv"
dfLatLong = pd.read_csv(latLongPath)
dfEurop = pd.read_csv(config.filePathEurop)
dfRecyceling["UN M49 Code"] = dfRecyceling["UN M49 Code"].astype(int)
dfLatLong["UN_A3"] = pd.to_numeric(dfLatLong["UN_A3"], errors="coerce")

# color of the countrys that there is data for
primaryColor = config.primaryColor
# color of the outline of countrys
secondaryColor = config.secondaryColor
#distance is used for automatic font size adjustment chage this value if there is to big of a changr in the font sze form dens to less dens areas
distance = config.distance
#self expaineble but it is to make teh smallest texts larger
minFontsize = config.minFontsize
#how large the max is
maxFontsize = config.maxFontsize

countries = gpd.read_file("ne_110m_admin_0_countries.shp")
countries["color"] = "white"

for UnCode in dfRecyceling["UN M49 Code"]:
    row = dfLatLong[dfLatLong["UN_A3"] == UnCode]
    if not row.empty:
        name = row["NAME"].values[0]
        countries.loc[countries["NAME"] == name, "color"] = primaryColor

for UnCode in dfEurop["UN M49 Code"]:
    row = dfLatLong[dfLatLong["UN_A3"] == UnCode]
    if not row.empty:
        name = row["NAME"].values[0]
        countries.loc[countries["NAME"] == name, "color"] = primaryColor

fig, ax = plt.subplots(figsize=(15, 8))
countries.plot(ax=ax, color=countries["color"], edgecolor=secondaryColor)

points = []
for Country, UnCode, RecyclingRate in zip(dfRecyceling["Country"], dfRecyceling["UN M49 Code"], dfRecyceling["Recycled Rate"]):
    if(Country != "Europe"):
        row = dfLatLong[dfLatLong["UN_A3"] == UnCode]
        if not row.empty:
            lon = row["lon"].values[0]
            lat = row["lat"].values[0]
            points.append((lon, lat, f"{Country} {RecyclingRate}"))
    else:
        row = dfLatLong[dfLatLong["UN_A3"] == 276]
        if not row.empty:
            lon = row["lon"].values[0]
            lat = row["lat"].values[0]
            points.append((lon, lat, f"{Country} {RecyclingRate}"))

if len(points) > 0:
    coords = [(lon, lat) for lon, lat, _ in points]
    distances = cdist(coords, coords)

    texts = []
    for i, (lon, lat, label) in enumerate(points):
        nearby = np.sum(distances[i] < distance) - 1
        fontsize = max(minFontsize, maxFontsize - nearby)
        ax.plot(lon, lat, "o", color=secondaryColor, markersize=3)
        texts.append(ax.text(lon, lat, label, fontsize=fontsize,
            bbox=dict(boxstyle="round,pad=0.3,rounding_size=0.5", facecolor="white", edgecolor= primaryColor, linewidth=0.8)))

    adjust_text(texts, expand_text=(40, 40), expand_points=(40, 40), force_text=(3, 3), force_points=(3, 3))

    # draw lines from dot to label
    for text, (lon, lat, label) in zip(texts, points):
        label_x, label_y = text.get_position()
        ax.plot([lon, label_x], [lat, label_y], color=secondaryColor, lw=0.8)

ax.axis("off")
plt.savefig("map.png", dpi=300)
print("Saved map.png!")