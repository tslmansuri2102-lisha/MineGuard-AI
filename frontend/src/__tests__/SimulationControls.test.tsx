import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { SimulationControls } from '../components/controls/SimulationControls';
import { SimulationStatus } from '../types/telemetry';

describe('SimulationControls Component', () => {
  const mockStatus: SimulationStatus = {
    status: 'Simulation running',
    is_running: true,
    mine_id: 'MINE-001',
    zone_id: 'ZONE-003',
    sensor_id: 'SENSOR-003',
    scenario: 'NORMAL',
    interval_seconds: 1.0,
    reading_count: 42,
  };

  it('renders simulation controls, scenario selector and reading count', () => {
    const handleStart = vi.fn().mockResolvedValue({});
    const handleStop = vi.fn().mockResolvedValue({});

    render(
      <SimulationControls
        status={mockStatus}
        onStart={handleStart}
        onStop={handleStop}
      />
    );

    expect(screen.getByText('Physics Simulation & Scenario Orchestration')).toBeInTheDocument();
    expect(screen.getByText('42')).toBeInTheDocument();
    expect(screen.getByText('Stop')).toBeInTheDocument();
  });

  it('triggers onStart when start button is clicked', () => {
    const handleStart = vi.fn().mockResolvedValue({});
    const handleStop = vi.fn().mockResolvedValue({});

    render(
      <SimulationControls
        status={mockStatus}
        onStart={handleStart}
        onStop={handleStop}
      />
    );

    const startBtn = screen.getByRole('button', { name: /Reconfigure|Start/i });
    fireEvent.click(startBtn);
    expect(handleStart).toHaveBeenCalled();
  });

  it('triggers onStart with scenario when quick preset button is clicked', () => {
    const handleStart = vi.fn().mockResolvedValue({});
    const handleStop = vi.fn().mockResolvedValue({});

    render(
      <SimulationControls
        status={mockStatus}
        onStart={handleStart}
        onStop={handleStop}
      />
    );

    const rainBtn = screen.getByRole('button', { name: /Heavy Rain/i });
    fireEvent.click(rainBtn);
    expect(handleStart).toHaveBeenCalledWith('HEAVY_RAIN', 1.0, 42);
  });
});
