from pathlib import Path
import json
import html

import folium
import geopandas as gpd
from branca.element import Element


BASE_DIR = Path(__file__).resolve().parents[1]

ZONE_FILE = BASE_DIR / "data" / "processed" / "gis" / "zones.geojson"
ROAD_FILE = BASE_DIR / "data" / "raw" / "gis" / "roads.geojson"
ZONE_DATA_FILE = BASE_DIR / "data" / "processed" / "gis" / "zone_api_data.json"
SENSOR_FILE = BASE_DIR / "data" / "processed" / "gis" / "sensors.geojson"

ELEVATION_IMAGE = (
    BASE_DIR
    / "data"
    / "processed"
    / "gis"
    / "map_layers"
    / "elevation.png"
)

SLOPE_IMAGE = (
    BASE_DIR
    / "data"
    / "processed"
    / "gis"
    / "map_layers"
    / "slope.png"
)

OUTPUT_FILE = BASE_DIR / "mine_map.html"

KUSUNDA = [23.7822, 86.3933]


print("==========================================")
print("MineGuard AI - Advanced GIS Dashboard")
print("==========================================")


required_files = [
    ZONE_FILE,
    ROAD_FILE,
    ZONE_DATA_FILE,
    ELEVATION_IMAGE,
    SLOPE_IMAGE
]


for file_path in required_files:
    if not file_path.exists():
        raise FileNotFoundError(
            f"Required file not found:\n{file_path}"
        )


with open(
    ZONE_DATA_FILE,
    "r",
    encoding="utf-8"
) as file:
    zone_api_data = json.load(file)


zone_data = {
    str(item["zone_id"]): item
    for item in zone_api_data
}


zones = gpd.read_file(
    ZONE_FILE
).to_crs("EPSG:4326")


roads = gpd.read_file(
    ROAD_FILE
).to_crs("EPSG:4326")


mine_map = folium.Map(
    location=KUSUNDA,
    zoom_start=15,
    tiles="OpenStreetMap",
    control_scale=True,
    prefer_canvas=True
)


elevation_layer = folium.FeatureGroup(
    name="Elevation / DEM",
    show=False
)


folium.raster_layers.ImageOverlay(
    image=str(ELEVATION_IMAGE),
    bounds=[
        [23.77875, 86.38986111111112],
        [23.785138888888888, 86.39819444444446]
    ],
    opacity=0.42,
    interactive=True,
    cross_origin=False,
    zindex=1
).add_to(elevation_layer)


elevation_layer.add_to(mine_map)


slope_layer = folium.FeatureGroup(
    name="Slope Analysis",
    show=False
)


folium.raster_layers.ImageOverlay(
    image=str(SLOPE_IMAGE),
    bounds=[
        [23.77877868536618, 86.3898312967052],
        [23.78517143564985, 86.39816966664041]
    ],
    opacity=0.42,
    interactive=True,
    cross_origin=False,
    zindex=2
).add_to(slope_layer)


slope_layer.add_to(mine_map)


study_area = [
    [23.7870, 86.3870],
    [23.7870, 86.4010],
    [23.7790, 86.4020],
    [23.7770, 86.3890]
]


study_layer = folium.FeatureGroup(
    name="Kusunda Study Area",
    show=True
)


folium.Polygon(
    locations=study_area,
    color="#64748b",
    weight=2,
    opacity=0.8,
    fill=False,
    dash_array="7 7",
    popup="Kusunda Mine Study Area"
).add_to(study_layer)


study_layer.add_to(mine_map)


road_layer = folium.FeatureGroup(
    name="Road Network",
    show=True
)


road_options = {
    "style_function": lambda feature: {
        "color": "#64748b",
        "weight": 1.8,
        "opacity": 0.65
    }
}


if "highway" in roads.columns:
    road_options["tooltip"] = folium.GeoJsonTooltip(
        fields=["highway"],
        aliases=["Road Type:"],
        localize=True
    )


folium.GeoJson(
    roads.to_json(),
    **road_options
).add_to(road_layer)


road_layer.add_to(mine_map)


def risk_color(level):

    level = str(level).upper()

    if level == "HIGH":
        return "#ff4d67"

    if level == "MODERATE":
        return "#f5b942"

    if level == "LOW":
        return "#22c7a5"

    return "#94a3b8"


zone_features = []


