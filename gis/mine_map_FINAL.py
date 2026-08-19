from pathlib import Path
import json
import folium
import geopandas as gpd

try:
    from simulation.config import DEFAULT_BASELINE_VALUES
except Exception:
    DEFAULT_BASELINE_VALUES = {
        "displacement_mm": 4.2,
        "strain": 0.21,
        "pore_pressure_kpa": 31.5,
        "rainfall_mm": 3.2,
        "temperature_c": 28.5,
        "vibration_g": 0.18,
    }

BASE_DIR = Path(__file__).resolve().parents[1]

ZONE_FILE = BASE_DIR / "data" / "processed" / "gis" / "zones.geojson"
ROAD_FILE = BASE_DIR / "data" / "raw" / "gis" / "roads.geojson"
ZONE_DATA_FILE = BASE_DIR / "data" / "processed" / "gis" / "zone_api_data.json"
SENSOR_FILE = BASE_DIR / "data" / "processed" / "gis" / "sensors.geojson"
OUTPUT_FILE = BASE_DIR / "mine_map.html"

KUSUNDA = [23.7822, 86.3933]

for path in (ZONE_FILE, ROAD_FILE, ZONE_DATA_FILE, SENSOR_FILE):
    if not path.exists():
        raise FileNotFoundError(f"Required file not found:\n{path}")

with open(ZONE_DATA_FILE, "r", encoding="utf-8") as f:
    zone_api_data = json.load(f)

if isinstance(zone_api_data, dict):
    zone_api_data = zone_api_data.get("zones", [zone_api_data])

zone_data = {
    str(x.get("zone_id")): x
    for x in zone_api_data
    if x.get("zone_id") is not None
}

zones = gpd.read_file(ZONE_FILE).to_crs("EPSG:4326")
roads = gpd.read_file(ROAD_FILE).to_crs("EPSG:4326")
sensors = gpd.read_file(SENSOR_FILE).to_crs("EPSG:4326")

sensor_by_zone = {}

for _, sensor in sensors.iterrows():
    sensor_zone = str(sensor.get("zone_id", "")).strip()
    sensor_id = str(sensor.get("sensor_id", "")).strip()

    if sensor_zone:
        sensor_by_zone[sensor_zone] = sensor_id


def risk_color(value):
    value = str(value or "").upper()
    if value == "CRITICAL":
        return "#ff1744"
    if value == "HIGH":
        return "#ff4d67"
    if value == "MODERATE":
        return "#f5b942"
    if value == "LOW":
        return "#22c7a5"
    return "#94a3b8"


features = []

