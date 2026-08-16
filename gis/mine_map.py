import folium

KUSUNDA = [23.7822, 86.3933]

mine_map = folium.Map(
    location=KUSUNDA,
    zoom_start=14,
    tiles="OpenStreetMap"
)

# --------------------------------------------------
# KUSUNDA STUDY AREA
# --------------------------------------------------

study_area = [
    [23.7870, 86.3870],
    [23.7870, 86.4010],
    [23.7790, 86.4020],
    [23.7770, 86.3890]
]

folium.Polygon(
    locations=study_area,
    color="black",
    weight=3,
    fill=False,
    popup="Kusunda Study Area"
).add_to(mine_map)


# --------------------------------------------------
# MINING ZONES
# --------------------------------------------------

zones = [
    {
        "name": "Zone A - Low Risk",
        "risk": "LOW",
        "color": "green",
        "coordinates": [
            [23.7865, 86.3875],
            [23.7865, 86.3935],
            [23.7820, 86.3940],
            [23.7810, 86.3885]
        ]
    },
    {
        "name": "Zone B - Medium Risk",
        "risk": "MEDIUM",
        "color": "orange",
        "coordinates": [
            [23.7865, 86.3935],
            [23.7865, 86.4005],
            [23.7815, 86.4010],
            [23.7820, 86.3940]
        ]
    },
    {
        "name": "Zone C - High Risk",
        "risk": "HIGH",
        "color": "red",
        "coordinates": [
            [23.7810, 86.3885],
            [23.7820, 86.3940],
            [23.7775, 86.3970],
            [23.7775, 86.3900]
        ]
    }
]

for zone in zones:
    folium.Polygon(
        locations=zone["coordinates"],
        color=zone["color"],
        fill=True,
        fill_color=zone["color"],
        fill_opacity=0.35,
        popup=f'{zone["name"]} | Risk: {zone["risk"]}'
    ).add_to(mine_map)


# --------------------------------------------------
# SENSOR LOCATIONS
# These are prototype locations for the software stage.
# --------------------------------------------------

sensors = [
    {
        "id": "SENSOR-01",
        "lat": 23.7845,
        "lon": 86.3905,
        "type": "Environmental",
        "parameters": "Temperature, Humidity, Rainfall"
    },
    {
        "id": "SENSOR-02",
        "lat": 23.7830,
        "lon": 86.3960,
        "type": "Ground Movement",
        "parameters": "Displacement, Vibration"
    },
    {
        "id": "SENSOR-03",
        "lat": 23.7795,
        "lon": 86.3935,
        "type": "Gas Monitoring",
        "parameters": "CO, CO2, CH4"
    },
    {
        "id": "SENSOR-04",
        "lat": 23.7850,
        "lon": 86.3990,
        "type": "Environmental",
        "parameters": "Temperature, Humidity"
    }
]

sensor_layer = folium.FeatureGroup(name="Sensor Locations")

for sensor in sensors:
    popup = f"""
    <b>{sensor["id"]}</b><br>
    Type: {sensor["type"]}<br>
    Parameters: {sensor["parameters"]}
    """

    folium.Marker(
        location=[sensor["lat"], sensor["lon"]],
        popup=popup,
        tooltip=sensor["id"],
        icon=folium.Icon(icon="info-sign")
    ).add_to(sensor_layer)

sensor_layer.add_to(mine_map)


# --------------------------------------------------
# GAS MONITORING ZONE
# Prototype layer - not live measurements.
# --------------------------------------------------

gas_zone = [
    [23.7815, 86.3910],
    [23.7815, 86.3955],
    [23.7780, 86.3965],
    [23.7775, 86.3920]
]

folium.Polygon(
    locations=gas_zone,
    color="purple",
    fill=True,
    fill_color="purple",
    fill_opacity=0.25,
    popup="Gas Monitoring Zone - Prototype"
).add_to(mine_map)


# --------------------------------------------------
# FIRE / THERMAL RISK ZONE
# Prototype layer for later satellite/fire data.
# --------------------------------------------------

fire_zone = [
    [23.7840, 86.3970],
    [23.7855, 86.4000],
    [23.7815, 86.4010],
    [23.7805, 86.3980]
]

folium.Polygon(
    locations=fire_zone,
    color="darkred",
    fill=True,
    fill_color="red",
    fill_opacity=0.30,
    popup="Potential Fire/Thermal Risk Zone - Prototype"
).add_to(mine_map)


# --------------------------------------------------
# RESTRICTED AREA
# --------------------------------------------------

restricted_area = [
    [23.7790, 86.3970],
    [23.7810, 86.4005],
    [23.7780, 86.4020],
    [23.7765, 86.3990]
]

folium.Polygon(
    locations=restricted_area,
    color="black",
    fill=True,
    fill_color="black",
    fill_opacity=0.45,
    popup="Restricted Area - Prototype"
).add_to(mine_map)


# --------------------------------------------------
# MAP LEGEND
# --------------------------------------------------

legend = """
<div style="
position: fixed;
bottom: 30px;
left: 30px;
width: 220px;
background-color: white;
border: 2px solid grey;
z-index: 9999;
padding: 12px;
font-size: 14px;
">

<b>Jharia Mine Risk Map</b><br><br>

<span style="color:green;">■</span>
Low Risk<br>

<span style="color:orange;">■</span>
Medium Risk<br>

<span style="color:red;">■</span>
High Risk<br>

<span style="color:purple;">■</span>
Gas Monitoring<br>

<span style="color:darkred;">■</span>
Fire/Thermal Risk<br>

<span style="color:black;">■</span>
Restricted Area<br>

📍 Sensor Location

</div>
"""

mine_map.get_root().html.add_child(
    folium.Element(legend)
)


# --------------------------------------------------
# LAYER CONTROL
# --------------------------------------------------

folium.LayerControl().add_to(mine_map)


# --------------------------------------------------
# SAVE MAP
# --------------------------------------------------

mine_map.save("mine_map.html")

print("Jharia/Kusunda GIS map created successfully.")
print("Open mine_map.html in your browser.")