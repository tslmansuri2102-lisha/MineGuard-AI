/**
 * Mock System Status and Infrastructure Health Architecture
 */

export const MOCK_SYSTEM_STATUS = {
  environment: "STANDALONE DEMO ENVIRONMENT",
  overallHealth: "DEMO SIMULATION RUNNING",
  uptime: "99.98% (Demo)",
  lastSync: "Just now",
  connectedNodes: 12,
  activeAlertTriggers: 3,
  systemComponents: [
    {
      id: "comp-frontend",
      name: "MineGuard Web Command Center",
      type: "User Interface / SPA",
      status: "ONLINE",
      version: "v1.0.0-PROD",
      latency: "4 ms",
      description: "React 18 + Vite client running in local browser context.",
      mode: "STANDALONE"
    },
    {
      id: "comp-api",
      name: "MineGuard Core REST API Gateway",
      type: "API Gateway Service",
      status: "DEMO",
      version: "v2.4.0 (Mock Fallback)",
      latency: "12 ms (Simulated)",
      description: "Prepared for VITE_API_BASE_URL connection. Operating in mock fallback mode.",
      mode: "MOCK LAYER"
    },
    {
      id: "comp-ws",
      name: "High-Frequency Telemetry WebSocket Streamer",
      type: "Real-time Event Broker",
      status: "ONLINE",
      version: "v2.1.2 (Virtual Engine)",
      latency: "18 ms",
      description: "Browser-side dynamic geotechnical telemetry physics simulation engine.",
      mode: "SIMULATED"
    },
    {
      id: "comp-ml",
      name: "Geotechnical Rockfall ML Inference Engine",
      type: "AI / Inference Node",
      status: "DEMO",
      version: "GNN-XGB v2.4.1",
      latency: "38 ms",
      description: "Spatio-Temporal Graph Neural Network prediction pipeline for slope failure forecasting.",
      mode: "DEMO AI"
    },
    {
      id: "comp-risk",
      name: "Geotechnical Limit Equilibrium Risk Engine",
      type: "Safety Calculation Engine",
      status: "DEMO",
      version: "Bishop-Janbu FoS v3.0",
      latency: "22 ms",
      description: "Real-time Factor of Safety (FoS) & Rock Mass Rating (RMR) calculation module.",
      mode: "DEMO CALC"
    },
    {
      id: "comp-alerts",
      name: "Multi-Channel Alert & Siren Dispatcher",
      type: "Safety Warning Service",
      status: "DEMO",
      version: "Audio/Visual Alert v1.8",
      latency: "8 ms",
      description: "Automated pit-wide sirens, SMS dispatch, and control room alarm signaling.",
      mode: "DEMO READY"
    },
    {
      id: "comp-gis",
      name: "Open-Pit Topographic GIS & Terrain Engine",
      type: "Spatial Mapping Engine",
      status: "ONLINE",
      version: "Vector GeoMap v2.0",
      latency: "2 ms",
      description: "High-contrast vector mine coordinate layout with bench and hazard zone polygons.",
      mode: "LOCAL SVG"
    },
    {
      id: "comp-iot",
      name: "Sensor Fleet Telemetry Ingest (MQTT/Modbus)",
      type: "Field Ingest Broker",
      status: "DEMO",
      version: "MQTT Ingest v4.2",
      latency: "15 ms",
      description: "Simulating 12 active field geotechnical instruments across 7 pit benches.",
      mode: "SIMULATED FLEET"
    }
  ]
};
