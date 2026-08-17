from pathlib import Path
import json
import html

import folium
import geopandas as gpd


BASE_DIR = Path(__file__).resolve().parents[1]

ZONE_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "gis"
    / "zones.geojson"
)

ROAD_FILE = (
    BASE_DIR
    / "data"
    / "raw"
    / "gis"
    / "roads.geojson"
)

ZONE_DATA_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "gis"
    / "zone_api_data.json"
)

SENSOR_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "gis"
    / "sensors.geojson"
)

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
print("MineGuard AI - GIS Dashboard")
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
    control_scale=True
)


elevation_layer = folium.FeatureGroup(
    name="Elevation / DEM",
    show=False
)


folium.raster_layers.ImageOverlay(
    image=str(ELEVATION_IMAGE),
    bounds=[
        [
            23.77875,
            86.38986111111112
        ],
        [
            23.785138888888888,
            86.39819444444446
        ]
    ],
    opacity=0.42,
    interactive=True,
    cross_origin=False,
    zindex=1
).add_to(
    elevation_layer
)


elevation_layer.add_to(
    mine_map
)


slope_layer = folium.FeatureGroup(
    name="Slope Map",
    show=False
)


folium.raster_layers.ImageOverlay(
    image=str(SLOPE_IMAGE),
    bounds=[
        [
            23.77877868536618,
            86.3898312967052
        ],
        [
            23.78517143564985,
            86.39816966664041
        ]
    ],
    opacity=0.42,
    interactive=True,
    cross_origin=False,
    zindex=2
).add_to(
    slope_layer
)


slope_layer.add_to(
    mine_map
)


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
    color="#111827",
    weight=3,
    fill=False,
    popup="Kusunda Mine Study Area"
).add_to(
    study_layer
)


study_layer.add_to(
    mine_map
)


road_layer = folium.FeatureGroup(
    name="Road Network",
    show=True
)


road_options = {
    "style_function": lambda feature: {
        "color": "#555555",
        "weight": 2,
        "opacity": 0.75
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
).add_to(
    road_layer
)


road_layer.add_to(
    mine_map
)


def risk_color(level):
    level = str(level).upper()

    if level == "HIGH":
        return "#ef4444"

    if level == "MODERATE":
        return "#f59e0b"

    if level == "LOW":
        return "#22c55e"

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

        "terrain_condition": gis.get(
            "gis_terrain_condition",
            "UNKNOWN"
        ),

        "gis_indicator": gis.get(
            "gis_terrain_indicator"
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
    name="AI Risk Heatmap",
    show=True
)


def zone_style(feature):

    risk_level = feature[
        "properties"
    ].get(
        "risk_level",
        "UNKNOWN"
    )

    color = risk_color(
        risk_level
    )

    return {
        "color": color,
        "weight": 3,
        "fillColor": color,
        "fillOpacity": 0.45
    }


zone_geojson = folium.GeoJson(
    {
        "type": "FeatureCollection",
        "features": zone_features
    },
    style_function=zone_style,
    highlight_function=lambda feature: {
        "weight": 5,
        "fillOpacity": 0.60
    },
    tooltip=folium.GeoJsonTooltip(
        fields=[
            "zone_id",
            "risk_level"
        ],
        aliases=[
            "Zone:",
            "AI Risk:"
        ],
        sticky=True
    )
)


zone_geojson.add_to(
    zone_layer
)


zone_layer.add_to(
    mine_map
)


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
        <div style="font-family:Arial;width:220px">
        <h4>MineGuard Sensor</h4>
        <b>Sensor ID:</b> {html.escape(str(sensor_id))}<br>
        <b>Type:</b> {html.escape(str(sensor_type))}<br>
        <b>Status:</b> Ready for IoT
        </div>
        """

        folium.CircleMarker(
            location=[
                sensor.geometry.y,
                sensor.geometry.x
            ],
            radius=7,
            color="#2563eb",
            fill=True,
            fill_color="#3b82f6",
            fill_opacity=0.95,
            tooltip=str(sensor_id),
            popup=folium.Popup(
                popup,
                max_width=280
            )
        ).add_to(
            sensor_layer
        )

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
        <div style="font-family:Arial;width:220px">
        <h4>MineGuard Sensor</h4>
        <b>Sensor ID:</b> {sensor["id"]}<br>
        <b>Type:</b> {sensor["type"]}<br>
        <b>Status:</b> Prototype
        </div>
        """

        folium.CircleMarker(
            location=[
                sensor["lat"],
                sensor["lon"]
            ],
            radius=7,
            color="#2563eb",
            fill=True,
            fill_color="#3b82f6",
            fill_opacity=0.95,
            tooltip=sensor["id"],
            popup=folium.Popup(
                popup,
                max_width=280
            )
        ).add_to(
            sensor_layer
        )


sensor_layer.add_to(
    mine_map
)


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
    color="#8b5cf6",
    weight=2,
    fill=True,
    fill_color="#8b5cf6",
    fill_opacity=0.15,
    popup="Gas Monitoring Area"
).add_to(
    gas_layer
)


