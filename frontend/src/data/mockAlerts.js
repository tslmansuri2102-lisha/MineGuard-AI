/**
 * Mock Alerts Data Layer
 * Comprehensive geotechnical alert repository with response protocols and action plans.
 */

export const MOCK_ALERTS = [
  {
    id: "ALT-2026-089",
    severity: "CRITICAL",
    title: "Critical Rockfall Hazard Detected",
    zoneId: "Zone A-03",
    zoneName: "East Highwall Face (Bench 04-06)",
    time: "2 mins ago",
    timestamp: "2026-08-17 13:34:10",
    status: "ACTIVE",
    category: "Slope Failure Precursor",
    readings: {
      displacement: "4.85 mm (+1.15 mm/hr)",
      vibration: "14.2 mm/s",
      porePressure: "215 kPa",
      fos: "1.08 FoS"
    },
    description: "Accelerated planar shear dilation observed along the joint set strike. High pore pressure saturation following 26.5mm rainfall event has critically reduced highwall shear resistance.",
    recommendedResponse: "IMMEDIATE EVACUATION: Sound Level-3 Pit siren. Clear all personnel and haul trucks from Bench L4-L6 floor within 150m blast zone radius. Lock down Ramp Corridor E.",
    actionPlan: [
      { step: "Trigger emergency siren in East Highwall sector", completed: true },
      { step: "Halt Caterpillar 797F haul fleet in East Ramp access", completed: true },
      { step: "Evacuate survey team & drilling crew from Bench L5", completed: false },
      { step: "Deploy automated UAV LiDAR scanner for contour verification", completed: false },
      { step: "Engage dewatering sump pump override in Sector Central", completed: false }
    ],
    author: "AI Rockfall Early Warning Model (v2.4-Ensemble)",
    confidence: "94.2%"
  },
  {
    id: "ALT-2026-088",
    severity: "HIGH",
    title: "Abnormal Ground Vibration & Rapid Creep",
    zoneId: "Zone B-02",
    zoneName: "South-West Transition Bench (Bench 03-05)",
    time: "14 mins ago",
    timestamp: "2026-08-17 13:22:04",
    status: "ACTIVE",
    category: "Micro-seismic Anomaly",
    readings: {
      vibration: "12.4 mm/s",
      displacement: "3.20 mm",
      porePressure: "165 kPa",
      fos: "1.18 FoS"
    },
    description: "Repeated high-amplitude micro-seismic bursts registered by triaxial geophone VIB-SW01. Tensile stress concentration detected along bedding planes.",
    recommendedResponse: "Impose 15 km/h speed restriction on Haul Ramp 2. Dispatch geotechnical inspector with thermal camera to inspect crest fracture SW-03.",
    actionPlan: [
      { step: "Notify pit superintendent and traffic dispatch", completed: true },
      { step: "Reduce haul truck payload & transit speeds", completed: false },
      { step: "Conduct visual geotechnical prism survey", completed: false }
    ],
    author: "Geotechnical Waveform Classifier",
    confidence: "88.6%"
  },
  {
    id: "ALT-2026-087",
    severity: "MODERATE",
    title: "Precipitation Infiltration & Pore Pressure Surge",
    zoneId: "Zone C-01",
    zoneName: "South Catchment Wall (Bench 01-03)",
    time: "32 mins ago",
    timestamp: "2026-08-17 13:04:18",
    status: "ACKNOWLEDGED",
    category: "Hydrological Saturation",
    readings: {
      rainfall: "26.5 mm/h",
      porePressure: "185 kPa",
      displacement: "1.90 mm",
      fos: "1.32 FoS"
    },
    description: "Monsoon storm runoff surpassing ditch catchment capacity. Vibrating wire piezometer shows hydrostatic pressure gradient rising above threshold.",
    recommendedResponse: "Verify ditch culvert clearance and verify auxiliary submersible pump activation on Bench 2 catch berm.",
    actionPlan: [
      { step: "Inspect ditch culverts for debris blockage", completed: true },
      { step: "Start backup diesel pump at Sump S-03", completed: true }
    ],
    author: "Hydrological Saturation Model",
    confidence: "82.0%"
  },
  {
    id: "ALT-2026-086",
    severity: "MODERATE",
    title: "Elevated Vibration from Secondary Blasting",
    zoneId: "Zone A-02",
    zoneName: "North-East Haul Ramp (Bench 02-04)",
    time: "1 hour ago",
    timestamp: "2026-08-17 12:35:50",
    status: "ACKNOWLEDGED",
    category: "Vibration Threshold",
    readings: {
      vibration: "9.8 mm/s",
      displacement: "1.45 mm",
      porePressure: "110 kPa",
      fos: "1.41 FoS"
    },
    description: "Post-blast transient peak particle velocity exceeded 8.0 mm/s limit. Structural integrity of retaining wire mesh remains intact.",
    recommendedResponse: "Log blast delay sequence and cross-reference with seismic attenuation curves.",
    actionPlan: [
      { step: "Cross-check blast design report with seismic record", completed: true }
    ],
    author: "Blasting Impact Monitor",
    confidence: "91.5%"
  },
  {
    id: "ALT-2026-085",
    severity: "LOW",
    title: "Sensor Node S-04 Battery Depleted",
    zoneId: "Zone B-01",
    zoneName: "Central Pit Floor & Sump",
    time: "3 hours ago",
    timestamp: "2026-08-17 10:15:22",
    status: "RESOLVED",
    category: "Hardware Telemetry",
    readings: {
      battery: "14%",
      voltage: "3.2V",
      signal: "-92 dBm"
    },
    description: "Solar battery backup on telemetry repeater node dropped below 15%. Scheduled maintenance replaced power cell.",
    recommendedResponse: "Resolved - solar panel cleaned and new LiFePO4 battery pack installed.",
    actionPlan: [
      { step: "Dispatch electrical instrumentation team", completed: true },
      { step: "Recalibrate signal receiver", completed: true }
    ],
    author: "Hardware Health Watchdog",
    confidence: "99.0%"
  }
];
