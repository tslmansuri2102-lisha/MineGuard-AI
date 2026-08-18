import React, { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react';
import { MOCK_ZONES } from '../data/mockZones';
import { INITIAL_LIVE_TELEMETRY, MOCK_TELEMETRY_HISTORY_24H, generateHistorySeries } from '../data/mockTelemetry';
import { MOCK_ALERTS } from '../data/mockAlerts';
import { MOCK_CURRENT_PREDICTION, MOCK_RISK_FACTORS, MOCK_PREDICTION_HISTORY } from '../data/mockPredictions';
import { MOCK_SENSORS } from '../data/mockSensors';
import { MOCK_SYSTEM_STATUS } from '../data/mockSystemStatus';

const MineGuardContext = createContext(null);

export function MineGuardProvider({ children }) {
  // Navigation
  const [currentTab, setCurrentTab] = useState('overview');

  // Core Geotechnical & Risk States
  const [currentRisk, setCurrentRisk] = useState(MOCK_CURRENT_PREDICTION);
  const [liveTelemetry, setLiveTelemetry] = useState(INITIAL_LIVE_TELEMETRY);
  const [telemetryHistory, setTelemetryHistory] = useState(MOCK_TELEMETRY_HISTORY_24H);
  const [zones, setZones] = useState(MOCK_ZONES);
  const [selectedZone, setSelectedZone] = useState(null);
  
  // Alerts
  const [alerts, setAlerts] = useState(MOCK_ALERTS);
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [unreadAlertCount, setUnreadAlertCount] = useState(2);
  const [activeAlarmTriggered, setActiveAlarmTriggered] = useState(true);

  // Simulation & Demo Controls
  const [isDemoMode, setIsDemoMode] = useState(true);
  const [isStreaming, setIsStreaming] = useState(true);
  const [streamSpeed, setStreamSpeed] = useState(1); // 1x, 2x, 5x
  const [activeScenario, setActiveScenario] = useState('rockfall_hazard'); // 'normal' | 'storm' | 'microseismic' | 'rockfall_hazard'
  const [lastUpdateTime, setLastUpdateTime] = useState(new Date().toLocaleTimeString());

  // Sensors & System Health
  const [sensors, setSensors] = useState(MOCK_SENSORS);
  const [systemStatus, setSystemStatus] = useState(MOCK_SYSTEM_STATUS);

  // Settings & Customization
  const [settings, setSettings] = useState({
    theme: 'graphite', // 'graphite' | 'midnight' | 'tactical'
    refreshRate: 2000,
    audioAlerts: false,
    autoEvacProtocol: true,
    showHeatmap: true,
    showSensorsOnMap: true,
    showHaulRoads: true,
    vibrationThreshold: 8.0,
    rainfallThreshold: 20.0,
    displacementThreshold: 3.5,
    porePressureThreshold: 160.0,
    apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'
  });

  // Keep a ref for history to avoid stale state in interval
  const historyRef = useRef(telemetryHistory);
  historyRef.current = telemetryHistory;

  // Real-time micro-fluctuation simulation loop
  useEffect(() => {
    if (!isStreaming || !isDemoMode) return;

    const interval = setInterval(() => {
      const now = new Date();
      setLastUpdateTime(now.toLocaleTimeString());

      setLiveTelemetry(prev => {
        // Multiplier based on scenario
        let vibTarget = 12.4;
        let rainTarget = 26.5;
        let dispTarget = 4.85;
        let poreTarget = 185.0;
        let tempTarget = 29.4;
        let fosTarget = 1.14;

        if (activeScenario === 'normal') {
          vibTarget = 1.8;
          rainTarget = 0.5;
          dispTarget = 0.85;
          poreTarget = 65.0;
          tempTarget = 27.5;
          fosTarget = 1.85;
        } else if (activeScenario === 'storm') {
          vibTarget = 3.2;
          rainTarget = 38.0;
          dispTarget = 2.40;
          poreTarget = 210.0;
          tempTarget = 22.0;
          fosTarget = 1.35;
        } else if (activeScenario === 'microseismic') {
          vibTarget = 16.5;
          rainTarget = 4.0;
          dispTarget = 3.60;
          poreTarget = 120.0;
          tempTarget = 29.0;
          fosTarget = 1.22;
        }

        // Add micro-noise
        const newVib = Math.max(0.1, Number((vibTarget + (Math.random() * 0.6 - 0.3)).toFixed(2)));
        const newRain = Math.max(0, Number((rainTarget + (Math.random() * 0.8 - 0.4)).toFixed(1)));
        const newDisp = Math.max(0.1, Number((dispTarget + (Math.random() * 0.1 - 0.05)).toFixed(2)));
        const newPore = Math.max(40, Number((poreTarget + (Math.random() * 3.0 - 1.5)).toFixed(1)));
        const newTemp = Number((tempTarget + (Math.random() * 0.2 - 0.1)).toFixed(1));
        const newFos = Math.max(0.95, Number((fosTarget + (Math.random() * 0.02 - 0.01)).toFixed(2)));

        const nextTelemetry = {
          vibration: {
            ...prev.vibration,
            value: newVib,
            status: newVib > 15 ? 'CRITICAL' : newVib > 8 ? 'HIGH' : newVib > 4.5 ? 'MODERATE' : 'LOW',
            sparkline: [...prev.vibration.sparkline.slice(1), newVib]
          },
          rainfall: {
            ...prev.rainfall,
            value: newRain,
            status: newRain > 35 ? 'CRITICAL' : newRain > 18 ? 'HIGH' : newRain > 5 ? 'MODERATE' : 'LOW',
            sparkline: [...prev.rainfall.sparkline.slice(1), newRain]
          },
          displacement: {
            ...prev.displacement,
            value: newDisp,
            status: newDisp > 6.0 ? 'CRITICAL' : newDisp > 3.5 ? 'HIGH' : newDisp > 1.8 ? 'MODERATE' : 'LOW',
            sparkline: [...prev.displacement.sparkline.slice(1), newDisp]
          },
          porePressure: {
            ...prev.porePressure,
            value: newPore,
            status: newPore > 240 ? 'CRITICAL' : newPore > 160 ? 'HIGH' : newPore > 110 ? 'MODERATE' : 'LOW',
            sparkline: [...prev.porePressure.sparkline.slice(1), newPore]
          },
          temperature: {
            ...prev.temperature,
            value: newTemp,
            sparkline: [...prev.temperature.sparkline.slice(1), newTemp]
          },
          slopeStability: {
            ...prev.slopeStability,
            value: newFos,
            status: newFos < 1.05 ? 'CRITICAL' : newFos < 1.25 ? 'HIGH' : newFos < 1.45 ? 'MODERATE' : 'LOW',
            sparkline: [...prev.slopeStability.sparkline.slice(1), newFos]
          }
        };

        // Append to history
        const timeLabel = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        const historyPoint = {
          time: timeLabel,
          fullDate: now.toISOString(),
          vibration: newVib,
          rainfall: newRain,
          displacement: newDisp,
          porePressure: newPore,
          temperature: newTemp,
          slopeStability: newFos,
          riskScore: activeScenario === 'rockfall_hazard' ? 88 : activeScenario === 'microseismic' ? 68 : activeScenario === 'storm' ? 48 : 18
        };

        setTelemetryHistory(prevHist => {
          const updated = [...prevHist.slice(1), historyPoint];
          return updated;
        });

        return nextTelemetry;
      });
    }, Math.max(500, 2000 / streamSpeed));

    return () => clearInterval(interval);
  }, [isStreaming, isDemoMode, streamSpeed, activeScenario]);

  // Scenario Switcher for SIH Hackathon Demo Walkthrough
  const applyScenario = useCallback((scenarioType) => {
    setActiveScenario(scenarioType);
    if (scenarioType === 'normal') {
      setCurrentRisk({
        currentRisk: "LOW",
        riskScore: 18,
        predictionStatus: "NORMAL / STABLE",
        confidence: "96%",
        hazardType: "Baseline Stability",
        projectedTimeToCritical: "None",
        affectedPrimaryZone: "All Zones Nominal",
        affectedSecondaryZone: "None",
        modelSummary: "All geotechnical instruments operating within safe baseline parameters. Zero shear creep detected."
      });
      setZones(prev => prev.map(z => ({
        ...z,
        riskLevel: "LOW",
        riskScore: Math.min(25, z.riskScore),
        status: "STABLE",
        activeAlertsCount: 0
      })));
      setActiveAlarmTriggered(false);
    } else if (scenarioType === 'storm') {
      setCurrentRisk({
        currentRisk: "MODERATE",
        riskScore: 52,
        predictionStatus: "WATER INFILTRATION WARNING",
        confidence: "89%",
        hazardType: "Catchment Wall Saturation",
        projectedTimeToCritical: "4 - 6 hours",
        affectedPrimaryZone: "Zone C-01 (South Catchment Wall)",
        affectedSecondaryZone: "Zone A-02 (Haul Ramp)",
        modelSummary: "Precipitation surge detected. Hydrostatic pore water pressure rising along lower benches."
      });
      setZones(prev => prev.map(z => {
        if (z.id === 'Zone C-01') return { ...z, riskLevel: 'MODERATE', riskScore: 58, status: 'WATER INFILTRATION', activeAlertsCount: 1 };
        if (z.id === 'Zone A-02') return { ...z, riskLevel: 'MODERATE', riskScore: 48, status: 'SLICK HAUL RAMP', activeAlertsCount: 1 };
        return { ...z, riskLevel: 'LOW', riskScore: 20, status: 'STABLE', activeAlertsCount: 0 };
      }));
      setActiveAlarmTriggered(false);
    } else if (scenarioType === 'microseismic') {
      setCurrentRisk({
        currentRisk: "HIGH",
        riskScore: 72,
        predictionStatus: "ELEVATED VIBRATION RISK",
        confidence: "91%",
        hazardType: "Micro-seismic Bench Dilation",
        projectedTimeToCritical: "1 - 2 hours",
        affectedPrimaryZone: "Zone B-02 (South-West Bench)",
        affectedSecondaryZone: "Zone A-03 (East Highwall)",
        modelSummary: "Subsurface seismic energy release detected by triaxial geophones. Haul road shear strain active."
      });
      setZones(prev => prev.map(z => {
        if (z.id === 'Zone B-02') return { ...z, riskLevel: 'HIGH', riskScore: 74, status: 'RAPID CREEP DETECTED', activeAlertsCount: 1 };
        if (z.id === 'Zone A-03') return { ...z, riskLevel: 'HIGH', riskScore: 68, status: 'MICRO-FRACTURES ACTIVE', activeAlertsCount: 1 };
        if (z.id === 'Zone A-02') return { ...z, riskLevel: 'MODERATE', riskScore: 52, status: 'SPEED RESTRICTED', activeAlertsCount: 1 };
        return { ...z, riskLevel: 'LOW', riskScore: 22, status: 'STABLE', activeAlertsCount: 0 };
      }));
      setActiveAlarmTriggered(true);
    } else if (scenarioType === 'rockfall_hazard') {
      setCurrentRisk(MOCK_CURRENT_PREDICTION);
      setZones(MOCK_ZONES);
      setActiveAlarmTriggered(true);
    }
  }, []);

  // Alert Actions
  const acknowledgeAlert = useCallback((alertId) => {
    setAlerts(prev => prev.map(a => a.id === alertId ? { ...a, status: 'ACKNOWLEDGED' } : a));
    if (selectedAlert && selectedAlert.id === alertId) {
      setSelectedAlert(prev => ({ ...prev, status: 'ACKNOWLEDGED' }));
    }
  }, [selectedAlert]);

  const resolveAlert = useCallback((alertId) => {
    setAlerts(prev => prev.map(a => a.id === alertId ? { ...a, status: 'RESOLVED' } : a));
    if (selectedAlert && selectedAlert.id === alertId) {
      setSelectedAlert(prev => ({ ...prev, status: 'RESOLVED' }));
    }
  }, [selectedAlert]);

  const toggleActionPlanStep = useCallback((alertId, stepIndex) => {
    setAlerts(prev => prev.map(a => {
      if (a.id === alertId && a.actionPlan) {
        const newPlan = [...a.actionPlan];
        newPlan[stepIndex] = { ...newPlan[stepIndex], completed: !newPlan[stepIndex].completed };
        return { ...a, actionPlan: newPlan };
      }
      return a;
    }));
    if (selectedAlert && selectedAlert.id === alertId && selectedAlert.actionPlan) {
      setSelectedAlert(prev => {
        const newPlan = [...prev.actionPlan];
        newPlan[stepIndex] = { ...newPlan[stepIndex], completed: !newPlan[stepIndex].completed };
        return { ...prev, actionPlan: newPlan };
      });
    }
  }, [selectedAlert]);

  const selectZoneById = useCallback((zoneId) => {
    const found = zones.find(z => z.id === zoneId);
    if (found) {
      setSelectedZone(found);
    }
  }, [zones]);

  const value = {
    // Navigation
    currentTab,
    setCurrentTab,
    
    // Risk & AI
    currentRisk,
    setCurrentRisk,
    riskFactors: MOCK_RISK_FACTORS,
    predictionHistory: MOCK_PREDICTION_HISTORY,
    
    // Telemetry
    liveTelemetry,
    telemetryHistory,
    sensors,
    lastUpdateTime,
    
    // Zones & Map
    zones,
    selectedZone,
    setSelectedZone,
    selectZoneById,
    
    // Alerts
    alerts,
    selectedAlert,
    setSelectedAlert,
    unreadAlertCount,
    setUnreadAlertCount,
    activeAlarmTriggered,
    setActiveAlarmTriggered,
    acknowledgeAlert,
    resolveAlert,
    toggleActionPlanStep,
    
    // Simulation controls
    isDemoMode,
    setIsDemoMode,
    isStreaming,
    setIsStreaming,
    streamSpeed,
    setStreamSpeed,
    activeScenario,
    applyScenario,
    
    // System Status & Settings
    systemStatus,
    settings,
    setSettings
  };

  return (
    <MineGuardContext.Provider value={value}>
      {children}
    </MineGuardContext.Provider>
  );
}

export function useMineGuard() {
  const context = useContext(MineGuardContext);
  if (!context) {
    throw new Error('useMineGuard must be used within a MineGuardProvider');
  }
  return context;
}