for _, zone in zones.iterrows():

    zone_id = str(
        zone.get(
            "zone_id",
            ""
        )
    )

    record = zone_data.get(
        zone_id,
        {}
    )

    gis = record.get(
        "gis",
        {}
    )

    realtime = record.get(
        "realtime",
        {}
    )

    risk = record.get(
        "risk",
        {}
    )

    explanation = risk.get(
        "explanation",
        {}
    )

    properties = {
        "zone_id": zone_id,

        "mine_id": record.get(
            "mine_id",
            "MINE-001"
        ),

        "area": gis.get(
            "area_sq_km"
        ),

        "elevation": gis.get(
            "mean_elevation_m"
        ),

        "min_elevation": gis.get(
            "min_elevation_m"
        ),

        "max_elevation": gis.get(
            "max_elevation_m"
        ),

        "slope": gis.get(
            "mean_slope_deg"
        ),

        "max_slope": gis.get(
            "max_slope_deg"
        ),

        "aspect": gis.get(
            "mean_aspect_deg"
        ),

        "curvature": gis.get(
            "mean_curvature"
        ),

        "roughness": gis.get(
            "mean_roughness"
        ),

        "max_roughness": gis.get(
            "max_roughness"
        ),

        "road_count": gis.get(
            "road_count"
        ),

        "road_length": gis.get(
            "road_length_km"
        ),

        "slope_indicator": gis.get(
            "slope_indicator"
        ),

        "roughness_indicator": gis.get(
            "roughness_indicator"
        ),

        "terrain_variability": gis.get(
            "terrain_variability_indicator"
        ),

        "gis_indicator": gis.get(
            "gis_terrain_indicator"
        ),

        "terrain_condition": gis.get(
            "gis_terrain_condition",
            "UNKNOWN"
        ),

        "displacement": realtime.get(
            "displacement_mm"
        ),

        "strain": realtime.get(
            "strain"
        ),

        "pressure": realtime.get(
            "pore_pressure_kpa"
        ),

        "rainfall": realtime.get(
            "rainfall_mm"
        ),

        "temperature": realtime.get(
            "temperature_c"
        ),

        "vibration": realtime.get(
            "vibration_g"
        ),

        "risk_level": risk.get(
            "level",
            "UNKNOWN"
        ),

        "risk_probability": risk.get(
            "probability"
        ),

        "risk_factors": explanation.get(
            "primary_factors",
            []
        ),

        "risk_recommendation": explanation.get(
            "recommendation",
            "Continue monitoring."
        )
    }

    zone_features.append(
        {
            "type": "Feature",
            "geometry": zone.geometry.__geo_interface__,
            "properties": properties
        }
    )


zone_layer = folium.FeatureGroup(
    name="AI Risk Intelligence",
    show=True
)


def zone_style(feature):

    level = feature[
        "properties"
    ].get(
        "risk_level",
        "UNKNOWN"
    )

    color = risk_color(level)

    return {
        "color": color,
        "weight": 2,
        "opacity": 0.9,
        "fillColor": color,
        "fillOpacity": 0.07
    }


def zone_highlight(feature):

    level = feature[
        "properties"
    ].get(
        "risk_level",
        "UNKNOWN"
    )

    color = risk_color(level)

    return {
        "color": color,
        "weight": 4,
        "opacity": 1,
        "fillColor": color,
        "fillOpacity": 0.16
    }


zone_geojson = folium.GeoJson(
    {
        "type": "FeatureCollection",
        "features": zone_features
    },
    style_function=zone_style,
    highlight_function=zone_highlight,
    tooltip=folium.GeoJsonTooltip(
        fields=[
            "zone_id",
            "risk_level"
        ],
        aliases=[
            "ZONE",
            "AI RISK"
        ],
        sticky=True
    )
)


zone_geojson.add_to(zone_layer)


zone_layer.add_to(mine_map)


sensor_layer = folium.FeatureGroup(
    name="Sensor Locations",
    show=True
)


if SENSOR_FILE.exists():

    sensors = gpd.read_file(
        SENSOR_FILE
    ).to_crs("EPSG:4326")

    for _, sensor in sensors.iterrows():

        props = sensor.to_dict()

        sensor_id = props.get(
            "sensor_id",
            props.get(
                "id",
                "SENSOR"
            )
        )

        sensor_type = props.get(
            "type",
            "Environmental"
        )

        popup = f"""
        <div style="
            font-family:Inter,Arial,sans-serif;
            width:220px;
            color:#e2e8f0;
            background:#0f172a;
            padding:8px;
        ">
            <div style="
                font-size:15px;
                font-weight:700;
                margin-bottom:8px;
            ">
                MineGuard Sensor
            </div>

            <b>Sensor ID:</b>
            {html.escape(str(sensor_id))}
            <br><br>

            <b>Type:</b>
            {html.escape(str(sensor_type))}
            <br><br>

            <b>Status:</b>
            <span style="color:#22c7a5">
                Ready
            </span>
        </div>
        """

        folium.CircleMarker(
            location=[
                sensor.geometry.y,
                sensor.geometry.x
            ],
            radius=5,
            color="#67e8f9",
            fill=True,
            fill_color="#22d3ee",
            fill_opacity=0.9,
            weight=2,
            tooltip=str(sensor_id),
            popup=folium.Popup(
                popup,
                max_width=280
            )
        ).add_to(sensor_layer)

