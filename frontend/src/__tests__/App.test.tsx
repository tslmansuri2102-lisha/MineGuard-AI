import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import App from '../App';

// Mock WebSocket
class MockWebSocket {
  onopen: any;
  onmessage: any;
  onerror: any;
  onclose: any;
  readyState = 1;
  constructor(url: string) {
    setTimeout(() => {
      if (this.onopen) this.onopen();
    }, 10);
  }
  close() {}
  send() {}
}

vi.stubGlobal('WebSocket', MockWebSocket);

describe('App Component', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn().mockImplementation((url) => {
      if (url.includes('/health')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ status: 'ok', service: 'MineGuard AI backend' }),
        });
      }
      if (url.includes('/simulation/status')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            status: 'Simulation running',
            is_running: true,
            mine_id: 'MINE-001',
            zone_id: 'ZONE-003',
            sensor_id: 'SENSOR-003',
            scenario: 'NORMAL',
            interval_seconds: 1.0,
            reading_count: 5,
          }),
        });
      }
      if (url.includes('/alerts/history')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve([]),
        });
      }
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({}),
      });
    }));
  });

  it('renders the complete MineGuard AI Command Center dashboard without crashing', () => {
    render(<App />);

    expect(screen.getByText('MineGuard AI')).toBeInTheDocument();
    expect(screen.getByText('Intelligent Mine Safety Command Center')).toBeInTheDocument();
    expect(screen.getByText('Real-Time Geotechnical Risk Assessment')).toBeInTheDocument();
    expect(screen.getByText('Live In-Situ Sensor Telemetry Grid (6 Channels)')).toBeInTheDocument();
    expect(screen.getByText('Root-Cause Threat Attribution')).toBeInTheDocument();
    expect(screen.getByText('Prescriptive Operational Mitigation')).toBeInTheDocument();
    expect(screen.getByText('Real-Time Rolling Telemetry & Risk Kinematics')).toBeInTheDocument();
    expect(screen.getByText('Mine Schematic & Geotechnical Zone Map')).toBeInTheDocument();
    expect(screen.getByText('Geotechnical Safety Alert Center')).toBeInTheDocument();
    expect(screen.getByText('Physics Simulation & Scenario Orchestration')).toBeInTheDocument();
  });
});
