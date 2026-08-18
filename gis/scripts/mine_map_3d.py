from pathlib import Path
import json

import geopandas as gpd


BASE_DIR = Path(__file__).resolve().parents[2]

ZONE_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "gis"
    / "zones.geojson"
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

OUTPUT_FILE = BASE_DIR / "mine_map_3d.html"

KUSUNDA_LAT = 23.7822
KUSUNDA_LON = 86.3933


print("==========================================")
print("MineGuard AI - 3D Terrain Intelligence")
print("==========================================")


if not ZONE_FILE.exists():
    raise FileNotFoundError(
        f"Zone file not found:\n{ZONE_FILE}"
    )


if not ZONE_DATA_FILE.exists():
    raise FileNotFoundError(
        f"Zone API data not found:\n{ZONE_DATA_FILE}"
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

        "elevation": gis.get(
            "mean_elevation_m",
            0
        ),

        "min_elevation": gis.get(
            "min_elevation_m",
            0
        ),

        "max_elevation": gis.get(
            "max_elevation_m",
            0
        ),

        "slope": gis.get(
            "mean_slope_deg",
            0
        ),

        "max_slope": gis.get(
            "max_slope_deg",
            0
        ),

        "roughness": gis.get(
            "mean_roughness",
            0
        ),

        "aspect": gis.get(
            "mean_aspect_deg",
            0
        ),

        "gis_indicator": gis.get(
            "gis_terrain_indicator",
            0
        ),

        "terrain_condition": gis.get(
            "gis_terrain_condition",
            "UNKNOWN"
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
        )
    }

    zone_features.append(
        {
            "type": "Feature",
            "geometry": zone.geometry.__geo_interface__,
            "properties": properties
        }
    )


sensor_features = []


if SENSOR_FILE.exists():

    sensors = gpd.read_file(
        SENSOR_FILE
    ).to_crs("EPSG:4326")

    for _, sensor in sensors.iterrows():

        if sensor.geometry is None:
            continue

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

        sensor_features.append(
            {
                "id": str(sensor_id),
                "type": str(sensor_type),
                "lat": float(
                    sensor.geometry.y
                ),
                "lon": float(
                    sensor.geometry.x
                )
            }
        )

else:

    sensor_features = [
        {
            "id": "SENSOR-001",
            "type": "Environmental",
            "lat": 23.7845,
            "lon": 86.3905
        },
        {
            "id": "SENSOR-002",
            "type": "Ground Movement",
            "lat": 23.7830,
            "lon": 86.3960
        },
        {
            "id": "SENSOR-003",
            "type": "Gas Monitoring",
            "lat": 23.7795,
            "lon": 86.3935
        },
        {
            "id": "SENSOR-004",
            "type": "Environmental",
            "lat": 23.7850,
            "lon": 86.3990
        }
    ]


zone_json = json.dumps(
    {
        "type": "FeatureCollection",
        "features": zone_features
    }
)


sensor_json = json.dumps(
    sensor_features
)


