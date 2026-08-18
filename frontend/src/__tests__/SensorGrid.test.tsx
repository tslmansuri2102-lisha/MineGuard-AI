import React from 'react';
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { SensorGrid } from '../components/sensors/SensorGrid';
import { SensorValues } from '../types/telemetry';

describe('SensorGrid Component', () => {
  const mockSensors: SensorValues = {
    displacement_mm: 24.2,
    strain: 0.81,
    pore_pressure_kpa: 62.0,
    rainfall_mm: 74.0,
    temperature_c: 32.0,
    vibration_g: 1.2,
  };

  it('renders all 6 sensor channels with correct values and units', () => {
    render(<SensorGrid sensors={mockSensors} status="NORMAL" />);

    expect(screen.getByText('Displacement')).toBeInTheDocument();
    expect(screen.getByText('24.2')).toBeInTheDocument();

    expect(screen.getByText('Rock Shear Strain')).toBeInTheDocument();
    expect(screen.getByText('0.81')).toBeInTheDocument();

    expect(screen.getByText('Pore Water Pressure')).toBeInTheDocument();
    expect(screen.getByText('62.0')).toBeInTheDocument();

    expect(screen.getByText('Precipitation')).toBeInTheDocument();
    expect(screen.getByText('74.0')).toBeInTheDocument();

    expect(screen.getByText('Bench Temperature')).toBeInTheDocument();
    expect(screen.getByText('32.0')).toBeInTheDocument();

    expect(screen.getByText('Dynamic Vibration')).toBeInTheDocument();
    expect(screen.getByText('1.20')).toBeInTheDocument();
  });

  it('renders fault status when data is degraded', () => {
    render(<SensorGrid sensors={{ ...mockSensors, displacement_mm: 0, strain: 0 }} status="DEGRADED" />);
    const faultBadges = screen.getAllByText('FAULT');
    expect(faultBadges.length).toBeGreaterThan(0);
  });
});
