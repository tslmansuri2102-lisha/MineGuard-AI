import React from 'react';
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MainRiskPanel } from '../components/risk/MainRiskPanel';
import { NormalizedRiskAssessment, SensorTelemetryPayload } from '../types/telemetry';

describe('MainRiskPanel Component', () => {
  const mockTelemetry: SensorTelemetryPayload = {
    mine_id: 'MINE-001',
    zone_id: 'ZONE-003',
    sensor_id: 'SENSOR-003',
    timestamp: '2026-08-16T12:00:00Z',
    sensors: {
      displacement_mm: 4.2,
      strain: 0.21,
      pore_pressure_kpa: 31.5,
      rainfall_mm: 3.2,
      temperature_c: 28.4,
      vibration_g: 0.18,
    },
  };

  it('renders LOW risk score and level correctly', () => {
    const mockRisk: NormalizedRiskAssessment = {
      score: 12.5,
      level: 'LOW',
      confidence: 0.95,
      status: 'NORMAL',
      factors: [{ feature: 'baseline_stability', impact: 'LOW' }],
      recommended_action: 'Continue normal monitoring.',
    };

    render(<MainRiskPanel risk={mockRisk} telemetry={mockTelemetry} />);
    expect(screen.getByText('12.5')).toBeInTheDocument();
    expect(screen.getByText('LOW RISK')).toBeInTheDocument();
    expect(screen.getByText('95%')).toBeInTheDocument();
    expect(screen.getByText('NORMAL')).toBeInTheDocument();
    expect(screen.getByText('MINE-001')).toBeInTheDocument();
    expect(screen.getByText('ZONE-003')).toBeInTheDocument();
    expect(screen.getByText('SENSOR-003')).toBeInTheDocument();
  });

  it('renders CRITICAL risk level with 100 score', () => {
    const mockRisk: NormalizedRiskAssessment = {
      score: 100.0,
      level: 'CRITICAL',
      confidence: 0.95,
      status: 'NORMAL',
      factors: [
        { feature: 'displacement_rate', impact: 'HIGH' },
        { feature: 'pore_pressure_kpa', impact: 'HIGH' },
      ],
      recommended_action: 'Evacuate personnel from the affected zone and initiate emergency geotechnical assessment.',
    };

    render(<MainRiskPanel risk={mockRisk} telemetry={mockTelemetry} />);
    expect(screen.getByText('100.0')).toBeInTheDocument();
    expect(screen.getByText('CRITICAL RISK')).toBeInTheDocument();
  });

  it('renders DEGRADED data quality status with reduced confidence', () => {
    const mockRisk: NormalizedRiskAssessment = {
      score: 10.0,
      level: 'LOW',
      confidence: 0.20,
      status: 'DEGRADED',
      factors: [{ feature: 'baseline_stability', impact: 'LOW' }],
      recommended_action: 'Sensor data quality compromised. Verify sensor health.',
    };

    render(<MainRiskPanel risk={mockRisk} telemetry={mockTelemetry} />);
    expect(screen.getByText('DEGRADED')).toBeInTheDocument();
    expect(screen.getByText('20%')).toBeInTheDocument();
  });
});
