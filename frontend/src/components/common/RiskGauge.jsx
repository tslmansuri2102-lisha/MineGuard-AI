import React from 'react';
import { ShieldAlert, AlertTriangle, ShieldCheck, Cpu, Info } from 'lucide-react';
import { RiskBadge } from './StatusBadge';

export function RiskGauge({
  score = 72,
  riskLevel = 'HIGH',
  confidence = '91%',
  status = 'ELEVATED RISK',
  hazardType = 'Planar Highwall Shear & Rockfall',
  timeToCritical = '45 - 90 mins',
  primaryZone = 'Zone A-03 (East Highwall)'
}) {
  // Semi-circle gauge calculation (angle: 180 degrees from -180 to 0 or polar coordinates)
  // Normalized score 0-100 to angle 0 to 180
  const clampedScore = Math.min(100, Math.max(0, score));
  const strokeWidth = 14;
  const radius = 95;
  const cx = 130;
  const cy = 125;
  
  // Circumference of semi-circle: PI * R
  const arcLength = Math.PI * radius;
  // Offset for dasharray: stroke-dashoffset = arcLength * (1 - clampedScore / 100)
  const strokeDashoffset = arcLength * (1 - clampedScore / 100);

  // Determine color theme based on score
  let activeColor = '#10B981';
  let glowColor = 'rgba(16, 185, 129, 0.3)';
  if (clampedScore >= 80) {
    activeColor = '#EF4444';
    glowColor = 'rgba(239, 68, 68, 0.4)';
  } else if (clampedScore >= 60) {
    activeColor = '#F97316';
    glowColor = 'rgba(249, 115, 22, 0.35)';
  } else if (clampedScore >= 35) {
    activeColor = '#F59E0B';
    glowColor = 'rgba(245, 158, 11, 0.3)';
  }

  // Needle angle: -90deg (0 score) to +90deg (100 score)
  const needleAngle = -90 + (clampedScore / 100) * 180;

  return (
    <div className="command-card card-elevated" style={{ position: 'relative', overflow: 'hidden' }}>
      {/* Top Banner Tag */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{ 
            width: '8px', 
            height: '8px', 
            borderRadius: '50%', 
            backgroundColor: activeColor,
            boxShadow: `0 0 10px ${activeColor}`
          }} />
          <span style={{ 
            fontFamily: 'var(--font-heading)', 
            fontSize: '13px', 
            fontWeight: 700, 
            letterSpacing: '0.8px',
            color: '#FFFFFF',
            textTransform: 'uppercase'
          }}>
            Current Mine Risk
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span style={{
            fontSize: '10px',
            fontFamily: 'var(--font-mono)',
            fontWeight: 700,
            color: '#38BDF8',
            backgroundColor: 'rgba(56, 189, 248, 0.12)',
            border: '1px solid rgba(56, 189, 248, 0.3)',
            padding: '2px 8px',
            borderRadius: '4px'
          }}>
            DEMO AI OUTPUT
          </span>
          <RiskBadge level={riskLevel} />
        </div>
      </div>

      {/* Main Gauge Graphic & Score Display */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-around', flexWrap: 'wrap', gap: '20px', padding: '10px 0' }}>
        {/* SVG Semi-Circle Arc */}
        <div style={{ position: 'relative', width: '260px', height: '145px', display: 'flex', justifyContent: 'center' }}>
          <svg width="260" height="145" viewBox="0 0 260 145" style={{ overflow: 'visible' }}>
            <defs>
              <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#10B981" />
                <stop offset="35%" stopColor="#F59E0B" />
                <stop offset="70%" stopColor="#F97316" />
                <stop offset="100%" stopColor="#EF4444" />
              </linearGradient>
              <filter id="gaugeGlow">
                <feGaussianBlur stdDeviation="3" result="blur" />
                <feComposite in="SourceGraphic" in2="blur" operator="over" />
              </filter>
            </defs>

            {/* Background Track Arc */}
            <path
              d="M 35,125 A 95,95 0 0,1 225,125"
              fill="none"
              stroke="rgba(255, 255, 255, 0.08)"
              strokeWidth={strokeWidth}
              strokeLinecap="round"
            />

            {/* Active Colored Arc */}
            <path
              d="M 35,125 A 95,95 0 0,1 225,125"
              fill="none"
              stroke="url(#gaugeGradient)"
              strokeWidth={strokeWidth}
              strokeDasharray={arcLength}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
              filter="url(#gaugeGlow)"
              style={{ transition: 'stroke-dashoffset 0.8s cubic-bezier(0.4, 0, 0.2, 1)' }}
            />

            {/* Tick Threshold Marks */}
            <line x1="35" y1="125" x2="45" y2="125" stroke="var(--risk-low)" strokeWidth="2" />
            <line x1="130" y1="30" x2="130" y2="40" stroke="var(--risk-moderate)" strokeWidth="2" />
            <line x1="225" y1="125" x2="215" y2="125" stroke="var(--risk-critical)" strokeWidth="2" />

            {/* Center Pivot Indicator */}
            <circle cx={cx} cy={cy} r={7} fill="#1E293B" stroke={activeColor} strokeWidth={2.5} />
            
            {/* Animated Needle */}
            <g transform={`translate(${cx}, ${cy}) rotate(${needleAngle})`} style={{ transition: 'transform 0.8s cubic-bezier(0.4, 0, 0.2, 1)' }}>
              <line x1="0" y1="0" x2="0" y2="-75" stroke="#FFFFFF" strokeWidth="2.5" strokeLinecap="round" />
              <polygon points="-4,-60 0,-78 4,-60" fill={activeColor} />
            </g>
          </svg>

          {/* Value Display overlay inside bottom of arc */}
          <div style={{
            position: 'absolute',
            bottom: '2px',
            textAlign: 'center',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center'
          }}>
            <span style={{ 
              fontSize: '34px', 
              fontWeight: 800, 
              color: '#FFFFFF',
              fontFamily: 'var(--font-mono)',
              lineHeight: 1
            }}>
              {score}%
            </span>
            <span style={{ 
              fontSize: '11px', 
              fontWeight: 700, 
              color: activeColor,
              letterSpacing: '1px',
              fontFamily: 'var(--font-heading)',
              textTransform: 'uppercase',
              marginTop: '4px'
            }}>
              {riskLevel} RISK
            </span>
          </div>
        </div>

        {/* AI Geotechnical Metadata Box */}
        <div style={{ flex: 1, minWidth: '220px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <div style={{ 
            padding: '10px 14px', 
            backgroundColor: 'rgba(0, 0, 0, 0.25)', 
            borderRadius: '6px',
            border: '1px solid var(--border-subtle)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
              <span style={{ fontSize: '11px', color: 'var(--text-tertiary)' }}>Model Confidence</span>
              <span style={{ fontSize: '12px', fontWeight: 700, fontFamily: 'var(--font-mono)', color: '#10B981' }}>
                {confidence}
              </span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '11px', color: 'var(--text-tertiary)' }}>Prediction State</span>
              <span style={{ fontSize: '11px', fontWeight: 700, fontFamily: 'var(--font-mono)', color: activeColor }}>
                {status}
              </span>
            </div>
          </div>

          <div style={{ fontSize: '12px', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
            <div style={{ marginBottom: '4px' }}>
              <span style={{ color: 'var(--text-tertiary)' }}>Primary Hazard: </span>
              <strong style={{ color: '#FFFFFF' }}>{hazardType}</strong>
            </div>
            <div>
              <span style={{ color: 'var(--text-tertiary)' }}>Critical Target: </span>
              <span style={{ color: '#F97316', fontWeight: 600 }}>{primaryZone}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Geotechnical Threshold Bar */}
      <div style={{ marginTop: '14px', paddingTop: '10px', borderTop: '1px solid var(--border-subtle)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10px', color: 'var(--text-tertiary)', fontFamily: 'var(--font-mono)', marginBottom: '4px' }}>
          <span>LOW (0-35%)</span>
          <span>MODERATE (36-60%)</span>
          <span>HIGH (61-80%)</span>
          <span>CRITICAL (81-100%)</span>
        </div>
        <div style={{ height: '4px', width: '100%', display: 'flex', borderRadius: '2px', overflow: 'hidden' }}>
          <div style={{ flex: 35, background: 'var(--risk-low)' }} />
          <div style={{ flex: 25, background: 'var(--risk-moderate)' }} />
          <div style={{ flex: 20, background: 'var(--risk-high)' }} />
          <div style={{ flex: 20, background: 'var(--risk-critical)' }} />
        </div>
      </div>
    </div>
  );
}

export default RiskGauge;