for _, zone in zones.iterrows():
    zone_id = str(zone.get("zone_id", ""))
    record = zone_data.get(zone_id, {})
    gis = record.get("gis", {})
    risk = record.get("risk", {})
    realtime = record.get("realtime", {})

    props = {
        "zone_id": zone_id,
        "mine_id": record.get("mine_id", "MINE-001"),
        "terrain_condition": gis.get(
            "gis_terrain_condition",
            record.get("terrain_condition", "UNKNOWN"),
        ),
        "gis_indicator": gis.get("gis_terrain_indicator"),
        "slope_indicator": gis.get("slope_indicator"),
        "roughness_indicator": gis.get("roughness_indicator"),
        "terrain_variability": gis.get("terrain_variability"),
        "elevation": gis.get("mean_elevation_m"),
        "slope": gis.get("mean_slope_deg"),
        "max_slope": gis.get("max_slope_deg"),
        "aspect": gis.get("mean_aspect_deg"),
        "curvature": gis.get("mean_curvature"),
        "roughness": gis.get("mean_roughness"),
        "road_count": gis.get("road_count"),
        "road_length": gis.get("road_length_km"),
        "risk_level": risk.get("level", "UNKNOWN"),
        "risk_probability": risk.get("probability"),
        "sensor_id": sensor_by_zone.get(zone_id),
        "telemetry_source": (
            "LIVE"
            if any(
                realtime.get(key) is not None
                for key in (
                    "displacement_mm",
                    "strain",
                    "pore_pressure_kpa",
                    "rainfall_mm",
                    "temperature_c",
                    "vibration_g",
                )
            )
            else "REFERENCE_BASELINE"
        ),
        "displacement": realtime.get(
            "displacement_mm",
            DEFAULT_BASELINE_VALUES["displacement_mm"],
        ),
        "strain": realtime.get(
            "strain",
            DEFAULT_BASELINE_VALUES["strain"],
        ),
        "pressure": realtime.get(
            "pore_pressure_kpa",
            DEFAULT_BASELINE_VALUES["pore_pressure_kpa"],
        ),
        "rainfall": realtime.get(
            "rainfall_mm",
            DEFAULT_BASELINE_VALUES["rainfall_mm"],
        ),
        "temperature": realtime.get(
            "temperature_c",
            DEFAULT_BASELINE_VALUES["temperature_c"],
        ),
        "vibration": realtime.get(
            "vibration_g",
            DEFAULT_BASELINE_VALUES["vibration_g"],
        ),
        "risk_factors": risk.get("factors", []),
        "risk_recommendation": risk.get(
            "recommended_action",
            "Continue normal monitoring.",
        ),
    }

    features.append({
        "type": "Feature",
        "geometry": zone.geometry.__geo_interface__,
        "properties": props,
    })

zone_geojson = {
    "type": "FeatureCollection",
    "features": features,
}

m = folium.Map(
    location=KUSUNDA,
    zoom_start=15,
    tiles="OpenStreetMap",
    control_scale=True,
    prefer_canvas=True,
)

study = folium.FeatureGroup(
    name="Kusunda Study Area",
    show=True,
)
folium.Polygon(
    [
        [23.7870, 86.3870],
        [23.7870, 86.4010],
        [23.7790, 86.4020],
        [23.7770, 86.3890],
    ],
    color="#111827",
    weight=3,
    fill=False,
    popup="Kusunda Mine Study Area",
).add_to(study)
study.add_to(m)

roads_layer = folium.FeatureGroup(
    name="Road Network",
    show=True,
)
road_kwargs = {
    "style_function": lambda feature: {
        "color": "#64748b",
        "weight": 2,
        "opacity": 0.7,
    }
}
if "highway" in roads.columns:
    road_kwargs["tooltip"] = folium.GeoJsonTooltip(
        fields=["highway"],
        aliases=["Road Type:"],
        localize=True,
    )
folium.GeoJson(
    roads.to_json(),
    **road_kwargs,
).add_to(roads_layer)
roads_layer.add_to(m)

zones_layer = folium.GeoJson(
    zone_geojson,
    name="AI Risk Zones",
    style_function=lambda feature: {
        "color": risk_color(
            feature["properties"].get("risk_level")
            or feature["properties"].get("terrain_condition")
        ),
        "weight": 3,
        "fillColor": risk_color(
            feature["properties"].get("risk_level")
            or feature["properties"].get("terrain_condition")
        ),
        "fillOpacity": 0.4,
    },
    highlight_function=lambda feature: {
        "weight": 5,
        "fillOpacity": 0.6,
    },
    tooltip=folium.GeoJsonTooltip(
        fields=["zone_id", "risk_level", "terrain_condition", "slope"],
        aliases=["Zone", "AI Risk", "Terrain", "Slope"],
        sticky=True,
    ),
).add_to(m)

sensor_layer = folium.FeatureGroup(
    name="IoT Sensors",
    show=True,
)