gas_layer.add_to(
    mine_map
)


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
    color="#dc2626",
    weight=2,
    fill=True,
    fill_color="#ef4444",
    fill_opacity=0.15,
    popup="Thermal / Fire Monitoring Area"
).add_to(
    thermal_layer
)


thermal_layer.add_to(
    mine_map
)


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
    color="#111827",
    weight=2,
    fill=True,
    fill_color="#111827",
    fill_opacity=0.25,
    popup="Restricted Area"
).add_to(
    restricted_layer
)


restricted_layer.add_to(
    mine_map
)


css = """
<style>

#mineguard-header {
    position:fixed;
    top:18px;
    left:60px;
    z-index:9998;
    background:linear-gradient(135deg,#0f172a,#1e293b);
    color:white;
    padding:14px 20px;
    border-radius:14px;
    box-shadow:0 8px 25px rgba(0,0,0,.25);
    font-family:Arial,sans-serif;
    min-width:300px;
}

#mineguard-header .title {
    font-size:20px;
    font-weight:800;
}

#mineguard-header .subtitle {
    font-size:11px;
    color:#cbd5e1;
    margin-top:4px;
}

#mineguard-status {
    position:fixed;
    top:18px;
    right:65px;
    z-index:9998;
    background:rgba(255,255,255,.96);
    padding:9px 15px;
    border-radius:20px;
    font-family:Arial,sans-serif;
    font-size:12px;
    font-weight:600;
    box-shadow:0 4px 15px rgba(0,0,0,.18);
}

.status-dot {
    display:inline-block;
    width:9px;
    height:9px;
    background:#22c55e;
    border-radius:50%;
    margin-right:6px;
}

#zone-dashboard {
    position:fixed;
    top:80px;
    right:18px;
    z-index:10000;
    width:370px;
    max-height:calc(100vh - 105px);
    overflow-y:auto;
    background:rgba(255,255,255,.98);
    border-radius:18px;
    box-shadow:0 15px 45px rgba(0,0,0,.25);
    font-family:Arial,sans-serif;
    display:none;
}

.dashboard-header {
    position:relative;
    background:linear-gradient(135deg,#0f172a,#1e293b);
    color:white;
    padding:18px;
    border-radius:18px 18px 0 0;
}

.dashboard-header .zone {
    font-size:22px;
    font-weight:800;
}

.dashboard-header .mine {
    color:#cbd5e1;
    font-size:12px;
    margin-top:4px;
}

.close-dashboard {
    position:absolute;
    top:10px;
    right:15px;
    cursor:pointer;
    color:white;
    font-size:24px;
    line-height:1;
}

.dashboard-body {
    padding:16px;
}

.section {
    margin-bottom:18px;
}

.section-title {
    font-size:10px;
    font-weight:800;
    color:#64748b;
    letter-spacing:1px;
    margin-bottom:9px;
}

.condition {
    padding:12px;
    border-radius:12px;
    font-size:18px;
    font-weight:800;
    text-align:center;
}

.metrics {
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:8px;
}

.metric {
    background:#f8fafc;
    border:1px solid #e2e8f0;
    border-radius:10px;
    padding:10px;
}

.metric-label {
    color:#64748b;
    font-size:10px;
}

.metric-value {
    color:#0f172a;
    font-size:14px;
    font-weight:700;
    margin-top:3px;
}

.sensor-grid {
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:7px;
}

.sensor {
    background:#eff6ff;
    border-radius:9px;
    padding:9px;
    font-size:10px;
    color:#475569;
}

.sensor-value {
    font-size:13px;
    font-weight:700;
    color:#1e3a8a;
    margin-top:3px;
}

.risk-box {
    background:#f8fafc;
    border:1px solid #e2e8f0;
    border-radius:12px;
    padding:13px;
    text-align:center;
}

.risk-level {
    font-size:26px;
    font-weight:900;
}

.explanation-box {
    background:#f8fafc;
    border:1px solid #e2e8f0;
    border-radius:12px;
    padding:12px;
}

.explanation-list {
    margin:0;
    padding-left:20px;
    color:#334155;
    font-size:12px;
    line-height:1.8;
}

.recommendation {
    margin-top:12px;
    background:#eef2ff;
    border-radius:10px;
    padding:11px;
    color:#334155;
    font-size:12px;
    line-height:1.5;
}

.recommendation-title {
    font-size:10px;
    font-weight:800;
    color:#64748b;
    margin-bottom:5px;
}

#mineguard-search {
    position:fixed;
    bottom:25px;
    left:25px;
    z-index:9998;
    background:white;
    padding:9px 12px;
    border-radius:12px;
    box-shadow:0 5px 20px rgba(0,0,0,.18);
    font-family:Arial,sans-serif;
}

#mineguard-search input {
    border:none;
    outline:none;
    width:180px;
    font-size:13px;
}

#mineguard-legend {
    position:fixed;
    bottom:25px;
    right:400px;
    z-index:9998;
    background:rgba(255,255,255,.97);
    padding:12px 15px;
    border-radius:12px;
    box-shadow:0 5px 20px rgba(0,0,0,.15);
    font-family:Arial,sans-serif;
    font-size:11px;
}

.legend-item {
    margin:5px 0;
}

.legend-dot {
    display:inline-block;
    width:10px;
    height:10px;
    border-radius:3px;
    margin-right:6px;
}

@media(max-width:900px) {

    #zone-dashboard {
        width:310px;
        right:10px;
    }

    #mineguard-header {
        left:55px;
        min-width:230px;
    }

    #mineguard-status {
        display:none;
    }

    #mineguard-legend {
        display:none;
    }
}

</style>
"""