else:

    prototype_sensors = [
        {
            "id": "SENSOR-001",
            "lat": 23.7845,
            "lon": 86.3905,
            "type": "Environmental"
        },
        {
            "id": "SENSOR-002",
            "lat": 23.7830,
            "lon": 86.3960,
            "type": "Ground Movement"
        },
        {
            "id": "SENSOR-003",
            "lat": 23.7795,
            "lon": 86.3935,
            "type": "Gas Monitoring"
        },
        {
            "id": "SENSOR-004",
            "lat": 23.7850,
            "lon": 86.3990,
            "type": "Environmental"
        }
    ]

    for sensor in prototype_sensors:

        popup = f"""
        <div style="
            font-family:Inter,Arial,sans-serif;
            width:220px;
            color:#e2e8f0;
            background:#0f172a;
            padding:8px;
        ">

            <div style="
                font-size:15px;
                font-weight:700;
                margin-bottom:8px;
            ">
                MineGuard Sensor
            </div>

            <b>Sensor ID:</b>
            {sensor["id"]}

            <br><br>

            <b>Type:</b>
            {sensor["type"]}

            <br><br>

            <b>Status:</b>
            <span style="color:#f5b942">
                Prototype
            </span>

        </div>
        """

        folium.CircleMarker(
            location=[
                sensor["lat"],
                sensor["lon"]
            ],
            radius=5,
            color="#67e8f9",
            fill=True,
            fill_color="#22d3ee",
            fill_opacity=0.9,
            weight=2,
            tooltip=sensor["id"],
            popup=folium.Popup(
                popup,
                max_width=280
            )
        ).add_to(sensor_layer)


sensor_layer.add_to(mine_map)


gas_layer = folium.FeatureGroup(
    name="Gas Monitoring",
    show=False
)


folium.Polygon(
    locations=[
        [23.7815, 86.3910],
        [23.7815, 86.3955],
        [23.7780, 86.3965],
        [23.7775, 86.3920]
    ],
    color="#a78bfa",
    weight=2,
    fill=True,
    fill_color="#8b5cf6",
    fill_opacity=0.08,
    dash_array="5 5",
    popup="Gas Monitoring Area"
).add_to(gas_layer)


gas_layer.add_to(mine_map)


thermal_layer = folium.FeatureGroup(
    name="Thermal Monitoring",
    show=False
)


folium.Polygon(
    locations=[
        [23.7840, 86.3970],
        [23.7855, 86.4000],
        [23.7815, 86.4010],
        [23.7805, 86.3980]
    ],
    color="#fb7185",
    weight=2,
    fill=True,
    fill_color="#fb7185",
    fill_opacity=0.07,
    dash_array="5 5",
    popup="Thermal / Fire Monitoring Area"
).add_to(thermal_layer)


thermal_layer.add_to(mine_map)


restricted_layer = folium.FeatureGroup(
    name="Restricted Area",
    show=False
)


folium.Polygon(
    locations=[
        [23.7790, 86.3970],
        [23.7810, 86.4005],
        [23.7780, 86.4020],
        [23.7765, 86.3990]
    ],
    color="#94a3b8",
    weight=2,
    fill=True,
    fill_color="#64748b",
    fill_opacity=0.08,
    dash_array="4 5",
    popup="Restricted Area"
).add_to(restricted_layer)


restricted_layer.add_to(mine_map)


