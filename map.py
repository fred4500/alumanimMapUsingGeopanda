import geopandas as gpd
import matplotlib.pyplot as plt
from adjustText import adjust_text
import pandas as pd

primaryColor = "lightblue"
secondaryColor = "gray"
textColor = "black"
noDataColor = "white"
fontSize = 20

dataPath = "/workspaces/alumanimMapUsingGeopanda/data/Aluminium Can Recycling.csv"
latLongPath = "/workspaces/alumanimMapUsingGeopanda/data/countries_latlon.csv"
europPath = "/workspaces/alumanimMapUsingGeopanda/data/Aluminium Can Recycling Europe.csv"

dfWorld = pd.read_csv(dataPath)
dfLatLong = pd.read_csv(latLongPath).set_index("UN_A3")
dfEurop = pd.read_csv(europPath)

worldTitles = dfWorld.columns.to_list()

countries = gpd.read_file("ne_110m_admin_0_countries.shp")
countries["color"] = noDataColor

# color europe countries
for row in dfEurop.itertuples():
    country = row[2]
    match = countries[countries["NAME"] == country]
    if match.empty:
        print(f"No match found for: {country}")
    else:
        countries.loc[countries["NAME"] == country, "color"] = primaryColor

points = []
for row in dfWorld.itertuples():
    year    = row[1]
    country = row[2]
    unCode  = row[3]
    pom     = row[4]
    rate    = row[5]

    if unCode in dfLatLong.index:
        latLongRow = dfLatLong.loc[unCode]
        lat = latLongRow["lat"]
        lon = latLongRow["lon"]
        match = countries[countries["NAME"] == country]
        if match.empty:
            print(f"No match found for: {country}")
        else:
            countries.loc[countries["NAME"] == country, "color"] = primaryColor
        points.append((lon, lat, f"{country}: {rate}"))

fig, ax = plt.subplots(figsize=(40, 20))
countries.plot(ax=ax, color=countries["color"], edgecolor=secondaryColor)

if points:
    texts = []
    for lon, lat, label in points:
        texts.append(ax.text(lon, lat, label, fontsize=fontSize,
            bbox=dict(boxstyle="round,pad=0.3,rounding_size=0.5",
                      facecolor="white", edgecolor=primaryColor, linewidth=0.8)))

    adjust_text(texts,
            expand_text=(fontSize * 6, fontSize * 6),
            expand_points=(fontSize * 6, fontSize * 6),
            force_text=(fontSize * 2, fontSize * 2),
            force_points=(fontSize * 2, fontSize * 2),
            max_move=10,
            iterations=10000)

    for text, (lon, lat, label) in zip(texts, points):
        label_x, label_y = text.get_position()
        ax.plot([lon, label_x], [lat, label_y], color=secondaryColor, lw=0.8)

ax.axis("off")
plt.savefig("test.png", dpi=300)
print("Saved test.png!")