for _, sensor in sensors.iterrows():
    if sensor.geometry is None or sensor.geometry.is_empty:
        continue

    point = (
        sensor.geometry
        if sensor.geometry.geom_type == "Point"
        else sensor.geometry.representative_point()
    )

    sid = str(sensor.get("sensor_id", "SENSOR"))
    zid = str(sensor.get("zone_id", "UNKNOWN"))

    popup = f"""
    <div style="font-family:Arial;width:210px;padding:8px">
        <b style="font-size:15px">MineGuard IoT Sensor</b><br><br>
        <b>Sensor:</b> {sid}<br>
        <b>Zone:</b> {zid}<br><br>
        <span style="color:#22c7a5;font-weight:700">● Connected</span>
    </div>
    """

    folium.CircleMarker(
        [point.y, point.x],
        radius=6,
        color="#67e8f9",
        weight=2,
        fill=True,
        fill_color="#22c7a5",
        fill_opacity=0.9,
        tooltip=sid,
        popup=folium.Popup(popup, max_width=280),
    ).add_to(sensor_layer)

sensor_layer.add_to(m)

css = r"""
<style>
html,body{width:100%;height:100%;margin:0;padding:0}
#mg-header,#mg-status,#mg-search,#mg-legend,#mg-dashboard{
position:fixed;z-index:9999;font-family:Arial,sans-serif}
#mg-header{
top:16px;left:16px;padding:14px 18px;border-radius:16px;
background:rgba(7,15,28,.94);color:#e2e8f0;
border:1px solid rgba(148,163,184,.25);
box-shadow:0 12px 40px rgba(0,0,0,.25)}
#mg-title{font-size:20px;font-weight:900}
#mg-subtitle{margin-top:4px;color:#94a3b8;font-size:9px;font-weight:700;letter-spacing:1px}
#mg-status{
top:18px;right:18px;padding:9px 13px;border-radius:999px;
background:rgba(7,15,28,.94);color:#22c7a5;
border:1px solid rgba(34,199,165,.35);font-size:10px;font-weight:800}
#mg-search{left:18px;bottom:20px;width:300px}
#mg-search-inner{
display:flex;gap:7px;padding:8px;border-radius:14px;
background:rgba(7,15,28,.95);border:1px solid rgba(148,163,184,.25)}
#zone-search{
flex:1;min-width:0;border:0;outline:0;border-radius:9px;
padding:10px;background:#111c2d;color:#e2e8f0}
#zone-search::placeholder{color:#64748b}
#zone-search-button{
border:0;border-radius:9px;padding:0 13px;background:#22c7a5;
color:#06111f;font-weight:900;cursor:pointer}
#mg-legend{
right:18px;bottom:20px;width:140px;padding:12px 14px;
border-radius:14px;background:rgba(7,15,28,.95);color:#cbd5e1;
border:1px solid rgba(148,163,184,.25);font-size:10px}
.legend-title{color:#67e8f9;font-size:9px;font-weight:900;margin-bottom:8px}
.legend-item{display:flex;gap:7px;align-items:center;margin-top:6px}
.legend-color{width:22px;height:5px;border-radius:99px}
#mg-dashboard{
display:none;top:70px;right:18px;width:390px;max-height:calc(100vh - 90px);
overflow:auto;border-radius:20px;background:rgba(7,15,28,.98);
color:#e2e8f0;border:1px solid rgba(148,163,184,.25);
box-shadow:0 24px 70px rgba(0,0,0,.4)}
#mg-dashboard-header{
position:sticky;top:0;padding:18px 20px;background:#07101c;
border-bottom:1px solid rgba(148,163,184,.15)}
#mg-close{float:right;font-size:24px;cursor:pointer;color:#94a3b8}
.mg-eyebrow{color:#67e8f9;font-size:9px;font-weight:900;letter-spacing:1px}
#mg-zone{font-size:27px;font-weight:900;margin-top:4px}
#mg-mine{color:#94a3b8;font-size:11px}
#mg-body{padding:15px}
.mg-card{padding:14px;margin-bottom:12px;border-radius:15px;background:#0c1728;border:1px solid rgba(148,163,184,.13)}
.mg-label{color:#94a3b8;font-size:9px;font-weight:900;letter-spacing:.7px}
#mg-risk-row{display:flex;justify-content:space-between;align-items:end;margin-top:5px}
#mg-risk{font-size:26px;font-weight:900}
#mg-score{font-size:20px;font-weight:900}
#mg-risk-track,.mg-track{height:7px;background:#1e293b;border-radius:99px;overflow:hidden;margin-top:10px}
#mg-risk-bar,.mg-bar{height:100%;width:0;border-radius:99px;transition:width .3s}
.mg-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:10px}
.mg-metric{padding:10px;border-radius:10px;background:#111c2d;color:#94a3b8;font-size:9px;font-weight:800}
.mg-value{display:block;color:#e2e8f0;font-size:14px;margin-top:4px;font-weight:900}
.mg-indicator{margin-top:11px}
.mg-head{display:flex;justify-content:space-between;font-size:9px;font-weight:800}
.mg-sensors{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:10px}
.mg-sensor{padding:10px;border-radius:10px;background:#111c2d;color:#94a3b8;font-size:9px}
.mg-sensor b{display:block;color:#e2e8f0;font-size:14px;margin-top:4px}
#mg-factors{margin:8px 0 0;padding-left:17px;font-size:10px;line-height:1.6}
#mg-action{font-size:11px;font-weight:700;line-height:1.5;margin-top:8px}
@media(max-width:900px){
#mg-dashboard{left:10px;right:10px;width:auto;top:65px}
#mg-status,#mg-legend{display:none}
#mg-search{left:10px;right:10px;width:auto}
}
</style>
"""