html_document = """
<!DOCTYPE html>

<html>

<head>

<meta charset="utf-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

<title>
MineGuard AI - 3D Terrain Intelligence
</title>

<link
    href="https://cesium.com/downloads/cesiumjs/releases/1.139/Build/Cesium/Widgets/widgets.css"
    rel="stylesheet"
>

<script src="https://cesium.com/downloads/cesiumjs/releases/1.139/Build/Cesium/Cesium.js"></script>

<style>

* {
    box-sizing: border-box;
}

html,
body,
#cesiumContainer {
    width: 100%;
    height: 100%;
    margin: 0;
    padding: 0;
    overflow: hidden;
    font-family: Arial, sans-serif;
}

body {
    background: #07111f;
}

.cesium-viewer-toolbar,
.cesium-viewer-animationContainer,
.cesium-viewer-timelineContainer,
.cesium-viewer-bottom {
    display: none !important;
}

#topbar {
    position: fixed;
    top: 18px;
    left: 22px;
    right: 22px;
    z-index: 1000;

    display: flex;
    align-items: center;
    justify-content: space-between;

    padding: 13px 17px;

    border: 1px solid rgba(148,163,184,.20);
    border-radius: 16px;

    background: rgba(7,17,31,.90);

    backdrop-filter: blur(18px);

    box-shadow:
        0 15px 45px rgba(0,0,0,.35);
}

.brand {
    display: flex;
    align-items: center;
    gap: 11px;
}

.brand-icon {
    width: 34px;
    height: 34px;

    display: flex;
    align-items: center;
    justify-content: center;

    border-radius: 10px;

    background:
        linear-gradient(
            135deg,
            #22c7a5,
            #0891b2
        );

    color: #042f2e;

    font-size: 17px;
    font-weight: 800;
}

.brand-name {
    color: #f8fafc;
    font-size: 16px;
    font-weight: 800;
}

.brand-subtitle {
    margin-top: 2px;
    color: #64748b;
    font-size: 8px;
    letter-spacing: 1.1px;
}

.mode {
    display: flex;
    align-items: center;
    gap: 7px;
}

.mode-badge {
    padding: 7px 11px;

    border: 1px solid rgba(34,199,165,.22);
    border-radius: 999px;

    background: rgba(34,199,165,.07);

    color: #5eead4;

    font-size: 9px;
    font-weight: 800;
    letter-spacing: .8px;
}

.status-dot {
    width: 7px;
    height: 7px;

    border-radius: 50%;

    background: #22c7a5;

    box-shadow:
        0 0 12px rgba(34,199,165,.8);
}

#side-panel {
    position: fixed;

    top: 90px;
    right: 22px;
    bottom: 22px;

    width: 355px;

    z-index: 1000;

    overflow-y: auto;

    border:
        1px solid
        rgba(148,163,184,.18);

    border-radius: 19px;

    background:
        rgba(7,17,31,.94);

    backdrop-filter:
        blur(22px);

    box-shadow:
        0 25px 70px
        rgba(0,0,0,.42);

    color: #e2e8f0;

    transform:
        translateX(380px);

    transition:
        transform .28s ease;
}

#side-panel.open {
    transform:
        translateX(0);
}

#side-panel::-webkit-scrollbar {
    width: 5px;
}

#side-panel::-webkit-scrollbar-thumb {
    background: #334155;
    border-radius: 10px;
}

.panel-header {
    padding: 19px;

    border-bottom:
        1px solid
        rgba(148,163,184,.13);
}

.panel-eyebrow {
    color: #22c7a5;

    font-size: 8px;
    font-weight: 800;

    letter-spacing: 1.6px;
}

.panel-zone {
    margin-top: 5px;

    color: #f8fafc;

    font-size: 23px;
    font-weight: 800;
}

.panel-mine {
    margin-top: 4px;

    color: #64748b;

    font-size: 10px;
}

.panel-body {
    padding: 15px;
}

.section {
    margin-bottom: 18px;
}

.section-title {
    margin-bottom: 8px;

    color: #64748b;

    font-size: 8px;
    font-weight: 800;

    letter-spacing: 1.4px;
}

.risk-card {
    padding: 14px;

    border:
        1px solid
        rgba(148,163,184,.13);

    border-radius: 13px;

    background:
        rgba(30,41,59,.45);
}

.risk-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.risk-label {
    color: #64748b;

    font-size: 8px;
    font-weight: 700;
}

#risk-level {
    margin-top: 3px;

    font-size: 23px;
    font-weight: 800;
}

#risk-percent {
    color: #f8fafc;

    font-size: 21px;
    font-weight: 800;

    text-align: right;
}

.risk-percent-label {
    color: #64748b;

    font-size: 7px;

    text-align: right;
}

.progress {
    height: 5px;

    margin-top: 13px;

    overflow: hidden;

    border-radius: 20px;

    background: #1e293b;
}

#risk-progress {
    width: 0%;
    height: 100%;

    border-radius: 20px;

    transition:
        width .5s ease;
}

.metrics {
    display: grid;

    grid-template-columns:
        1fr 1fr;

    gap: 7px;
}

.metric {
    padding: 10px;

    border:
        1px solid
        rgba(148,163,184,.10);

    border-radius: 10px;

    background:
        rgba(30,41,59,.38);
}

.metric-name {
    color: #64748b;

    font-size: 7px;
    font-weight: 700;

    letter-spacing: .7px;

    text-transform: uppercase;
}

.metric-value {
    margin-top: 4px;

    color: #f1f5f9;

    font-size: 13px;
    font-weight: 700;
}

.factor {
    display: flex;
    gap: 8px;

    margin-bottom: 7px;

    color: #cbd5e1;

    font-size: 9px;
    line-height: 1.5;
}

.factor-dot {
    flex: 0 0 auto;

    width: 5px;
    height: 5px;

    margin-top: 5px;

    border-radius: 50%;

    background: #22c7a5;

    box-shadow:
        0 0 7px
        rgba(34,199,165,.65);
}

.recommendation {
    margin-top: 12px;

    padding: 11px;

    border-left:
        3px solid
        #22c7a5;

    border-radius: 8px;

    background:
        rgba(34,199,165,.05);

    color: #cbd5e1;

    font-size: 9px;

    line-height: 1.55;
}

.recommendation-title {
    margin-bottom: 5px;

    color: #22c7a5;

    font-size: 7px;
    font-weight: 800;

    letter-spacing: 1px;
}

.sensor-status {
    margin-bottom: 8px;

    padding: 9px;

    border:
        1px solid
        rgba(245,185,66,.14);

    border-radius: 8px;

    background:
        rgba(245,185,66,.05);

    color: #f5b942;

    font-size: 8px;
}

.sensor-grid {
    display: grid;

    grid-template-columns:
        1fr 1fr;

    gap: 7px;
}

.sensor {
    padding: 9px;

    border:
        1px solid
        rgba(103,232,249,.10);

    border-radius: 9px;

    background:
        rgba(8,47,73,.22);

    color: #64748b;

    font-size: 8px;
}

.sensor-value {
    margin-top: 4px;

    color: #67e8f9;

    font-size: 11px;
    font-weight: 700;
}

#bottom-panel {
    position: fixed;

    left: 22px;
    bottom: 22px;

    z-index: 1000;

    display: flex;

    gap: 7px;
}

.control-button {
    padding: 9px 13px;

    border:
        1px solid
        rgba(148,163,184,.20);

    border-radius: 10px;

    background:
        rgba(7,17,31,.90);

    backdrop-filter:
        blur(14px);

    color: #cbd5e1;

    cursor: pointer;

    font-size: 9px;
    font-weight: 700;

    transition:
        all .2s ease;
}

.control-button:hover {
    border-color:
        rgba(34,199,165,.35);

    color: #5eead4;

    transform:
        translateY(-1px);
}

#terrain-badge {
    position: fixed;

    left: 22px;
    top: 90px;

    z-index: 1000;

    padding: 10px 13px;

    border:
        1px solid
        rgba(148,163,184,.18);

    border-radius: 11px;

    background:
        rgba(7,17,31,.82);

    backdrop-filter:
        blur(14px);

    color: #94a3b8;

    font-size: 8px;

    letter-spacing: .6px;
}

#terrain-badge strong {
    color: #f8fafc;
}

#loading {
    position: fixed;

    inset: 0;

    z-index: 5000;

    display: flex;

    align-items: center;
    justify-content: center;

    background:
        #07111f;

    color: #cbd5e1;

    font-size: 12px;
}

.loading-box {
    text-align: center;
}

.loading-spinner {
    width: 32px;
    height: 32px;

    margin:
        0 auto 13px;

    border:
        2px solid
        #1e293b;

    border-top-color:
        #22c7a5;

    border-radius: 50%;

    animation:
        spin .8s linear infinite;
}

@keyframes spin {

    to {
        transform:
            rotate(360deg);
    }

}

@media(max-width:900px) {

    #side-panel {
        width:
            calc(100vw - 20px);

        right: 10px;

        top: 72px;

        bottom: 10px;
    }

    #topbar {
        left: 10px;
        right: 10px;
    }

    #terrain-badge {
        display: none;
    }

    .brand-subtitle {
        display: none;
    }

}

</style>

</head>

<body>

<div id="loading">

    <div class="loading-box">

        <div class="loading-spinner"></div>

        Initializing MineGuard 3D Terrain Intelligence

    </div>

</div>

<div id="cesiumContainer"></div>

<div id="topbar">

    <div class="brand">

        <div class="brand-icon">
            ⛏
        </div>

        <div>

            <div class="brand-name">
                MineGuard AI
            </div>

            <div class="brand-subtitle">
                3D TERRAIN INTELLIGENCE
            </div>

        </div>

    </div>

    <div class="mode">

        <span class="status-dot"></span>

        <span class="mode-badge">
            3D TERRAIN MODE
        </span>

    </div>

</div>

<div id="terrain-badge">

    TERRAIN EXAGGERATION
    <strong>1.8×</strong>

    &nbsp; • &nbsp;

    AI RISK LAYERS

</div>

<div id="side-panel">

    <div class="panel-header">

        <div class="panel-eyebrow">
            MINE SAFETY INTELLIGENCE
        </div>

        <div
            id="panel-zone"
            class="panel-zone"
        >
            Select Zone
        </div>

        <div
            id="panel-mine"
            class="panel-mine"
        >
            MINE-001
        </div>

    </div>

    <div class="panel-body">

        <div class="section">

            <div class="section-title">
                AI RISK ASSESSMENT
            </div>

            <div class="risk-card">

                <div class="risk-row">

                    <div>

                        <div class="risk-label">
                            CURRENT RISK
                        </div>

                        <div id="risk-level">
                            —
                        </div>

                    </div>

                    <div>

                        <div id="risk-percent">
                            —
                        </div>

                        <div class="risk-percent-label">
                            PROBABILITY
                        </div>

                    </div>

                </div>

                <div class="progress">

                    <div id="risk-progress"></div>

                </div>

            </div>

        </div>

        <div class="section">

            <div class="section-title">
                TERRAIN PROFILE
            </div>

            <div class="metrics">

                <div class="metric">

                    <div class="metric-name">
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

                    <div class="metric-name">
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

                    <div class="metric-name">
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

                    <div class="metric-name">
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

                    <div class="metric-name">
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

                    <div class="metric-name">
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
                WHY THIS ZONE IS AT RISK
            </div>

            <div id="factors"></div>

            <div class="recommendation">

                <div class="recommendation-title">
                    RECOMMENDED ACTION
                </div>

                <div id="recommendation">
                    Select a zone.
                </div>

            </div>

        </div>

        <div class="section">

            <div class="section-title">
                LIVE SENSOR TELEMETRY
            </div>

            <div class="sensor-status">
                ⏳ Awaiting IoT sensor integration
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

<div id="bottom-panel">

    <button
        class="control-button"
        onclick="resetCamera()"
    >
        ⌂ Reset View
    </button>

    <button
        class="control-button"
        onclick="togglePanel()"
    >
        ◫ Zone Intelligence
    </button>

    <button
        class="control-button"
        onclick="toggleExaggeration()"
    >
        ⛰ Terrain Depth
    </button>

</div>

<script>

const zoneData =
    __ZONE_DATA__;

const sensorData =
    __SENSOR_DATA__;

const MINEGUARD_LAT =
    __LATITUDE__;

const MINEGUARD_LON =
    __LONGITUDE__;


const viewer =
    new Cesium.Viewer(
        "cesiumContainer",
        {
            animation: false,
            timeline: false,
            fullscreenButton: false,
            navigationHelpButton: false,
            sceneModePicker: false,
            geocoder: false,
            homeButton: false,
            infoBox: false,
            selectionIndicator: false,
            baseLayerPicker: false,
            shouldAnimate: false
        }
    );


viewer.scene.backgroundColor =
    Cesium.Color.fromCssColorString(
        "#07111f"
    );


viewer.scene.globe.baseColor =
    Cesium.Color.fromCssColorString(
        "#172235"
    );


viewer.scene.globe.enableLighting =
    true;


viewer.scene.globe.showGroundAtmosphere =
    true;


viewer.scene.globe.depthTestAgainstTerrain =
    false;


viewer.scene.globe.terrainExaggeration =
    1.8;


let currentExaggeration =
    1.8;


function riskColor(level) {

    level =
        String(level)
            .toUpperCase();


    if (level === "HIGH") {
        return "#ff4d67";
    }


    if (level === "MODERATE") {
        return "#f5b942";
    }


    if (level === "LOW") {
        return "#22c7a5";
    }


    return "#94a3b8";
}


function hexToCesium(
    hex,
    alpha
) {

    return Cesium.Color
        .fromCssColorString(
            hex
        )
        .withAlpha(
            alpha
        );
}


function getPolygonCenter(
    points
) {

    let longitude = 0;

    let latitude = 0;


    points.forEach(
        function(point) {

            longitude +=
                point[0];

            latitude +=
                point[1];

        }
    );


    return [
        longitude / points.length,
        latitude / points.length
    ];
}


function getProperty(
    entity,
    name
) {

    if (
        !entity.properties ||
        !entity.properties[name]
    ) {

        return null;

    }


    return entity.properties[name].getValue(
        Cesium.JulianDate.now()
    );
}


zoneData.features.forEach(
    function(feature) {

        if (
            !feature.geometry ||
            !feature.geometry.coordinates
        ) {

            return;

        }


        let coordinates =
            feature.geometry.coordinates;


        let rings;


        if (
            feature.geometry.type ===
            "Polygon"
        ) {

            rings = coordinates;

        } else if (
            feature.geometry.type ===
            "MultiPolygon"
        ) {

            rings =
                coordinates[0];

        } else {

            return;

        }


        if (
            !rings ||
            !rings[0] ||
            rings[0].length < 3
        ) {

            return;

        }


        const properties =
            feature.properties;


        const level =
            properties.risk_level ||
            "UNKNOWN";


        const color =
            riskColor(level);


        const elevation =
            Number(
                properties.elevation || 0
            );


        const baseHeight =
            Math.max(
                0,
                elevation - 20
            );


        const positions =
            rings[0].map(
                function(point) {

                    return Cesium
                        .Cartesian3
                        .fromDegrees(
                            point[0],
                            point[1],
                            baseHeight
                        );

                }
            );


        const entity =
            viewer.entities.add(
                {
                    name:
                        properties.zone_id,

                    polygon:
                        {
                            hierarchy:
                                positions,

                            height:
                                baseHeight,

                            extrudedHeight:
                                baseHeight + 45,

                            material:
                                hexToCesium(
                                    color,
                                    0.18
                                ),

                            outline:
                                true,

                            outlineColor:
                                hexToCesium(
                                    color,
                                    0.95
                                ),

                            outlineWidth:
                                2
                        },

                    properties:
                        properties
                }
            );


        const center =
            getPolygonCenter(
                rings[0]
            );


        viewer.entities.add(
            {
                position:
                    Cesium
                        .Cartesian3
                        .fromDegrees(
                            center[0],
                            center[1],
                            baseHeight + 70
                        ),

                label:
                    {
                        text:
                            properties.zone_id +
                            "  •  " +
                            level,

                        font:
                            "700 11px Arial",

                        fillColor:
                            Cesium.Color.WHITE,

                        outlineColor:
                            Cesium.Color.BLACK,

                        outlineWidth:
                            3,

                        style:
                            Cesium
                                .LabelStyle
                                .FILL_AND_OUTLINE,

                        verticalOrigin:
                            Cesium
                                .VerticalOrigin
                                .BOTTOM,

                        pixelOffset:
                            new Cesium.Cartesian2(
                                0,
                                -8
                            ),

                        disableDepthTestDistance:
                            Number.POSITIVE_INFINITY
                    }
            }
        );

    }
);


sensorData.forEach(
    function(sensor) {

        const position =
            Cesium
                .Cartesian3
                .fromDegrees(
                    Number(sensor.lon),
                    Number(sensor.lat),
                    60
                );


        viewer.entities.add(
            {
                position:
                    position,

                point:
                    {
                        pixelSize:
                            9,

                        color:
                            Cesium
                                .Color
                                .fromCssColorString(
                                    "#67e8f9"
                                ),

                        outlineColor:
                            Cesium.Color.WHITE,

                        outlineWidth:
                            1,

                        heightReference:
                            Cesium
                                .HeightReference
                                .RELATIVE_TO_GROUND,

                        disableDepthTestDistance:
                            Number.POSITIVE_INFINITY
                    },

                label:
                    {
                        text:
                            String(
                                sensor.id
                            ),

                        font:
                            "600 9px Arial",

                        fillColor:
                            Cesium
                                .Color
                                .fromCssColorString(
                                    "#67e8f9"
                                ),

                        pixelOffset:
                            new Cesium.Cartesian2(
                                0,
                                -18
                            ),

                        disableDepthTestDistance:
                            Number.POSITIVE_INFINITY
                    }
            }
        );

    }
);


const handler =
    new Cesium.ScreenSpaceEventHandler(
        viewer.scene.canvas
    );


handler.setInputAction(
    function(click) {

        const picked =
            viewer.scene.pick(
                click.position
            );


        if (
            !Cesium.defined(picked) ||
            !picked.id
        ) {

            return;

        }


        const entity =
            picked.id;


        if (
            !entity.properties ||
            !entity.properties.zone_id
        ) {

            return;

        }


        showZone(entity);

    },
    Cesium.ScreenSpaceEventType.LEFT_CLICK
);


function setText(
    id,
    value
) {

    const element =
        document.getElementById(id);


    if (element) {

        element.textContent =
            value;

    }
}


function setMetric(
    id,
    value,
    suffix
) {

    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {

        setText(
            id,
            "—"
        );

        return;

    }


    if (
        typeof value ===
        "number"
    ) {

        setText(
            id,
            value.toFixed(3) +
            suffix
        );

        return;

    }


    setText(
        id,
        String(value) +
        suffix
    );
}


function setSensor(
    id,
    value,
    suffix
) {

    if (
        value === null ||
        value === undefined
    ) {

        setText(
            id,
            "Waiting"
        );

        return;

    }


    if (
        typeof value ===
        "number"
    ) {

        setText(
            id,
            value.toFixed(3) +
            suffix
        );

        return;

    }


    setText(
        id,
        String(value) +
        suffix
    );
}


function showZone(
    entity
) {

    const zone =
        getProperty(
            entity,
            "zone_id"
        ) ||
        "UNKNOWN";


    const mine =
        getProperty(
            entity,
            "mine_id"
        ) ||
        "MINE-001";


    const risk =
        getProperty(
            entity,
            "risk_level"
        ) ||
        "UNKNOWN";


    const color =
        riskColor(risk);


    setText(
        "panel-zone",
        zone
    );


    setText(
        "panel-mine",
        mine
    );


    const riskElement =
        document.getElementById(
            "risk-level"
        );


    riskElement.textContent =
        risk;


    riskElement.style.color =
        color;


    let probability =
        Number(
            getProperty(
                entity,
                "risk_probability"
            )
        );


    if (
        Number.isFinite(
            probability
        )
    ) {

        if (
            probability <= 1
        ) {

            probability *=
                100;

        }


        probability =
            Math.max(
                0,
                Math.min(
                    100,
                    probability
                )
            );


        setText(
            "risk-percent",
            probability.toFixed(2) +
            "%"
        );


        const progress =
            document.getElementById(
                "risk-progress"
            );


        progress.style.width =
            probability +
            "%";


        progress.style.background =
            color;

    } else {

        setText(
            "risk-percent",
            "—"
        );


        document.getElementById(
            "risk-progress"
        ).style.width =
            "0%";
    }


    setMetric(
        "elevation",
        getProperty(
            entity,
            "elevation"
        ),
        " m"
    );


    setMetric(
        "slope",
        getProperty(
            entity,
            "slope"
        ),
        "°"
    );


    setMetric(
        "max-slope",
        getProperty(
            entity,
            "max_slope"
        ),
        "°"
    );


    setMetric(
        "roughness",
        getProperty(
            entity,
            "roughness"
        ),
        " m"
    );


    setMetric(
        "aspect",
        getProperty(
            entity,
            "aspect"
        ),
        "°"
    );


    setMetric(
        "gis-indicator",
        getProperty(
            entity,
            "gis_indicator"
        ),
        ""
    );


    const factors =
        getProperty(
            entity,
            "risk_factors"
        ) || [];


    const factorsContainer =
        document.getElementById(
            "factors"
        );


    factorsContainer.innerHTML =
        "";


    if (
        !Array.isArray(factors) ||
        factors.length === 0
    ) {

        factorsContainer.innerHTML =
            '<div class="factor">' +
            '<span class="factor-dot"></span>' +
            '<span>No significant terrain factors detected.</span>' +
            '</div>';

    } else {

        factors.forEach(
            function(factor) {

                const item =
                    document.createElement(
                        "div"
                    );


                item.className =
                    "factor";


                const dot =
                    document.createElement(
                        "span"
                    );


                dot.className =
                    "factor-dot";


                const text =
                    document.createElement(
                        "span"
                    );


                text.textContent =
                    String(factor);


                item.appendChild(
                    dot
                );


                item.appendChild(
                    text
                );


                factorsContainer.appendChild(
                    item
                );

            }
        );

    }


    setText(
        "recommendation",
        getProperty(
            entity,
            "risk_recommendation"
        ) ||
        "Continue monitoring."
    );


    setSensor(
        "displacement",
        getProperty(
            entity,
            "displacement"
        ),
        " mm"
    );


    setSensor(
        "strain",
        getProperty(
            entity,
            "strain"
        ),
        ""
    );


    setSensor(
        "pressure",
        getProperty(
            entity,
            "pressure"
        ),
        " kPa"
    );


    setSensor(
        "rainfall",
        getProperty(
            entity,
            "rainfall"
        ),
        " mm"
    );


    setSensor(
        "temperature",
        getProperty(
            entity,
            "temperature"
        ),
        " °C"
    );


    setSensor(
        "vibration",
        getProperty(
            entity,
            "vibration"
        ),
        " g"
    );


    document
        .getElementById(
            "side-panel"
        )
        .classList
        .add(
            "open"
        );


    viewer.flyTo(
        entity,
        {
            duration:
                1.2,

            offset:
                new Cesium
                    .HeadingPitchRange(
                        0,
                        Cesium.Math.toRadians(
                            -42
                        ),
                        750
                    )
        }
    );
}


function togglePanel() {

    document
        .getElementById(
            "side-panel"
        )
        .classList
        .toggle(
            "open"
        );
}


function resetCamera() {

    viewer.camera.flyTo(
        {
            destination:
                Cesium
                    .Cartesian3
                    .fromDegrees(
                        MINEGUARD_LON,
                        MINEGUARD_LAT,
                        900
                    ),

            orientation:
                {
                    heading:
                        Cesium.Math.toRadians(
                            0
                        ),

                    pitch:
                        Cesium.Math.toRadians(
                            -58
                        ),

                    roll:
                        0
                },

            duration:
                1.2
        }
    );
}


function toggleExaggeration() {

    if (
        currentExaggeration ===
        1.8
    ) {

        currentExaggeration =
            3.0;

    } else {

        currentExaggeration =
            1.8;

    }


    viewer.scene.globe
        .terrainExaggeration =
        currentExaggeration;


    document
        .querySelector(
            "#terrain-badge strong"
        )
        .textContent =
        currentExaggeration +
        "×";
}


viewer.camera.flyTo(
    {
        destination:
            Cesium
                .Cartesian3
                .fromDegrees(
                    MINEGUARD_LON,
                    MINEGUARD_LAT,
                    900
                ),

        orientation:
            {
                heading:
                    Cesium.Math.toRadians(
                        0
                    ),

                pitch:
                    Cesium.Math.toRadians(
                        -58
                    ),

                roll:
                    0
            },

        duration:
            1.5
    }
);


document
    .getElementById(
        "loading"
    )
    .style
    .display =
    "none";

</script>

</body>

</html>
"""


html_document = html_document.replace(
    "__ZONE_DATA__",
    zone_json
)


html_document = html_document.replace(
    "__SENSOR_DATA__",
    sensor_json
)


html_document = html_document.replace(
    "__LATITUDE__",
    str(KUSUNDA_LAT)
)


html_document = html_document.replace(
    "__LONGITUDE__",
    str(KUSUNDA_LON)
)


with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as file:

    file.write(
        html_document
    )


print()
print("==========================================")
print("3D MINEGUARD DASHBOARD CREATED")
print("==========================================")
print()
print(
    f"Output: {OUTPUT_FILE}"
)
print(
    f"Zones integrated: {len(zone_features)}"
)
print(
    f"Sensors integrated: {len(sensor_features)}"
)
print()
print("AI RISK LAYERS       : ENABLED")
print("3D ZONE EXTRUSION    : ENABLED")
print("ZONE LABELS          : ENABLED")
print("3D SENSOR MARKERS    : ENABLED")
print("TERRAIN DEPTH        : ENABLED")
print("ZONE INTELLIGENCE    : ENABLED")
print("IoT READY            : YES")
print()
print("==========================================")
print("OPEN mine_map_3d.html")
print("==========================================")