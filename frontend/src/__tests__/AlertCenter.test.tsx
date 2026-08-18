import React from 'react';
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { AlertCenter } from '../components/alerts/AlertCenter';
import { AlertEvent } from '../types/telemetry';

describe('AlertCenter Component', () => {
  it('renders empty alert message when no events exist', () => {
    render(<AlertCenter alerts={[]} />);
    expect(screen.getByText('No Safety Alerts Triggered')).toBeInTheDocument();
    expect(screen.getByText('0 Events Dispatched')).toBeInTheDocument();
  });

  it('renders critical and high alerts correctly', () => {
    const mockAlerts: AlertEvent[] = [
      {
        alert_id: 'ALERT-000001',
        timestamp: '2026-08-16T12:30:00Z',
        mine_id: 'MINE-001',
        zone_id: 'ZONE-003',
        sensor_id: 'SENSOR-003',
        risk_level: 'CRITICAL',
        risk_score: 100.0,
        message: 'Catastrophic slope displacement detected.',
        recommended_action: 'Evacuate personnel immediately.',
        factors: [{ feature: 'displacement_rate', impact: 'HIGH' }],
      },
      {
        alert_id: 'ALERT-000002',
        timestamp: '2026-08-16T12:28:00Z',
        mine_id: 'MINE-001',
        zone_id: 'ZONE-003',
        sensor_id: 'SENSOR-003',
        risk_level: 'HIGH',
        risk_score: 72.5,
        message: 'Heavy rain pore pressure infiltration warning.',
        recommended_action: 'Inspect drainage pumps.',
        factors: [{ feature: 'pore_pressure_kpa', impact: 'HIGH' }],
      },
    ];

    render(<AlertCenter alerts={mockAlerts} />);

    expect(screen.getByText('[ALERT-000001]')).toBeInTheDocument();
    expect(screen.getByText('Catastrophic slope displacement detected.')).toBeInTheDocument();
    expect(screen.getByText('Action: Evacuate personnel immediately.')).toBeInTheDocument();

    expect(screen.getByText('[ALERT-000002]')).toBeInTheDocument();
    expect(screen.getByText('Heavy rain pore pressure infiltration warning.')).toBeInTheDocument();
    expect(screen.getByText('2 Events Dispatched')).toBeInTheDocument();
  });
});
