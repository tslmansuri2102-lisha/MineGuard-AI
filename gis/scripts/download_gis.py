from pathlib import Path
import osmnx as ox

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_GIS_DIR = BASE_DIR / "data" / "raw" / "gis"
RAW_GIS_DIR.mkdir(parents=True, exist_ok=True)

# Small Kusunda/Jharia study area
# (west, south, east, north)
BBOX = (
    86.3670,
    23.7950,
    86.3870,
    23.8120
)

print("Downloading Kusunda road network...")

ox.settings.requests_timeout = 180
ox.settings.overpass_timeout = 180

roads = ox.graph.graph_from_bbox(
    bbox=BBOX,
    network_type="drive",
    simplify=True
)

edges = ox.convert.graph_to_gdfs(
    roads,
    nodes=False,
    edges=True
)

edges.to_file(
    RAW_GIS_DIR / "roads.geojson",
    driver="GeoJSON"
)

print("\nSUCCESS!")
print(f"Road features: {len(edges)}")
print(f"Saved to: {RAW_GIS_DIR / 'roads.geojson'}")