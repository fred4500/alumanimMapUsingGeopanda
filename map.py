
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from adjustText import adjust_text
import pandas as pd
 
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "configs"))
 
from config_appearance import *
from config_text_adjustment import *
from config_data import *
 
# --- Load data ---
dfWorld   = pd.read_csv(DATA_PATH)
dfLatLong = pd.read_csv(LAT_LONG_PATH).set_index("UN_A3")
dfEurop   = pd.read_csv(EUROP_PATH)
dfRings   = pd.read_csv(RING_PATH)
 
# --- Helpers ---
def parseRate(value):
    return float(str(value).strip().replace('%', '')) / 100
 
def resolveCountry(name):
    return NAME_MAP.get(name, name)
 
# --- Map setup ---
countries = gpd.read_file(SHAPEFILE_PATH)
countries["color"] = NO_DATA_COLOR
 
cmap = plt.cm.get_cmap(HEATMAP_COLORMAP)
norm = mcolors.Normalize(vmin=HEATMAP_MIN, vmax=HEATMAP_MAX)
 
# --- Color Europe countries ---
for row in dfEurop.itertuples():
    country = resolveCountry(row[2])
 
    match = countries[countries["NAME"] == country]
    rate = parseRate(dfWorld[dfWorld.iloc[:, 1] == 'Europe'].iloc[:, 4].values[0])
    if match.empty:
        print(f"No match found for: {country}")
    else:
        color = mcolors.to_hex(cmap(norm(rate))) if HEATMAP else PRIMARY_COLOR
        countries.loc[countries["NAME"] == country, "color"] = color
 
# --- Figure ---
fig, ax = plt.subplots(figsize=(MAP_WIDTH, MAP_HEIGHT))
 
points       = []
ringCmap     = plt.cm.get_cmap(RING_COLORMAP)
ring_artists = []
 
# --- Color world countries and collect label points ---
for row in dfWorld.itertuples():
    country = row[2]
    unCode  = row[3]
    pom     = row[4]
    rate    = parseRate(row[5])
 
    if country in SKIP_COUNTRIES:
        continue
 
    resolvedCountry = resolveCountry(country)
 
    if unCode in dfLatLong.index:
        latLongRow = dfLatLong.loc[unCode]
        lat = latLongRow["lat"]
        lon = latLongRow["lon"]
        match = countries[countries["NAME"] == resolvedCountry]
 
        if match.empty and resolvedCountry != "Europe":
            print(f"No match found for: {resolvedCountry}")
        else:
            color = mcolors.to_hex(cmap(norm(rate))) if HEATMAP else PRIMARY_COLOR
            countries.loc[countries["NAME"] == resolvedCountry, "color"] = color
 
            # Label — use override name if defined, otherwise country name from CSV
            label_name = LABEL_OVERRIDES.get(int(unCode), country)
            points.append((lon, lat, f"{label_name}: {rate:.0%}", int(unCode)))
 
            if USE_RINGS:
                ringSize = MAX_RING_SIZE
                for ring in range(len(dfRings) - 1, -1, -1):
                    ringRow = dfRings.iloc[ring]
                    if int(pom) >= int(ringRow.iloc[1]):
                        circle, = ax.plot(lon, lat, marker='o', color=ringCmap(1 - ring / 5), markersize=ringSize)
                        ring_artists.append(circle)
                    ringSize -= STEP_DOWN_PER_RING
                circle, = ax.plot(lon, lat, marker='o', color=RING_ZERRO_POM_COLOR, markersize=RING_ZERRO_POM_SIZE)
                ring_artists.append(circle)


 
# --- Plot countries ---
countries.plot(ax=ax, color=countries["color"], edgecolor=SECONDARY_COLOR)
 
# --- Colorbar ---
if HEATMAP:
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    plt.colorbar(sm, ax=ax, orientation="horizontal", fraction=0.03, pad=0.02, label="Recycling Rate (%)")
 
# --- Labels and leader lines ---
if points:
    texts = []
    for lon, lat, label, unCode in points:
        texts.append(ax.text(
            lon, lat, label,
            fontsize=FONT_SIZE,
            bbox=dict(
                boxstyle=LABEL_BOXSTYLE,
                facecolor=LABEL_FACE_COLOR,
                edgecolor=LABEL_EDGE_COLOR,
                linewidth=LABEL_LINE_WIDTH,
            )
        ))
 
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
 
    # Build optional kwargs for adjustText
    adjust_kwargs = dict(
        expand=EXPAND,
        force_text=FORCE_TEXT,
        force_points=FORCE_POINTS,
        avoid_self=AVOID_SELF,
        max_move=MAX_MOVE,
        iterations=ITERATIONS,
    )
    if AVOID_COUNTRIES:
        adjust_kwargs["add_objects"] = ax.collections
    if POINT_PADDING is not None:
        adjust_kwargs["point_padding"] = POINT_PADDING
    if AVOID_AXES:
        adjust_kwargs["avoid_axes"] = AVOID_AXES
    if PRECISION is not None:
        adjust_kwargs["precision"] = PRECISION
 
    adjust_text(texts, **adjust_kwargs)
 
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
 
    # Apply manual offsets on top of auto-adjusted positions
    # Matches by country name (label before ":") or UN code (integer)
    for text, (lon, lat, label, unCode) in zip(texts, points):
        country_name = label.split(":")[0]
        offset = MANUAL_ADJUSTMENTS.get(country_name) or MANUAL_ADJUSTMENTS.get(unCode)
        if offset:
            dx, dy = offset
            x, y = text.get_position()
            text.set_position((x + dx, y + dy))
 
    for text, (lon, lat, label, unCode) in zip(texts, points):
        label_x, label_y = text.get_position()
        ax.plot([lon, label_x], [lat, label_y], color=LEADER_LINE_COLOR, lw=LEADER_LINE_WIDTH)
 
ax.axis("off")
plt.savefig(f"{MAP_OUTPUT_NAME}.png", dpi=MAP_DPI, bbox_inches='tight', pad_inches=0.0)
print(f"Saved {MAP_OUTPUT_NAME}.png!")
