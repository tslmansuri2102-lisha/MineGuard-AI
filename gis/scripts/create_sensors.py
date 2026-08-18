from pathlib import Path
import geopandas as gpd
from shapely.geometry import Point

BASE_DIR = Path(__file__).resolve().parents[2]

ZONE_FILE = BASE_DIR / "data" / "processed" / "gis" / "zones.geojson"
OUTPUT_DIR = BASE_DIR / "data" / "processed" / "gis"
OUTPUT_FILE = OUTPUT_DIR / "sensors.geojson"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MINE_ID = "MINE-001"

print("==========================================")
print("MineGuard AI - Sensor Location Generator")
print("==========================================")

if not ZONE_FILE.exists():
    raise FileNotFoundError(
        f"Zone file not found:\n{ZONE_FILE}\n"
        "Run create_zones.py first."
    )

zones = gpd.read_file(ZONE_FILE)

if zones.empty:
    raise ValueError("zones.geojson is empty.")

if zones.crs is None:
    raise ValueError("zones.geojson has no CRS.")

zones = zones.to_crs("EPSG:4326")

print(f"\nLoaded {len(zones)} zones.")

sensor_types = [
    "Environmental",
    "Ground Movement",
    "Gas Monitoring",
    "Pressure Monitoring",
    "Vibration Monitoring",
    "Weather Monitoring",
    "Structural Monitoring",
    "Multi-Parameter",
    "Multi-Parameter"
]

sensors = []

for index, zone in zones.iterrows():

    zone_id = zone["zone_id"]

    geometry = zone.geometry

    if geometry is None or geometry.is_empty:
        print(f"Skipping {zone_id}: invalid geometry.")
        continue

    centroid = geometry.centroid

    sensor_id = f"SENSOR-{len(sensors) + 1:03d}"

    sensor_type = sensor_types[
        len(sensors) % len(sensor_types)
    ]

    sensor = {
        "mine_id": MINE_ID,
        "zone_id": zone_id,
        "sensor_id": sensor_id,
        "sensor_type": sensor_type,
        "status": "PROTOTYPE",
        "data_source": "GIS_PROTOTYPE",
        "latitude": round(centroid.y, 6),
        "longitude": round(centroid.x, 6),
        "supports_displacement": True,
        "supports_strain": True,
        "supports_pore_pressure": True,
        "supports_rainfall": True,
        "supports_temperature": True,
        "supports_vibration": True,
        "last_reading": None,
        "risk_level": "UNKNOWN",
        "risk_probability": None,
        "geometry": Point(centroid.x, centroid.y)
    }

    sensors.append(sensor)

sensors_gdf = gpd.GeoDataFrame(
    sensors,
    geometry="geometry",
    crs="EPSG:4326"
)

sensors_gdf = sensors_gdf[
    [
        "mine_id",
        "zone_id",
        "sensor_id",
        "sensor_type",
        "status",
        "data_source",
        "latitude",
        "longitude",
        "supports_displacement",
        "supports_strain",
        "supports_pore_pressure",
        "supports_rainfall",
        "supports_temperature",
        "supports_vibration",
        "last_reading",
        "risk_level",
        "risk_probability",
        "geometry"
    ]
]

sensors_gdf.to_file(
    OUTPUT_FILE,
    driver="GeoJSON"
)

print("\n==========================================")
print("SENSOR GENERATION COMPLETED")
print("==========================================")

print(f"Mine ID       : {MINE_ID}")
print(f"Sensors       : {len(sensors_gdf)}")
print(f"Output file   : {OUTPUT_FILE}")

print("\nGenerated sensors:")

for _, sensor in sensors_gdf.iterrows():
    print(
        f"{sensor['sensor_id']} | "
        f"{sensor['zone_id']} | "
        f"{sensor['sensor_type']}"
    )

print("\nIMPORTANT:")
print("These are prototype sensor locations.")
print("They will later be replaced/updated by real IoT hardware.")