ui_html = r"""
<div id="mg-header">
    <div id="mg-title">⛏ MineGuard AI</div>
    <div id="mg-subtitle">INTELLIGENT MINE SAFETY & TERRAIN INTELLIGENCE</div>
</div>

<div id="mg-status">● CONNECTING</div>

<div id="mg-search">
    <div id="mg-search-inner">
        <input id="zone-search" placeholder="Search ZONE-003" autocomplete="off">
        <button id="zone-search-button" type="button">GO</button>
    </div>
</div>

<div id="mg-legend">
    <div class="legend-title">AI RISK LEVEL</div>
    <div class="legend-item"><span class="legend-color" style="background:#ff1744"></span>Critical</div>
    <div class="legend-item"><span class="legend-color" style="background:#ff4d67"></span>High</div>
    <div class="legend-item"><span class="legend-color" style="background:#f5b942"></span>Moderate</div>
    <div class="legend-item"><span class="legend-color" style="background:#22c7a5"></span>Low</div>
</div>

<div id="mg-dashboard">
    <div id="mg-dashboard-header">
        <span id="mg-close" onclick="closeZoneDashboard()">×</span>
        <div class="mg-eyebrow">MINE SAFETY INTELLIGENCE</div>
        <div id="mg-zone">ZONE</div>
        <div id="mg-mine">MINE-001</div>
    </div>

    <div id="mg-body">
        <div class="mg-card">
            <div class="mg-label">LIVE AI RISK ASSESSMENT</div>
            <div id="mg-risk-row">
                <div id="mg-risk">UNKNOWN</div>
                <div id="mg-score">—</div>
            </div>
            <div id="mg-risk-track"><div id="mg-risk-bar"></div></div>
        </div>

        <div class="mg-card">
            <div class="mg-label">TERRAIN PROFILE</div>
            <div class="mg-grid">
                <div class="mg-metric">Elevation<span id="m-elevation" class="mg-value">—</span></div>
                <div class="mg-metric">Slope<span id="m-slope" class="mg-value">—</span></div>
                <div class="mg-metric">Max Slope<span id="m-max-slope" class="mg-value">—</span></div>
                <div class="mg-metric">Aspect<span id="m-aspect" class="mg-value">—</span></div>
                <div class="mg-metric">Roughness<span id="m-roughness" class="mg-value">—</span></div>
                <div class="mg-metric">Curvature<span id="m-curvature" class="mg-value">—</span></div>
                <div class="mg-metric">Roads<span id="m-roads" class="mg-value">—</span></div>
                <div class="mg-metric">Road Length<span id="m-road-length" class="mg-value">—</span></div>
            </div>
        </div>

        <div class="mg-card">
            <div class="mg-label">GIS RISK INDICATORS</div>
            <div class="mg-indicator"><div class="mg-head"><span>Slope</span><span id="i-slope">—</span></div><div class="mg-track"><div id="b-slope" class="mg-bar"></div></div></div>
            <div class="mg-indicator"><div class="mg-head"><span>Roughness</span><span id="i-roughness">—</span></div><div class="mg-track"><div id="b-roughness" class="mg-bar"></div></div></div>
            <div class="mg-indicator"><div class="mg-head"><span>Terrain Variability</span><span id="i-variability">—</span></div><div class="mg-track"><div id="b-variability" class="mg-bar"></div></div></div>
            <div class="mg-indicator"><div class="mg-head"><span>GIS Indicator</span><span id="i-gis">—</span></div><div class="mg-track"><div id="b-gis" class="mg-bar"></div></div></div>
        </div>

        <div class="mg-card">
            <div class="mg-label">SENSOR TELEMETRY</div>
            <div id="mg-telemetry-source" style="margin-top:6px;color:#94a3b8;font-size:9px;font-weight:800;">REFERENCE BASELINE</div>
            <div class="mg-sensors">
                <div class="mg-sensor">Displacement<b id="s-displacement">—</b></div>
                <div class="mg-sensor">Strain<b id="s-strain">—</b></div>
                <div class="mg-sensor">Pore Pressure<b id="s-pressure">—</b></div>
                <div class="mg-sensor">Rainfall<b id="s-rainfall">—</b></div>
                <div class="mg-sensor">Temperature<b id="s-temperature">—</b></div>
                <div class="mg-sensor">Vibration<b id="s-vibration">—</b></div>
            </div>
        </div>

        <div class="mg-card">
            <div class="mg-label">WHY THIS ZONE IS AT RISK</div>
            <ul id="mg-factors"><li>Waiting for AI analysis.</li></ul>
        </div>

        <div class="mg-card">
            <div class="mg-label">RECOMMENDED ACTION</div>
            <div id="mg-action">Continue normal monitoring.</div>
        </div>
    </div>
</div>
"""