css = """
<style>

@import url(
'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap'
);

* {
    box-sizing: border-box;
}

body {
    font-family: Inter, Arial, sans-serif;
}

#mineguard-header {
    position: fixed;
    top: 18px;
    left: 60px;
    z-index: 9998;
    min-width: 310px;
    padding: 15px 20px;
    border: 1px solid rgba(148,163,184,.25);
    border-radius: 16px;
    background: rgba(15,23,42,.94);
    backdrop-filter: blur(14px);
    box-shadow:
        0 12px 35px rgba(0,0,0,.30);
    color: #f8fafc;
}

#mineguard-header .title {
    display: flex;
    align-items: center;
    gap: 9px;
    font-size: 20px;
    font-weight: 800;
    letter-spacing: -.4px;
}

#mineguard-header .subtitle {
    margin-top: 5px;
    color: #94a3b8;
    font-size: 10px;
    letter-spacing: .5px;
}

.brand-mark {
    width: 28px;
    height: 28px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 8px;
    background: linear-gradient(
        135deg,
        #22c7a5,
        #0891b2
    );
    color: #082f49;
    font-size: 15px;
}

#mineguard-status {
    position: fixed;
    top: 18px;
    right: 65px;
    z-index: 9998;
    display: flex;
    align-items: center;
    gap: 7px;
    padding: 9px 14px;
    border: 1px solid rgba(148,163,184,.25);
    border-radius: 999px;
    background: rgba(15,23,42,.92);
    backdrop-filter: blur(12px);
    box-shadow: 0 8px 25px rgba(0,0,0,.20);
    color: #cbd5e1;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: .7px;
}

.status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #22c7a5;
    box-shadow: 0 0 10px rgba(34,199,165,.8);
}

#zone-dashboard {
    position: fixed;
    top: 78px;
    right: 18px;
    z-index: 10000;
    width: 390px;
    max-height: calc(100vh - 96px);
    overflow-y: auto;
    display: none;
    border: 1px solid rgba(148,163,184,.20);
    border-radius: 20px;
    background: rgba(10,18,32,.96);
    backdrop-filter: blur(20px);
    box-shadow:
        0 25px 70px rgba(0,0,0,.42);
    color: #e2e8f0;
    animation: panelIn .25s ease-out;
}

@keyframes panelIn {
    from {
        opacity: 0;
        transform: translateX(20px);
    }

    to {
        opacity: 1;
        transform: translateX(0);
    }
}

#zone-dashboard::-webkit-scrollbar {
    width: 5px;
}

#zone-dashboard::-webkit-scrollbar-thumb {
    background: #334155;
    border-radius: 10px;
}

.dashboard-header {
    position: relative;
    padding: 20px;
    border-bottom: 1px solid rgba(148,163,184,.14);
    background:
        linear-gradient(
            135deg,
            rgba(30,41,59,.95),
            rgba(15,23,42,.96)
        );
}

.dashboard-header .eyebrow {
    margin-bottom: 5px;
    color: #22c7a5;
    font-size: 9px;
    font-weight: 800;
    letter-spacing: 1.6px;
}

.dashboard-header .zone {
    color: #f8fafc;
    font-size: 24px;
    font-weight: 800;
}

.dashboard-header .mine {
    margin-top: 5px;
    color: #94a3b8;
    font-size: 11px;
}

.close-dashboard {
    position: absolute;
    top: 15px;
    right: 17px;
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px solid rgba(148,163,184,.20);
    border-radius: 9px;
    background: rgba(255,255,255,.05);
    color: #94a3b8;
    cursor: pointer;
    font-size: 20px;
    transition: .2s;
}

.close-dashboard:hover {
    background: rgba(255,255,255,.10);
    color: white;
}

.dashboard-body {
    padding: 16px;
}

.section {
    margin-bottom: 18px;
}

.section-title {
    margin-bottom: 9px;
    color: #64748b;
    font-size: 9px;
    font-weight: 800;
    letter-spacing: 1.5px;
}

.risk-panel {
    padding: 15px;
    border: 1px solid rgba(148,163,184,.15);
    border-radius: 14px;
    background: rgba(30,41,59,.55);
}

.risk-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.risk-status-label {
    color: #64748b;
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 1px;
}

.risk-level {
    margin-top: 4px;
    font-size: 25px;
    font-weight: 800;
}

.risk-percent {
    color: #f8fafc;
    font-size: 24px;
    font-weight: 800;
}

.risk-percent-label {
    margin-top: 2px;
    color: #64748b;
    font-size: 8px;
    text-align: right;
}

.risk-track {
    height: 6px;
    margin-top: 14px;
    overflow: hidden;
    border-radius: 20px;
    background: #1e293b;
}

.risk-bar {
    height: 100%;
    width: 0%;
    border-radius: 20px;
    transition: width .5s ease;
}

.metrics {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 7px;
}

.metric {
    padding: 11px;
    border: 1px solid rgba(148,163,184,.12);
    border-radius: 11px;
    background: rgba(30,41,59,.42);
}

.metric-label {
    color: #64748b;
    font-size: 8px;
    font-weight: 700;
    letter-spacing: .7px;
    text-transform: uppercase;
}

.metric-value {
    margin-top: 5px;
    color: #f1f5f9;
    font-size: 14px;
    font-weight: 700;
}

.indicator-card {
    margin-bottom: 8px;
    padding: 10px 11px;
    border: 1px solid rgba(148,163,184,.12);
    border-radius: 11px;
    background: rgba(30,41,59,.42);
}

.indicator-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.indicator-name {
    color: #94a3b8;
    font-size: 10px;
}

.indicator-value {
    color: #f8fafc;
    font-size: 10px;
    font-weight: 700;
}

.indicator-track {
    height: 4px;
    margin-top: 7px;
    overflow: hidden;
    border-radius: 10px;
    background: #1e293b;
}

.indicator-bar {
    height: 100%;
    border-radius: 10px;
    background: #22c7a5;
}

.sensor-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 7px;
}

.sensor {
    padding: 10px;
    border: 1px solid rgba(103,232,249,.10);
    border-radius: 10px;
    background: rgba(8,47,73,.25);
    color: #64748b;
    font-size: 9px;
}

.sensor-value {
    margin-top: 4px;
    color: #67e8f9;
    font-size: 12px;
    font-weight: 700;
}

.sensor-status {
    margin-bottom: 9px;
    padding: 9px 10px;
    border: 1px solid rgba(245,185,66,.15);
    border-radius: 9px;
    background: rgba(245,185,66,.06);
    color: #f5b942;
    font-size: 9px;
}

.explanation-box {
    padding: 12px;
    border: 1px solid rgba(148,163,184,.12);
    border-radius: 12px;
    background: rgba(30,41,59,.42);
}

.explanation-list {
    margin: 0;
    padding-left: 17px;
    color: #cbd5e1;
    font-size: 10px;
    line-height: 1.9;
}

.recommendation {
    margin-top: 12px;
    padding: 11px;
    border-left: 3px solid #22c7a5;
    border-radius: 8px;
    background: rgba(34,199,165,.06);
    color: #cbd5e1;
    font-size: 10px;
    line-height: 1.55;
}

.recommendation-title {
    margin-bottom: 5px;
    color: #22c7a5;
    font-size: 8px;
    font-weight: 800;
    letter-spacing: 1px;
}

#mineguard-search {
    position: fixed;
    bottom: 22px;
    left: 24px;
    z-index: 9998;
    display: flex;
    align-items: center;
    gap: 7px;
    padding: 10px 13px;
    border: 1px solid rgba(148,163,184,.22);
    border-radius: 12px;
    background: rgba(15,23,42,.94);
    backdrop-filter: blur(12px);
    box-shadow: 0 10px 30px rgba(0,0,0,.25);
}

.search-icon {
    color: #22c7a5;
}

#mineguard-search input {
    width: 180px;
    border: none;
    outline: none;
    background: transparent;
    color: #f8fafc;
    font-family: Inter, Arial, sans-serif;
    font-size: 11px;
}

#mineguard-search input::placeholder {
    color: #64748b;
}

#mineguard-legend {
    position: fixed;
    right: 18px;
    bottom: 22px;
    z-index: 9998;
    min-width: 170px;
    padding: 13px;
    border: 1px solid rgba(148,163,184,.20);
    border-radius: 13px;
    background: rgba(15,23,42,.94);
    backdrop-filter: blur(12px);
    box-shadow: 0 10px 30px rgba(0,0,0,.25);
    color: #cbd5e1;
    font-family: Inter, Arial, sans-serif;
    font-size: 9px;
}

.legend-title {
    margin-bottom: 9px;
    color: #f8fafc;
    font-size: 9px;
    font-weight: 800;
    letter-spacing: 1px;
}

.legend-item {
    display: flex;
    align-items: center;
    margin: 7px 0;
}

.legend-line {
    width: 18px;
    height: 3px;
    margin-right: 8px;
    border-radius: 10px;
}

.leaflet-control-layers {
    border: 1px solid rgba(148,163,184,.25) !important;
    border-radius: 12px !important;
    background: rgba(15,23,42,.94) !important;
    color: #cbd5e1 !important;
    box-shadow: 0 8px 25px rgba(0,0,0,.25) !important;
}

.leaflet-control-layers label {
    color: #cbd5e1 !important;
    font-family: Inter, Arial, sans-serif;
    font-size: 11px;
}

.leaflet-control-zoom a {
    background: rgba(15,23,42,.94) !important;
    color: #cbd5e1 !important;
    border-color: #334155 !important;
}

.leaflet-control-attribution {
    background: rgba(15,23,42,.75) !important;
    color: #94a3b8 !important;
}

.leaflet-control-attribution a {
    color: #67e8f9 !important;
}

@media(max-width: 900px) {

    #zone-dashboard {
        width: calc(100vw - 20px);
        right: 10px;
        top: 70px;
        max-height: calc(100vh - 80px);
    }

    #mineguard-header {
        left: 55px;
        min-width: 220px;
    }

    #mineguard-status {
        display: none;
    }

    #mineguard-legend {
        display: none;
    }

    #mineguard-search {
        bottom: 15px;
        left: 15px;
    }

}

</style>
"""


