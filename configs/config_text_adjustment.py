# =============================================================================
# TEXT ADJUSTMENT CONFIG
# Controls for adjustText — the library that auto-repositions overlapping labels
# Docs: https://github.com/Phlya/adjustText
# =============================================================================
 
# --- Core behavior ---
 
# How much to expand the bounding box around each text label before checking
# for collisions. A tuple (x_factor, y_factor).
# Higher values = labels pushed further apart from each other.
# Default: (1.05, 1.05). Increase if labels still overlap after adjustment.
EXPAND = (1, 1)
 
# Force applied to move text away from OTHER text labels.
# Tuple (x_force, y_force). Higher = stronger repulsion between labels.
# Default: (0.1, 0.25). Raise if labels cluster together.
FORCE_TEXT = (1, 1)
 
# Force applied to move text away from the DATA POINTS (the map coordinates).
# Tuple (x_force, y_force). Higher = labels pushed further from their origin.
# Default: (0.2, 0.5). Raise if labels sit too close to their markers.
FORCE_POINTS = (1, 1)
 
# Whether text labels should repel each other (in addition to repelling points).
# True = labels avoid overlapping each other. Recommended: True.
AVOID_SELF = True
 
# --- Iteration and movement limits ---
 
# Maximum number of iterations the adjustment algorithm will run.
# More iterations = better placement but slower render time.
# Default: 200. Values 300-1000 are reasonable for dense maps.
ITERATIONS = 1000
 
# Maximum distance (in data units) a label is allowed to move from its
# original position. None = unlimited movement.
# Lower values keep labels close to their points; higher allows more freedom.
MAX_MOVE = 1000
 
# --- Optional object avoidance ---
# (These are advanced adjustText options you can enable if needed)
 
# When True, labels will avoid overlapping the country polygons on the map.
# Passes the rendered country patches to adjustText as objects to avoid.
# Can slow down rendering significantly on dense maps.
AVOID_COUNTRIES = False
 
# Minimum distance between a label edge and a data point, in display units.
# None uses adjustText's default. Increase to prevent labels from
# sitting directly on top of their own data point.
POINT_PADDING = None
 
# Whether to also avoid the x and y axis limits (plot edges).
# True prevents labels from running off the visible map area.
AVOID_AXES = False
 
# --- Precision ---
 
# Step size for each nudge during iteration (data units).
# Smaller values = finer adjustment but more iterations needed.
# None uses adjustText's default heuristic.
PRECISION = 0.1
 
# --- Manual label adjustments ---
# Applied after adjustText finishes, as a final nudge on specific labels.
# Key   = country name (string) OR UN A3 code (integer) — either works
#         Name match uses the label as displayed (i.e. LABEL_OVERRIDES value if set)
#         UN code match uses the raw integer code from the CSV
# Value = (x_offset, y_offset) in map coordinate units (degrees)
# Positive x → right, negative x → left
# Positive y → up,    negative y → down
# Example:
#   "Germany": (2, 1)    # match by name  — shift 2° right, 1° up
#   784:       (-3, -2)  # match by UN code (UAE) — shift 3° left, 2° down
MANUAL_ADJUSTMENTS = {
    # "Germany": (2, 1),
    # 784:       (-3, -2),
}