# =============================================================================
# DATA CONFIG
# File paths and data-handling settings for the recycling rate map
# =============================================================================

# --- Input file paths ---
# Main world dataset: must have columns [year, country, UN_A3, pom, rate]
DATA_PATH = "/workspaces/alumanimMapUsingGeopanda/data/Aluminium Can Recycling.csv"

# Latitude/longitude lookup table: indexed by UN_A3 country code
# Required columns: UN_A3, lat, lon
LAT_LONG_PATH = "/workspaces/alumanimMapUsingGeopanda/data/countries_latlon.csv"

# Europe-specific dataset: merged on top of the world data for EU countries
# Allows higher-detail European figures to override the global figures
EUROP_PATH = "/workspaces/alumanimMapUsingGeopanda/data/Aluminium Can Recycling Europe.csv"

# Optional dataset used for ring visualisation (POM volume tiers).
# Ring sizing and color settings live in config_appearance.py.
RING_PATH = "/workspaces/alumanimMapUsingGeopanda/data/Aluminium Can Recycling POM.csv"

# --- Country name mapping ---
# Maps names as they appear in your CSV → names as they appear in the shapefile.
# Add entries here whenever a "No match found for:" warning is printed.
NAME_MAP = {
    "Turkiye":       "Turkey",
    "United States": "United States of America",
}

# --- Countries to skip entirely ---
# Aggregate rows that don't correspond to a single mappable country.
SKIP_COUNTRIES = {"World"}

# --- Special label overrides ---
# Maps UN_A3 code (integer) → custom display label.
# Used when the default country name is too long or ambiguous on the map.
LABEL_OVERRIDES = {
    784: "UAE",   # United Arab Emirates → shorter label
}

# --- Shapefile ---
# Path to the Natural Earth 110m admin-0 shapefile (or any compatible .shp).
# Download from: https://www.naturalearthdata.com/downloads/110m-cultural-vectors/
SHAPEFILE_PATH = "mapData/ne_110m_admin_0_countries.shp"