mine_map.get_root().html.add_child(
    Element(css)
)


header = """
<div id="mineguard-header">

    <div class="title">

        <span class="brand-mark">
            ⛏
        </span>

        <span>
            MineGuard AI
        </span>

    </div>

    <div class="subtitle">
        INTELLIGENT MINE SAFETY & TERRAIN INTELLIGENCE
    </div>

</div>

<div id="mineguard-status">

    <span class="status-dot"></span>

    GIS SYSTEM ONLINE

</div>
"""


mine_map.get_root().html.add_child(
    Element(header)
)


dashboard = """
<div id="zone-dashboard">

    <div class="dashboard-header">

        <span
            class="close-dashboard"
            onclick="closeZoneDashboard()"
        >
            ×
        </span>

        <div class="eyebrow">
            MINE SAFETY INTELLIGENCE
        </div>

        <div
            id="dashboard-zone"
            class="zone"
        >
            ZONE-001
        </div>

        <div
            id="dashboard-mine"
            class="mine"
        >
            MINE-001
        </div>

    </div>


    <div class="dashboard-body">


        <div class="section">

            <div class="section-title">
                AI RISK ASSESSMENT
            </div>

            <div class="risk-panel">

                <div class="risk-top">

                    <div>

                        <div class="risk-status-label">
                            CURRENT RISK
                        </div>

                        <div
                            id="risk-level"
                            class="risk-level"
                        >
                            UNKNOWN
                        </div>

                    </div>


                    <div>

                        <div
                            id="risk-percent"
                            class="risk-percent"
                        >
                            —
                        </div>

                        <div class="risk-percent-label">
                            MODEL PROBABILITY
                        </div>

                    </div>

                </div>


                <div class="risk-track">

                    <div
                        id="risk-bar"
                        class="risk-bar"
                    ></div>

                </div>

            </div>

        </div>


        <div class="section">

            <div class="section-title">
                TERRAIN PROFILE
            </div>

            <div class="metrics">

                <div class="metric">

                    <div class="metric-label">
                        Elevation
                    </div>

                    <div
                        id="elevation"
                        class="metric-value"
                    >
                        —
                    </div>

                </div>


                <div class="metric">

                    <div class="metric-label">
                        Mean Slope
                    </div>

                    <div
                        id="slope"
                        class="metric-value"
                    >
                        —
                    </div>

                </div>


                <div class="metric">

                    <div class="metric-label">
                        Max Slope
                    </div>

                    <div
                        id="max-slope"
                        class="metric-value"
                    >
                        —
                    </div>

                </div>


                <div class="metric">

                    <div class="metric-label">
                        Roughness
                    </div>

                    <div
                        id="roughness"
                        class="metric-value"
                    >
                        —
                    </div>

                </div>


                <div class="metric">

                    <div class="metric-label">
                        Aspect
                    </div>

                    <div
                        id="aspect"
                        class="metric-value"
                    >
                        —
                    </div>

                </div>


                <div class="metric">

                    <div class="metric-label">
                        Curvature
                    </div>

                    <div
                        id="curvature"
                        class="metric-value"
                    >
                        —
                    </div>

                </div>


                <div class="metric">

                    <div class="metric-label">
                        Roads
                    </div>

                    <div
                        id="roads"
                        class="metric-value"
                    >
                        —
                    </div>

                </div>


                <div class="metric">

                    <div class="metric-label">
                        Road Length
                    </div>

                    <div
                        id="road-length"
                        class="metric-value"
                    >
                        —
                    </div>

                </div>

            </div>

        </div>


        <div class="section">

            <div class="section-title">
                GIS TERRAIN SIGNALS
            </div>


            <div class="indicator-card">

                <div class="indicator-row">

                    <span class="indicator-name">
                        Slope Indicator
                    </span>

                    <span
                        id="slope-indicator"
                        class="indicator-value"
                    >
                        —
                    </span>

                </div>

                <div class="indicator-track">

                    <div
                        id="slope-indicator-bar"
                        class="indicator-bar"
                    ></div>

                </div>

            </div>


            <div class="indicator-card">

                <div class="indicator-row">

                    <span class="indicator-name">
                        Roughness Indicator
                    </span>

                    <span
                        id="roughness-indicator"
                        class="indicator-value"
                    >
                        —
                    </span>

                </div>

                <div class="indicator-track">

                    <div
                        id="roughness-indicator-bar"
                        class="indicator-bar"
                    ></div>

                </div>

            </div>


            <div class="indicator-card">

                <div class="indicator-row">

                    <span class="indicator-name">
                        Terrain Variability
                    </span>

                    <span
                        id="terrain-variability"
                        class="indicator-value"
                    >
                        —
                    </span>

                </div>

                <div class="indicator-track">

                    <div
                        id="terrain-variability-bar"
                        class="indicator-bar"
                    ></div>

                </div>

            </div>


            <div class="indicator-card">

                <div class="indicator-row">

                    <span class="indicator-name">
                        Combined GIS Indicator
                    </span>

                    <span
                        id="gis-indicator"
                        class="indicator-value"
                    >
                        —
                    </span>

                </div>

                <div class="indicator-track">

                    <div
                        id="gis-indicator-bar"
                        class="indicator-bar"
                    ></div>

                </div>

            </div>

        </div>


        <div class="section">

            <div class="section-title">
                WHY THIS ZONE IS AT RISK
            </div>

            <div class="explanation-box">

                <ul
                    id="risk-factors"
                    class="explanation-list"
                >
                    <li>
                        Waiting for risk analysis
                    </li>
                </ul>


                <div class="recommendation">

                    <div class="recommendation-title">
                        RECOMMENDED ACTION
                    </div>

                    <div id="risk-recommendation">
                        Continue monitoring.
                    </div>

                </div>

            </div>

        </div>


        <div class="section">

            <div class="section-title">
                LIVE SENSOR TELEMETRY
            </div>

            <div class="sensor-status">
                ⏳ IoT telemetry awaiting sensor integration
            </div>


            <div class="sensor-grid">

                <div class="sensor">

                    Displacement

                    <div
                        id="displacement"
                        class="sensor-value"
                    >
                        Waiting
                    </div>

                </div>


                <div class="sensor">

                    Strain

                    <div
                        id="strain"
                        class="sensor-value"
                    >
                        Waiting
                    </div>

                </div>


                <div class="sensor">

                    Pore Pressure

                    <div
                        id="pressure"
                        class="sensor-value"
                    >
                        Waiting
                    </div>

                </div>


                <div class="sensor">

                    Rainfall

                    <div
                        id="rainfall"
                        class="sensor-value"
                    >
                        Waiting
                    </div>

                </div>


                <div class="sensor">

                    Temperature

                    <div
                        id="temperature"
                        class="sensor-value"
                    >
                        Waiting
                    </div>

                </div>


                <div class="sensor">

                    Vibration

                    <div
                        id="vibration"
                        class="sensor-value"
                    >
                        Waiting
                    </div>

                </div>

            </div>

        </div>


    </div>

</div>
"""


