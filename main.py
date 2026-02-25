import geopandas as gpd
import matplotlib.pyplot as plt
from adjustText import adjust_text

# Load world map
countries = gpd.read_file("ne_110m_admin_0_countries.shp")

# Color specific countries
countries["color"] = "white"
countries.loc[countries["NAME"] == "France", "color"] = "lightblue"
countries.loc[countries["NAME"] == "Brazil", "color"] = "lightblue"


# Draw the map
fig, ax = plt.subplots(figsize=(15, 8))
countries.plot(ax=ax, color=countries["color"], edgecolor="gray")

# List of dots and their labels
points = [
    (2.35, 48.85, "France 90%"),
    (-47.9, -15.7, "Brazil 30%"),
    (-47.9, -15.7, "hi"),
]

texts = []
for lon, lat, label in points:
    ax.plot(lon, lat, "o", color="gray", markersize=3)
    texts.append(ax.text(lon, lat, label, fontsize=9,
    bbox=dict(boxstyle="round,pad=0.3, rounding_size=0.5", facecolor="white", edgecolor="lightblue", linewidth=0.8)))

# This automatically moves labels so they don't overlap
adjust_text(texts,arrowprops=dict(arrowstyle="-", color="gray", lw=0.8), expand_text=(2, 2))

ax.axis("off")
plt.savefig("map.png", dpi=300)
print("Saved map.png!")