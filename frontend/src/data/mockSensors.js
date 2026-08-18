/**
 * Mock Geotechnical Sensor Fleet Data
 */

export const MOCK_SENSORS = [
  {
    id: "DISP-E01",
    type: "Borehole Extensometer (MPBX)",
    zone: "Zone A-03",
    location: "Bench L5 East Crest (Ch 450)",
    reading: "4.85 mm",
    readingType: "Displacement",
    status: "CRITICAL_ALERT",
    battery: "92%",
    signalStrength: "-68 dBm (Strong)",
    samplingInterval: "1.0 sec",
    lastCalibrated: "2026-07-20",
    health: 98
  },
  {
    id: "VIB-E04",
    type: "Triaxial Geophone Seismograph",
    zone: "Zone A-03",
    location: "Bench L4 Toe Anchor",
    reading: "14.2 mm/s",
    readingType: "Vibration PPV",
    status: "WARNING",
    battery: "84%",
    signalStrength: "-72 dBm (Good)",
    samplingInterval: "0.2 sec",
    lastCalibrated: "2026-08-02",
    health: 96
  },
  {
    id: "PIEZ-E02",
    type: "Vibrating Wire Piezometer",
    zone: "Zone A-03",
    location: "Sub-Bench 5 Borehole (Depth 35m)",
    reading: "215 kPa",
    readingType: "Pore Pressure",
    status: "CRITICAL_ALERT",
    battery: "89%",
    signalStrength: "-74 dBm (Good)",
    samplingInterval: "5.0 sec",
    lastCalibrated: "2026-07-15",
    health: 94
  },
  {
    id: "RADAR-01",
    type: "Real-time Slope Stability Radar (SSR)",
    zone: "Zone A-03 / Sector East",
    location: "West Rim Overlook Tower",
    reading: "3.8 mm/hr rate",
    readingType: "Radar Interferometry",
    status: "CRITICAL_ALERT",
    battery: "Grid Powered (100%)",
    signalStrength: "Fiber Optic Link",
    samplingInterval: "Continuous (60s scan)",
    lastCalibrated: "2026-08-10",
    health: 100
  },
  {
    id: "VIB-SW01",
    type: "Triaxial Seismograph",
    zone: "Zone B-02",
    location: "Ramp 2 Switchback Berm",
    reading: "12.4 mm/s",
    readingType: "Vibration PPV",
    status: "WARNING",
    battery: "76%",
    signalStrength: "-81 dBm (Fair)",
    samplingInterval: "0.5 sec",
    lastCalibrated: "2026-06-18",
    health: 91
  },
  {
    id: "DISP-SW03",
    type: "Multipoint Extensometer",
    zone: "Zone B-02",
    location: "Bench L3 Crest",
    reading: "3.20 mm",
    readingType: "Displacement",
    status: "WARNING",
    battery: "88%",
    signalStrength: "-70 dBm (Good)",
    samplingInterval: "2.0 sec",
    lastCalibrated: "2026-07-28",
    health: 95
  },
  {
    id: "RAIN-01",
    type: "Optical Precipitation Gauge",
    zone: "Zone A-01",
    location: "North Rim Weather Mast",
    reading: "26.5 mm/h",
    readingType: "Rainfall",
    status: "ACTIVE",
    battery: "95%",
    signalStrength: "-65 dBm (Strong)",
    samplingInterval: "10.0 sec",
    lastCalibrated: "2026-08-01",
    health: 99
  },
  {
    id: "INCL-02",
    type: "In-Place Inclinometer String (IPI)",
    zone: "Zone B-02",
    location: "Borehole SW-09 (Depth 50m)",
    reading: "0.42° tilt",
    readingType: "Angular Deflection",
    status: "WARNING",
    battery: "82%",
    signalStrength: "-76 dBm (Good)",
    samplingInterval: "5.0 sec",
    lastCalibrated: "2026-07-10",
    health: 93
  }
];
