import sys
import json
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from adjustText import adjust_text
import pandas as pd

# ── Load config from GUI (passed as JSON string arg) or use defaults ──────────
if len(sys.argv) > 1:
    config = json.loads(sys.argv[1])
else:
    config = {}

primaryColor   = config.get("primaryColor",   "lightblue")
secondaryColor = config.get("secondaryColor", "gray")
textColor      = config.get("textColor",      "black")
noDataColor    = config.get("noDataColor",    "white")
fontSize       = config.get("fontSize",       20)
useGradient    = config.get("useGradient",    True)
gradientMin    = config.get("gradientMin",    0.20)
gradientMax    = config.get("gradientMax",    0.90)
dataPath       = config.get("dataPath",       "/workspaces/alumanimMapUsingGeopanda/data/Aluminium Can Recycling.csv")
latLongPath    = config.get("latLongPath",    "/workspaces/alumanimMapUsingGeopanda/data/countries_latlon.csv")
europPath      = config.get("europPath",      "/workspaces/alumanimMapUsingGeopanda/data/Aluminium Can Recycling Europe.csv")
mapName        = config.get("mapName",        "test")
mapWith        = config.get("mapWith",        40)
mapDepht       = config.get("mapDepht",       20)

# ── Data loading ──────────────────────────────────────────────────────────────
dfWorld   = pd.read_csv(dataPath)
dfLatLong = pd.read_csv(latLongPath).set_index("UN_A3")
dfEurop   = pd.read_csv(europPath)

def parseRate(value):
    return float(str(value).strip().replace('%', '')) / 100

nameMap = {
    "Turkiye":       "Turkey",
    "United States": "United States of America",
}

def resolveCountry(name):
    return nameMap.get(name, name)

countries = gpd.read_file("ne_110m_admin_0_countries.shp")
countries["color"] = noDataColor

cmap = plt.cm.RdYlGn
norm = mcolors.Normalize(vmin=gradientMin, vmax=gradientMax)

# ── Colour Europe ─────────────────────────────────────────────────────────────
for row in dfEurop.itertuples():
    country = resolveCountry(row[2])
    rate    = parseRate(row[3])

    match = countries[countries["NAME"] == country]
    if match.empty:
        print(f"No match found for: {country}")
    else:
        color = mcolors.to_hex(cmap(norm(rate))) if useGradient else primaryColor
        countries.loc[countries["NAME"] == country, "color"] = color

# ── World points ──────────────────────────────────────────────────────────────
skipCountries = {"World"}
points = []

for row in dfWorld.itertuples():
    year    = row[1]
    country = row[2]
    unCode  = row[3]
    pom     = row[4]
    rate    = parseRate(row[5])

    if country in skipCountries:
        continue

    resolvedCountry = resolveCountry(country)

    if unCode in dfLatLong.index:
        latLongRow = dfLatLong.loc[unCode]
        lat = latLongRow["lat"]
        lon = latLongRow["lon"]
        match = countries[countries["NAME"] == resolvedCountry]
        if match.empty:
            print(f"No match found for: {resolvedCountry}")
        else:
            color = mcolors.to_hex(cmap(norm(rate))) if useGradient else primaryColor
            countries.loc[countries["NAME"] == resolvedCountry, "color"] = color
        if int(unCode) == 784:
            points.append((lon, lat, f"UAE: {rate:.0%}"))
        else:
            points.append((lon, lat, f"{country}: {rate:.0%}"))

# ── Plot ──────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(mapWith, mapDepht))
countries.plot(ax=ax, color=countries["color"], edgecolor=secondaryColor)

if useGradient:
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    plt.colorbar(sm, ax=ax, orientation="horizontal", fraction=0.03,
                 pad=0.02, label="Recycling Rate (%)")

if points:
    texts = []
    for lon, lat, label in points:
        texts.append(ax.text(lon, lat, label, fontsize=fontSize,
            color=textColor,
            bbox=dict(boxstyle="round,pad=0.3,rounding_size=0.5",
                      facecolor="white", edgecolor=primaryColor, linewidth=0.8)))

    centroids = countries.geometry.centroid
    obs_x = centroids.x.tolist()
    obs_y = centroids.y.tolist()

    adjust_text(texts,
        x=obs_x,
        y=obs_y,
        expand_text=(fontSize * 6, fontSize * 6),
        expand_points=(fontSize * 6, fontSize * 6),
        force_text=(fontSize * 0.5, fontSize * 0.5),
        force_points=(fontSize * 1.5, fontSize * 1.5),
        avoid_self=True,
        max_move=50,
        iterations=10000)

    for text, (lon, lat, label) in zip(texts, points):
        label_x, label_y = text.get_position()
        ax.plot([lon, label_x], [lat, label_y], color=secondaryColor, lw=0.8)

ax.axis("off")
plt.savefig(f"{mapName}.png", dpi=300)
print(f"Saved {mapName}.png!")