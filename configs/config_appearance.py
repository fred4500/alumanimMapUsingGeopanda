# =============================================================================
# APPEARANCE CONFIG
# Visual styling for the recycling rate world map
# =============================================================================

# --- Map dimensions (in inches) ---
MAP_WIDTH  = 15
MAP_HEIGHT = 8

# --- Colors ---
PRIMARY_COLOR   = "lightblue"   # Fill color for non-heatmap countries with data
SECONDARY_COLOR = "gray"        # Border/edge color for all countries
TEXT_COLOR      = "black"       # General text color (currently unused but reserved)
NO_DATA_COLOR   = "white"       # Fill for countries with no data

# --- Font ---
FONT_SIZE = 8                   # Label font size (points) for country annotations

# --- Heatmap mode ---
# True  → countries colored on a green-to-red gradient based on recycling rate
# False → countries with data all get PRIMARY_COLOR (flat blue)
HEATMAP = False

# --- Heatmap color scale ---
# Values outside this range are clamped to the min/max color
HEATMAP_MIN = 0.20              # Rate mapped to the "low" end of the colormap (red)
HEATMAP_MAX = 0.90              # Rate mapped to the "high" end of the colormap (green)

# Matplotlib colormap name to use when HEATMAP = True
# Options: "RdYlGn" (red-yellow-green), "RdYlBu", "coolwarm", "viridis", etc.
HEATMAP_COLORMAP = "RdYlGn"

# --- Country label boxes ---
# Matplotlib fancy bbox style string for annotation boxes
LABEL_BOXSTYLE    = "round,pad=0.3,rounding_size=0.5"
LABEL_FACE_COLOR  = "white"
LABEL_EDGE_COLOR  = PRIMARY_COLOR   # Border color of label box matches primary
LABEL_LINE_WIDTH  = 0.8             # Thickness of label box border

# --- Leader lines (connecting label to point) ---
LEADER_LINE_COLOR = SECONDARY_COLOR
LEADER_LINE_WIDTH = 0.8

# --- Rings ---
# Rings draw concentric circles per country, scaled to POM (put-on-market) volume tiers.
# Each country gets one circle per tier it qualifies for, shrinking inward.

USE_RINGS = True        # True = draw rings; False = skip ring rendering entirely

MAX_RING_SIZE = 40           # Marker size (points) of the outermost/largest ring
STEP_DOWN_PER_RING = 8          # Size reduction per inner ring (= MAX_RING_SIZE / number of tiers)
                                # e.g. 5 tiers → 40, 32, 24, 16, 8
RING_ZERRO_POM_SIZE = 4 # size of the ring each country gets

# Matplotlib colormap used to color each ring by tier index.
# Rings are drawn from outermost (darkest) to innermost (lightest) using
# the expression: ringCmap(1 - ring_index / num_tiers)
RING_COLORMAP = "Blues"         # Options: "Blues", "Oranges", "Greens", "Purples", etc.

RING_ZERRO_POM_COLOR = SECONDARY_COLOR # Color of the ring each country gets

# --- Output ---
MAP_OUTPUT_NAME = "heat"        # Saved as {MAP_OUTPUT_NAME}.png
MAP_DPI         = 300          # Resolution of the output image
