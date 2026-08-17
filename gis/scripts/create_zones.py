from pathlib import Path
import geopandas as gpd
from shapely.geometry import box

BASE_DIR = Path(__file__).resolve().parents[2]

ROAD_FILE = BASE_DIR / "data" / "raw" / "gis" / "roads.geojson"
OUTPUT_DIR = BASE_DIR / "data" / "processed" / "gis"
OUTPUT_FILE = OUTPUT_DIR / "zones.geojson"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MINE_ID = "MINE-001"

GRID_ROWS = 3
GRID_COLS = 3

print("==========================================")
print("MineGuard AI - Mine Zone Generator")
print("==========================================")

if not ROAD_FILE.exists():
    raise FileNotFoundError(
        f"Road dataset not found:\n{ROAD_FILE}\n"
        "Make sure roads.geojson exists in data/raw/gis/"
    )

print("\nLoading real GIS road data...")

roads = gpd.read_file(ROAD_FILE)

if roads.empty:
    raise ValueError("The road dataset is empty.")

if roads.crs is None:
    raise ValueError("Road dataset has no coordinate reference system.")

roads = roads.to_crs("EPSG:4326")

minx, miny, maxx, maxy = roads.total_bounds

print("\nStudy area derived from GIS data:")
print(f"West  : {minx:.6f}")
print(f"South : {miny:.6f}")
print(f"East  : {maxx:.6f}")
print(f"North : {maxy:.6f}")

width = (maxx - minx) / GRID_COLS
height = (maxy - miny) / GRID_ROWS

zones = []

zone_number = 1

for row in range(GRID_ROWS):
    for col in range(GRID_COLS):

        west = minx + col * width
        east = minx + (col + 1) * width

        south = miny + row * height
        north = miny + (row + 1) * height

        geometry = box(
            west,
            south,
            east,
            north
        )

        zone_id = f"ZONE-{zone_number:03d}"

        centroid = geometry.centroid

        zones.append(
            {
                "mine_id": MINE_ID,
                "zone_id": zone_id,
                "zone_name": f"Mine Zone {zone_number}",
                "row": row + 1,
                "column": col + 1,
                "status": "PROTOTYPE",
                "risk_level": "UNKNOWN",
                "risk_probability": None,
                "sensor_count": 0,
                "drone_status": "NO_DATA",
                "data_source": "GIS_GRID",
                "boundary_type": "PROTOTYPE_ZONE",
                "centroid_lat": round(centroid.y, 6),
                "centroid_lon": round(centroid.x, 6),
                "geometry": geometry
            }
        )

        zone_number += 1

zones_gdf = gpd.GeoDataFrame(
    zones,
    geometry="geometry",
    crs="EPSG:4326"
)

print(f"\nGenerated {len(zones_gdf)} zones.")

# Calculate accurate area using UTM Zone 45N
# Appropriate for the Jharia region.
zones_projected = zones_gdf.to_crs("EPSG:32645")

zones_gdf["area_hectares"] = (
    zones_projected.geometry.area / 10000
).round(4)

zones_gdf["area_sq_km"] = (
    zones_projected.geometry.area / 1_000_000
).round(6)

zones_gdf["area_hectares"] = zones_gdf["area_hectares"].astype(float)
zones_gdf["area_sq_km"] = zones_gdf["area_sq_km"].astype(float)

# Keep final GIS geometry in WGS84
zones_gdf = zones_gdf.to_crs("EPSG:4326")

# Validate geometries
invalid_count = (~zones_gdf.geometry.is_valid).sum()

if invalid_count > 0:
    print(f"\nFixing {invalid_count} invalid geometries...")
    zones_gdf["geometry"] = zones_gdf.geometry.make_valid()

# Reorder columns for clean GeoJSON output
zones_gdf = zones_gdf[
    [
        "mine_id",
        "zone_id",
        "zone_name",
        "row",
        "column",
        "status",
        "risk_level",
        "risk_probability",
        "sensor_count",
        "drone_status",
        "data_source",
        "boundary_type",
        "centroid_lat",
        "centroid_lon",
        "area_hectares",
        "area_sq_km",
        "geometry"
    ]
]

zones_gdf.to_file(
    OUTPUT_FILE,
    driver="GeoJSON"
)

print("\n==========================================")
print("ZONE GENERATION COMPLETED")
print("==========================================")
print(f"Mine ID       : {MINE_ID}")
print(f"Zones created : {len(zones_gdf)}")
print(f"Output file   : {OUTPUT_FILE}")

print("\nGenerated zones:")

for _, zone in zones_gdf.iterrows():
    print(
        f"{zone['zone_id']} | "
        f"Area: {zone['area_hectares']:.2f} ha | "
        f"Risk: {zone['risk_level']}"
    )

print("\nImportant:")
print("These are prototype computational zones.")
print("They are NOT official mine boundaries.")
print("Risk remains UNKNOWN until ML/IoT/Drone data is available.")