mine_map.get_root().html.add_child(
    folium.Element(css)
)


header = """
<div id="mineguard-header">

    <div class="title">
        ⛏ MineGuard AI
    </div>

    <div class="subtitle">
        Intelligent Mine Safety & Terrain Monitoring
    </div>

</div>

<div id="mineguard-status">

    <span class="status-dot"></span>

    GIS SYSTEM ONLINE

</div>
"""


mine_map.get_root().html.add_child(
    folium.Element(header)
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
                AI RISK STATUS
            </div>

            <div
                id="terrain-condition"
                class="condition"
            >
                UNKNOWN
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
                GIS TERRAIN INDICATORS
            </div>

            <div class="metrics">

                <div class="metric">
                    <div class="metric-label">
                        Slope Indicator
                    </div>
                    <div
                        id="slope-indicator"
                        class="metric-value"
                    >
                        —
                    </div>
                </div>

                <div class="metric">
                    <div class="metric-label">
                        Roughness Indicator
                    </div>
                    <div
                        id="roughness-indicator"
                        class="metric-value"
                    >
                        —
                    </div>
                </div>

                <div class="metric">
                    <div class="metric-label">
                        Terrain Variability
                    </div>
                    <div
                        id="terrain-variability"
                        class="metric-value"
                    >
                        —
                    </div>
                </div>

                <div class="metric">
                    <div class="metric-label">
                        GIS Indicator
                    </div>
                    <div
                        id="gis-indicator"
                        class="metric-value"
                    >
                        —
                    </div>
                </div>

            </div>

        </div>

        <div class="section">

            <div class="section-title">
                LIVE SENSOR DATA
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

        <div class="section">

            <div class="section-title">
                AI RISK ENGINE
            </div>

            <div class="risk-box">

                <div
                    id="risk-level"
                    class="risk-level"
                >
                    UNKNOWN
                </div>

                <div
                    style="
                    margin-top:7px;
                    color:#64748b;
                    font-size:12px;
                    "
                >
                    Probability:
                    <span id="risk-probability">
                        Waiting for ML
                    </span>
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

    </div>

</div>
"""


mine_map.get_root().html.add_child(
    folium.Element(dashboard)
)


search_box = """
<div id="mineguard-search">

    🔎

    <input
        id="zone-search"
        type="text"
        placeholder="Search ZONE-001"
    >

</div>
"""


mine_map.get_root().html.add_child(
    folium.Element(search_box)
)


legend = """
<div id="mineguard-legend">

    <b>AI Risk Heatmap</b>

    <div class="legend-item">
        <span
            class="legend-dot"
            style="background:#22c55e"
        ></span>
        LOW RISK
    </div>

    <div class="legend-item">
        <span
            class="legend-dot"
            style="background:#f59e0b"
        ></span>
        MODERATE RISK
    </div>

    <div class="legend-item">
        <span
            class="legend-dot"
            style="background:#ef4444"
        ></span>
        HIGH RISK
    </div>

    <div
        style="
        margin-top:8px;
        color:#64748b;
        font-size:10px;
        "
    >
        Based on MineGuard AI prediction
    </div>

</div>
"""


mine_map.get_root().html.add_child(
    folium.Element(legend)
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
                        document.getElementById(
                            id
                        );

                    if (element) {
                        element.textContent =
                            value;
                    }
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


                    setElement(
                        "terrain-condition",
                        riskLevel
                    );


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
                        "roughness",
                        formatValue(
                            properties.roughness,
                            " m"
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


                    if (
                        properties.risk_probability !== null &&
                        properties.risk_probability !== undefined
                    ) {

                        setElement(
                            "risk-probability",
                            (
                                Number(
                                    properties.risk_probability
                                ) * 100
                            ).toFixed(2)
                            + "%"
                        );

                    } else {

                        setElement(
                            "risk-probability",
                            "Waiting for ML"
                        );
                    }


                    setElement(
                        "risk-level",
                        riskLevel
                    );


                    const riskFactors =
                        properties.risk_factors ||
                        [];


                    const factorsElement =
                        document.getElementById(
                            "risk-factors"
                        );


                    if (factorsElement) {

                        factorsElement.innerHTML =
                            "";


                        if (
                            riskFactors.length === 0
                        ) {

                            factorsElement.innerHTML =
                                "<li>No significant terrain factors detected.</li>";

                        } else {

                            riskFactors.forEach(
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


                    const conditionBox =
                        document.getElementById(
                            "terrain-condition"
                        );


                    if (conditionBox) {

                        if (
                            riskLevel === "HIGH"
                        ) {

                            conditionBox.style.background =
                                "#fee2e2";

                            conditionBox.style.color =
                                "#b91c1c";

                        } else if (
                            riskLevel === "MODERATE"
                        ) {

                            conditionBox.style.background =
                                "#fef3c7";

                            conditionBox.style.color =
                                "#b45309";

                        } else if (
                            riskLevel === "LOW"
                        ) {

                            conditionBox.style.background =
                                "#dcfce7";

                            conditionBox.style.color =
                                "#15803d";

                        } else {

                            conditionBox.style.background =
                                "#f1f5f9";

                            conditionBox.style.color =
                                "#475569";
                        }
                    }


                    const riskBox =
                        document.getElementById(
                            "risk-level"
                        );


                    if (riskBox) {

                        if (
                            riskLevel === "HIGH"
                        ) {

                            riskBox.style.color =
                                "#dc2626";

                        } else if (
                            riskLevel === "MODERATE"
                        ) {

                            riskBox.style.color =
                                "#d97706";

                        } else if (
                            riskLevel === "LOW"
                        ) {

                            riskBox.style.color =
                                "#16a34a";

                        } else {

                            riskBox.style.color =
                                "#64748b";
                        }
                    }
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
                                    80,
                                    80
                                ],
                                maxZoom: 16
                            }
                        );
                    }
                }


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
            800
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
    folium.Element(
        javascript
    )
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
print("MINEGUARD GIS DASHBOARD CREATED")
print("==========================================")
print()
print(
    f"Output: {OUTPUT_FILE}"
)
print(
    f"Zones integrated: {len(zone_data)}"
)
print("JSON integration: SUCCESS")
print("AI risk integration: SUCCESS")
print("AI RISK HEATMAP: ENABLED")
print("Explainable AI: ENABLED")
print("DEM visualization: ENABLED")
print("Slope visualization: ENABLED")
print("Interactive dashboard: ENABLED")
print("Zone search: ENABLED")
print("Sensor layer: ENABLED")
print("OpenStreetMap: ENABLED")
print()
print("==========================================")
print("OPEN mine_map.html")
print("==========================================")