m.get_root().html.add_child(folium.Element(css))
m.get_root().html.add_child(folium.Element(ui_html))

map_name = m.get_name()
zone_name = zones_layer.get_name()

js = r"""
<script>
(function () {
    "use strict";

    const API_BASE = "http://localhost:8000/api/v1";
    const MAP_NAME = "__MAP_NAME__";
    const ZONE_NAME = "__ZONE_NAME__";

    let mapInstance = null;
    let zoneLayer = null;
    let selectedZone = null;

    function runtime(name) {
        try {
            return window[name];
        } catch (e) {
            return null;
        }
    }

    function text(id, value) {
        const e = document.getElementById(id);
        if (e) e.textContent = value;
    }

    function num(value, digits) {
        const n = Number(value);
        return Number.isFinite(n)
            ? n.toFixed(digits === undefined ? 2 : digits)
            : "—";
    }

    function pct(value) {
        const n = Number(value);
        if (!Number.isFinite(n)) return "—";
        return (Math.max(0, Math.min(1, n)) * 100).toFixed(1) + "%";
    }

    function color(level) {
        level = String(level || "").toUpperCase();
        if (level === "CRITICAL") return "#ff1744";
        if (level === "HIGH") return "#ff4d67";
        if (level === "MODERATE") return "#f5b942";
        if (level === "LOW") return "#22c7a5";
        return "#94a3b8";
    }

    function bar(id, value) {
        const e = document.getElementById(id);
        if (!e) return;
        let n = Number(value);
        if (!Number.isFinite(n)) n = 0;
        n = Math.max(0, Math.min(1, n));
        e.style.width = (n * 100) + "%";
        e.style.background = "#22c7a5";
    }

    function factors(items) {
        const list = document.getElementById("mg-factors");
        if (!list) return;
        list.innerHTML = "";

        if (!Array.isArray(items) || items.length === 0) {
            const li = document.createElement("li");
            li.textContent = "No significant risk factors detected.";
            list.appendChild(li);
            return;
        }

        items.forEach(function (item) {
            const li = document.createElement("li");
            if (item && typeof item === "object") {
                li.textContent =
                    String(item.feature || "Risk factor") +
                    " — " +
                    String(item.impact || "DETECTED");
            } else {
                li.textContent = String(item);
            }
            list.appendChild(li);
        });
    }

    function showZone(p) {
        if (!p) return;

        selectedZone = String(p.zone_id || "").toUpperCase();

        document.getElementById("mg-dashboard").style.display = "block";

        text("mg-zone", p.zone_id || "ZONE");
        text("mg-mine", p.mine_id || "MINE-001");

        text(
            "mg-telemetry-source",
            p.telemetry_source === "LIVE"
                ? "● LIVE BACKEND TELEMETRY"
                : "REFERENCE BASELINE • NO LIVE READING"
        );

        const source =
            document.getElementById("mg-telemetry-source");

        if (source) {
            source.style.color =
                p.telemetry_source === "LIVE"
                    ? "#22c7a5"
                    : "#94a3b8";
        }

        const level = String(
            p.risk_level || p.terrain_condition || "UNKNOWN"
        ).toUpperCase();

        text("mg-risk", level);

        const risk = document.getElementById("mg-risk");
        if (risk) risk.style.color = color(level);

        let probability = Number(p.risk_probability);
        if (Number.isFinite(probability) && probability <= 1) probability *= 100;

        text(
            "mg-score",
            Number.isFinite(probability) ? probability.toFixed(1) + "%" : "—"
        );

        const riskBar = document.getElementById("mg-risk-bar");
        if (riskBar) {
            riskBar.style.width =
                (Number.isFinite(probability) ? Math.max(0, Math.min(100, probability)) : 0) + "%";
            riskBar.style.background = color(level);
        }

        text("m-elevation", num(p.elevation) + " m");
        text("m-slope", num(p.slope) + "°");
        text("m-max-slope", num(p.max_slope) + "°");
        text("m-aspect", num(p.aspect) + "°");
        text("m-roughness", num(p.roughness));
        text("m-curvature", num(p.curvature, 4));
        text("m-roads", p.road_count == null ? "—" : String(p.road_count));
        text("m-road-length", num(p.road_length, 3) + " km");

        text("i-slope", pct(p.slope_indicator));
        text("i-roughness", pct(p.roughness_indicator));
        text("i-variability", pct(p.terrain_variability));
        text("i-gis", pct(p.gis_indicator));

        bar("b-slope", p.slope_indicator);
        bar("b-roughness", p.roughness_indicator);
        bar("b-variability", p.terrain_variability);
        bar("b-gis", p.gis_indicator);

        text("s-displacement", num(p.displacement) + " mm");
        text("s-strain", num(p.strain));
        text("s-pressure", num(p.pressure) + " kPa");
        text("s-rainfall", num(p.rainfall) + " mm");
        text("s-temperature", num(p.temperature) + " °C");
        text("s-vibration", num(p.vibration) + " g");

        factors(p.risk_factors || []);
        text(
            "mg-action",
            p.risk_recommendation || "Continue normal monitoring."
        );
    }

    window.closeZoneDashboard = function () {
        const d = document.getElementById("mg-dashboard");
        if (d) d.style.display = "none";
        selectedZone = null;
    };

    function openLayer(layer) {
        if (!layer || !layer.feature || !layer.feature.properties) return;

        selectedZone = String(
            layer.feature.properties.zone_id || ""
        ).toUpperCase();

        showZone(layer.feature.properties);

        if (mapInstance && layer.getBounds) {
            mapInstance.fitBounds(
                layer.getBounds(),
                { padding: [70, 430, 70, 70], maxZoom: 16 }
            );
        }
    }

    function getSelectedZoneProperties() {
        if (!zoneLayer || !selectedZone) return null;

        let result = null;

        zoneLayer.eachLayer(function (layer) {
            if (
                result ||
                !layer.feature ||
                !layer.feature.properties
            ) {
                return;
            }

            const id = String(
                layer.feature.properties.zone_id || ""
            ).toUpperCase();

            if (id === selectedZone) {
                result = layer.feature.properties;
            }
        });

        return result;
    }

    function attachZones() {
        if (!zoneLayer) return;

        zoneLayer.eachLayer(function (layer) {
            layer.off("click");
            layer.on("click", function () {
                openLayer(layer);
            });
        });
    }

    function searchZone() {
        if (!zoneLayer) return;

        const input = document.getElementById("zone-search");
        if (!input) return;

        let q = input.value.trim().toUpperCase();
        if (!q) return;

        if (!q.startsWith("ZONE-")) q = "ZONE-" + q;

        let found = false;

        zoneLayer.eachLayer(function (layer) {
            if (!layer.feature || !layer.feature.properties) return;

            const id = String(
                layer.feature.properties.zone_id || ""
            ).toUpperCase();

            if (id === q) {
                found = true;
                openLayer(layer);
            }
        });

        if (!found) {
            window.alert("Zone " + q + " was not found.");
        }
    }

    window.searchZone = searchZone;

    function setLiveRisk(zoneId, level, score) {
        if (!zoneLayer) return;

        zoneLayer.eachLayer(function (layer) {
            if (!layer.feature || !layer.feature.properties) return;

            const p = layer.feature.properties;
            const id = String(p.zone_id || "").toUpperCase();

            if (id !== String(zoneId || "").toUpperCase()) return;

            p.risk_level = level;
            p.risk_probability = Number(score) / 100;

            const c = color(level);
            layer.setStyle({
                color: c,
                fillColor: c,
                weight: 3,
                fillOpacity: 0.42
            });
        });
    }

    async function getJSON(url) {
        const r = await fetch(url, { cache: "no-store" });
        if (!r.ok) throw new Error("HTTP " + r.status);
        return r.json();
    }

    async function liveUpdate() {
        let sensor = null;
        let risk = null;
        let alerts = null;

        try {
            sensor = await getJSON(
                API_BASE + "/sensors/latest"
            );
        } catch (error) {
            console.error("Sensor API error:", error);
        }

        try {
            risk = await getJSON(
                API_BASE + "/risk/latest"
            );
        } catch (error) {
            console.error("Risk API error:", error);
        }

        try {
            alerts = await getJSON(
                API_BASE + "/alerts/history"
            );
        } catch (error) {
            console.warn("Alerts API error:", error);
        }

        if (!sensor && !risk) {
            text("mg-status", "● BACKEND OFFLINE");

            const status =
                document.getElementById("mg-status");

            if (status) {
                status.style.color = "#ff4d67";
            }

            return;
        }

        text("mg-status", "● BACKEND ONLINE • LIVE");

        const status =
            document.getElementById("mg-status");

        if (status) {
            status.style.color = "#22c7a5";
        }

        if (risk) {
            setLiveRisk(
                risk.zone_id,
                risk.risk_level,
                risk.risk_score
            );
        }

        /*
         * Only the zone returned by the live sensor endpoint is
         * upgraded from REFERENCE_BASELINE to LIVE.
         *
         * Every other zone keeps its own complete GIS data and
         * baseline sensor values.
         */
        if (
            sensor &&
            sensor.sensors &&
            selectedZone &&
            selectedZone ===
                String(sensor.zone_id || "").toUpperCase()
        ) {
            const base =
                getSelectedZoneProperties() || {};

            const s = sensor.sensors;

            const merged =
                Object.assign(
                    {},
                    base,
                    {
                        zone_id:
                            sensor.zone_id ||
                            base.zone_id,

                        mine_id:
                            sensor.mine_id ||
                            base.mine_id,

                        sensor_id:
                            sensor.sensor_id ||
                            base.sensor_id,

                        telemetry_source:
                            "LIVE",

                        displacement:
                            s.displacement_mm,

                        strain:
                            s.strain,

                        pressure:
                            s.pore_pressure_kpa,

                        rainfall:
                            s.rainfall_mm,

                        temperature:
                            s.temperature_c,

                        vibration:
                            s.vibration_g
                    }
                );

            if (risk) {
                merged.risk_level =
                    risk.risk_level;

                merged.risk_probability =
                    Number(risk.risk_score) / 100;

                merged.risk_factors =
                    risk.factors ||
                    merged.risk_factors ||
                    [];

                merged.risk_recommendation =
                    risk.recommended_action ||
                    merged.risk_recommendation;
            }

            showZone(merged);
        }

        if (
            risk &&
            selectedZone &&
            selectedZone ===
                String(risk.zone_id || "").toUpperCase()
        ) {
            const current =
                getSelectedZoneProperties();

            if (current) {
                current.risk_level =
                    risk.risk_level;

                current.risk_probability =
                    Number(risk.risk_score) / 100;

                current.risk_factors =
                    risk.factors ||
                    current.risk_factors ||
                    [];

                current.risk_recommendation =
                    risk.recommended_action ||
                    current.risk_recommendation;

                current.telemetry_source =
                    "LIVE";
            }
        }

        if (
            selectedZone &&
            Array.isArray(alerts) &&
            alerts.length > 0
        ) {
            const alert = alerts[0];

            if (
                String(alert.zone_id || "").toUpperCase() ===
                selectedZone
            ) {
                factors(
                    alert.factors || []
                );

                text(
                    "mg-action",
                    alert.recommended_action ||
                    "Follow the latest safety instructions."
                );
            }
        }
    }

    function initialize() {
        mapInstance = runtime(MAP_NAME);
        zoneLayer = runtime(ZONE_NAME);

        if (!mapInstance || !zoneLayer) return false;

        attachZones();

        const input = document.getElementById("zone-search");
        const button = document.getElementById("zone-search-button");

        if (input) {
            input.addEventListener("keydown", function (event) {
                if (event.key === "Enter") {
                    event.preventDefault();
                    searchZone();
                }
            });
        }

        if (button) button.addEventListener("click", searchZone);

        liveUpdate();
        window.setInterval(liveUpdate, 3000);

        return true;
    }

    window.addEventListener("load", function () {
        let tries = 0;

        const timer = window.setInterval(function () {
            tries += 1;

            if (initialize()) {
                window.clearInterval(timer);
                return;
            }

            if (tries >= 40) {
                window.clearInterval(timer);
                console.error("MineGuard map initialization timed out.");
            }
        }, 250);
    });

})();
</script>
"""

js = (
    js
    .replace("__MAP_NAME__", map_name)
    .replace("__ZONE_NAME__", zone_name)
)

m.get_root().html.add_child(folium.Element(js))

folium.LayerControl(collapsed=False).add_to(m)

m.save(OUTPUT_FILE)

print()
print("==========================================")
print("MINEGUARD AI MAP CREATED SUCCESSFULLY")
print("==========================================")
print(f"Zones integrated: {len(features)}")
print(f"Sensors integrated: {len(sensors)}")
print(f"Output: {OUTPUT_FILE}")
print("Backend integration: ENABLED")
print("IoT telemetry: ENABLED")
print("AI risk: ENABLED")
print("Alerts: ENABLED")
print("Zone search: ENABLED")
print("==========================================")