mine_map.get_root().html.add_child(
    Element(dashboard)
)


search_box = """
<div id="mineguard-search">

    <span class="search-icon">
        ⌕
    </span>

    <input
        id="zone-search"
        type="text"
        placeholder="Search zone e.g. ZONE-007"
    >

</div>
"""


mine_map.get_root().html.add_child(
    Element(search_box)
)


legend = """
<div id="mineguard-legend">

    <div class="legend-title">
        AI RISK INTELLIGENCE
    </div>

    <div class="legend-item">

        <span
            class="legend-line"
            style="background:#ff4d67"
        ></span>

        High Risk

    </div>


    <div class="legend-item">

        <span
            class="legend-line"
            style="background:#f5b942"
        ></span>

        Moderate Risk

    </div>


    <div class="legend-item">

        <span
            class="legend-line"
            style="background:#22c7a5"
        ></span>

        Low Risk

    </div>

</div>
"""


mine_map.get_root().html.add_child(
    Element(legend)
)


map_name = mine_map.get_name()
zone_geojson_name = zone_geojson.get_name()


javascript = """
<script>

window.addEventListener(
    "load",
    function() {

        setTimeout(
            function() {

                const mapInstance =
                    __MAP_NAME__;

                const zoneLayer =
                    __ZONE_GEOJSON__;


                function formatValue(
                    value,
                    suffix
                ) {

                    if (
                        value === null ||
                        value === undefined ||
                        value === ""
                    ) {
                        return "—";
                    }

                    if (
                        typeof value === "number"
                    ) {

                        return value.toFixed(3)
                            + (suffix || "");

                    }

                    return value
                        + (suffix || "");
                }


                function setElement(
                    id,
                    value
                ) {

                    const element =
                        document.getElementById(id);

                    if (element) {
                        element.textContent = value;
                    }
                }


                function setBar(
                    id,
                    value
                ) {

                    const element =
                        document.getElementById(id);

                    if (!element) {
                        return;
                    }

                    let numeric =
                        Number(value);

                    if (
                        !Number.isFinite(numeric)
                    ) {
                        numeric = 0;
                    }

                    numeric =
                        Math.max(
                            0,
                            Math.min(
                                1,
                                numeric
                            )
                        );

                    element.style.width =
                        (
                            numeric * 100
                        ) + "%";
                }


                function riskColor(
                    level
                ) {

                    level =
                        String(level)
                            .toUpperCase();

                    if (
                        level === "HIGH"
                    ) {
                        return "#ff4d67";
                    }

                    if (
                        level === "MODERATE"
                    ) {
                        return "#f5b942";
                    }

                    if (
                        level === "LOW"
                    ) {
                        return "#22c7a5";
                    }

                    return "#94a3b8";
                }


                function showZoneDashboard(
                    properties
                ) {

                    const dashboard =
                        document.getElementById(
                            "zone-dashboard"
                        );

                    if (!dashboard) {
                        return;
                    }


                    dashboard.style.display =
                        "block";


                    setElement(
                        "dashboard-zone",
                        properties.zone_id ||
                        "UNKNOWN"
                    );


                    setElement(
                        "dashboard-mine",
                        properties.mine_id ||
                        "MINE-001"
                    );


                    const riskLevel =
                        properties.risk_level ||
                        "UNKNOWN";


                    const riskColorValue =
                        riskColor(
                            riskLevel
                        );


                    setElement(
                        "risk-level",
                        riskLevel
                    );


                    const riskLevelElement =
                        document.getElementById(
                            "risk-level"
                        );


                    if (riskLevelElement) {

                        riskLevelElement.style.color =
                            riskColorValue;
                    }


                    let probability =
                        Number(
                            properties.risk_probability
                        );


                    if (
                        Number.isFinite(
                            probability
                        )
                    ) {

                        if (
                            probability <= 1
                        ) {

                            probability *= 100;
                        }

                        probability =
                            Math.max(
                                0,
                                Math.min(
                                    100,
                                    probability
                                )
                            );


                        setElement(
                            "risk-percent",
                            probability.toFixed(2) + "%"
                        );


                        const riskBar =
                            document.getElementById(
                                "risk-bar"
                            );


                        if (riskBar) {

                            riskBar.style.width =
                                probability + "%";

                            riskBar.style.background =
                                riskColorValue;

                            riskBar.style.boxShadow =
                                "0 0 12px " +
                                riskColorValue;
                        }

                    } else {

                        setElement(
                            "risk-percent",
                            "—"
                        );

                        setBar(
                            "risk-bar",
                            0
                        );
                    }


                    setElement(
                        "elevation",
                        formatValue(
                            properties.elevation,
                            " m"
                        )
                    );


                    setElement(
                        "slope",
                        formatValue(
                            properties.slope,
                            "°"
                        )
                    );


                    setElement(
                        "max-slope",
                        formatValue(
                            properties.max_slope,
                            "°"
                        )
                    );


                    setElement(
                        "roughness",
                        formatValue(
                            properties.roughness,
                            " m"
                        )
                    );


                    setElement(
                        "aspect",
                        formatValue(
                            properties.aspect,
                            "°"
                        )
                    );


                    setElement(
                        "curvature",
                        formatValue(
                            properties.curvature
                        )
                    );


                    setElement(
                        "roads",
                        formatValue(
                            properties.road_count
                        )
                    );


                    setElement(
                        "road-length",
                        formatValue(
                            properties.road_length,
                            " km"
                        )
                    );


                    setElement(
                        "slope-indicator",
                        formatValue(
                            properties.slope_indicator
                        )
                    );


                    setElement(
                        "roughness-indicator",
                        formatValue(
                            properties.roughness_indicator
                        )
                    );


                    setElement(
                        "terrain-variability",
                        formatValue(
                            properties.terrain_variability
                        )
                    );


                    setElement(
                        "gis-indicator",
                        formatValue(
                            properties.gis_indicator
                        )
                    );


                    setBar(
                        "slope-indicator-bar",
                        properties.slope_indicator
                    );


                    setBar(
                        "roughness-indicator-bar",
                        properties.roughness_indicator
                    );


                    setBar(
                        "terrain-variability-bar",
                        properties.terrain_variability
                    );


                    setBar(
                        "gis-indicator-bar",
                        properties.gis_indicator
                    );


                    setElement(
                        "displacement",
                        properties.displacement !== null &&
                        properties.displacement !== undefined
                            ? formatValue(
                                properties.displacement,
                                " mm"
                            )
                            : "Waiting"
                    );


                    setElement(
                        "strain",
                        properties.strain !== null &&
                        properties.strain !== undefined
                            ? formatValue(
                                properties.strain
                            )
                            : "Waiting"
                    );


                    setElement(
                        "pressure",
                        properties.pressure !== null &&
                        properties.pressure !== undefined
                            ? formatValue(
                                properties.pressure,
                                " kPa"
                            )
                            : "Waiting"
                    );


                    setElement(
                        "rainfall",
                        properties.rainfall !== null &&
                        properties.rainfall !== undefined
                            ? formatValue(
                                properties.rainfall,
                                " mm"
                            )
                            : "Waiting"
                    );


                    setElement(
                        "temperature",
                        properties.temperature !== null &&
                        properties.temperature !== undefined
                            ? formatValue(
                                properties.temperature,
                                " °C"
                            )
                            : "Waiting"
                    );


                    setElement(
                        "vibration",
                        properties.vibration !== null &&
                        properties.vibration !== undefined
                            ? formatValue(
                                properties.vibration,
                                " g"
                            )
                            : "Waiting"
                    );


                    const factors =
                        properties.risk_factors || [];


                    const factorsElement =
                        document.getElementById(
                            "risk-factors"
                        );


                    if (factorsElement) {

                        factorsElement.innerHTML = "";


                        if (
                            factors.length === 0
                        ) {

                            factorsElement.innerHTML =
                                "<li>No significant terrain factors detected.</li>";

                        } else {

                            factors.forEach(
                                function(factor) {

                                    const li =
                                        document.createElement(
                                            "li"
                                        );

                                    li.textContent =
                                        factor;

                                    factorsElement.appendChild(
                                        li
                                    );
                                }
                            );
                        }
                    }


                    setElement(
                        "risk-recommendation",
                        properties.risk_recommendation ||
                        "Continue monitoring."
                    );
                }


                window.closeZoneDashboard =
                    function() {

                        const dashboard =
                            document.getElementById(
                                "zone-dashboard"
                            );

                        if (dashboard) {

                            dashboard.style.display =
                                "none";
                        }
                    };


                function openZone(
                    layer
                ) {

                    if (
                        !layer ||
                        !layer.feature ||
                        !layer.feature.properties
                    ) {
                        return;
                    }


                    showZoneDashboard(
                        layer.feature.properties
                    );


                    if (
                        layer.getBounds
                    ) {

                        mapInstance.fitBounds(
                            layer.getBounds(),
                            {
                                padding: [
                                    70,
                                    410,
                                    70,
                                    70
                                ],
                                maxZoom: 16
                            }
                        );
                    }
                }


                zoneLayer.eachLayer(
                    function(layer) {

                        layer.on(
                            "click",
                            function() {

                                openZone(
                                    layer
                                );
                            }
                        );

                    }
                );


                window.searchZone =
                    function() {

                        const input =
                            document.getElementById(
                                "zone-search"
                            );

                        if (!input) {
                            return;
                        }


                        const query =
                            input.value
                                .trim()
                                .toUpperCase();


                        if (!query) {
                            return;
                        }


                        zoneLayer.eachLayer(
                            function(layer) {

                                if (
                                    !layer.feature ||
                                    !layer.feature.properties
                                ) {
                                    return;
                                }


                                const zoneId =
                                    String(
                                        layer.feature.properties.zone_id ||
                                        ""
                                    ).toUpperCase();


                                if (
                                    zoneId === query
                                ) {

                                    openZone(
                                        layer
                                    );
                                }

                            }
                        );
                    };


                const searchInput =
                    document.getElementById(
                        "zone-search"
                    );


                if (searchInput) {

                    searchInput.addEventListener(
                        "keydown",
                        function(event) {

                            if (
                                event.key === "Enter"
                            ) {

                                window.searchZone();
                            }

                        }
                    );
                }


            },
            700
        );

    }
);

</script>
"""


javascript = javascript.replace(
    "__MAP_NAME__",
    map_name
)


javascript = javascript.replace(
    "__ZONE_GEOJSON__",
    zone_geojson_name
)


mine_map.get_root().html.add_child(
    Element(javascript)
)


folium.LayerControl(
    collapsed=False
).add_to(
    mine_map
)


mine_map.save(
    OUTPUT_FILE
)


print()
print("==========================================")
print("MINEGUARD AI GIS DASHBOARD CREATED")
print("==========================================")
print()
print(f"Output: {OUTPUT_FILE}")
print(f"Zones integrated: {len(zone_data)}")
print()
print("JSON integration       : SUCCESS")
print("AI risk integration    : SUCCESS")
print("Risk heatmap           : ENABLED")
print("Explainable AI         : ENABLED")
print("DEM visualization      : ENABLED")
print("Slope visualization    : ENABLED")
print("Interactive dashboard  : ENABLED")
print("Professional UI        : ENABLED")
print("Zone search            : ENABLED")
print("Sensor layer           : ENABLED")
print("IoT-ready              : YES")
print()
print("==========================================")
print("OPEN mine_map.html")
print("==========================================")