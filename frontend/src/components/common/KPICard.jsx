import React from 'react';
import { ArrowUpRight, ArrowDownRight, Minus } from 'lucide-react';
import Sparkline from '../charts/Sparkline';

export function KPICard({
  title,
  value,
  unit = '',
  status = null,
  statusColor = '#9CA3AF',
  delta = null,
  trend = 'neutral',
  subtitle = '',
  icon: Icon = null,
  sparklineData = null,
  sparklineColor = '#38BDF8',
  highlight = false,
  onClick = null
}) {
  return (
    <div 
      className={`command-card ${highlight ? 'hazard-highlight' : ''}`}
      onClick={onClick}
      style={{
        cursor: onClick ? 'pointer' : 'default',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        minHeight: '128px'
      }}
    >
      {/* Top row */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {Icon && (
            <div style={{ 
              padding: '6px', 
              borderRadius: '6px', 
              backgroundColor: 'rgba(255, 255, 255, 0.05)',
              color: statusColor || 'var(--text-accent)'
            }}>
              <Icon size={16} />
            </div>
          )}
          <span style={{ 
            fontSize: '11px', 
            fontWeight: 700, 
            color: 'var(--text-tertiary)', 
            textTransform: 'uppercase',
            letterSpacing: '0.6px',
            fontFamily: 'var(--font-heading)'
          }}>
            {title}
          </span>
        </div>
        {status && (
          <span style={{
            fontSize: '10px',
            fontFamily: 'var(--font-mono)',
            fontWeight: 700,
            color: statusColor,
            backgroundColor: `${statusColor}18`,
            border: `1px solid ${statusColor}40`,
            padding: '2px 6px',
            borderRadius: '4px'
          }}>
            {status}
          </span>
        )}
      </div>

      {/* Main Metric Value & Trend Sparkline */}
      <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between', gap: '12px', marginTop: 'auto' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '4px' }}>
            <span style={{ 
              fontSize: '26px', 
              fontWeight: 800, 
              color: '#FFFFFF',
              fontFamily: 'var(--font-mono)',
              lineHeight: 1.1
            }}>
              {value}
            </span>
            {unit && (
              <span style={{ fontSize: '12px', color: 'var(--text-tertiary)', fontWeight: 500 }}>
                {unit}
              </span>
            )}
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginTop: '4px' }}>
            {delta && (
              <span style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '2px',
                fontSize: '11px',
                fontWeight: 600,
                fontFamily: 'var(--font-mono)',
                color: trend === 'up' ? (title.includes('Stability') ? '#10B981' : '#F97316') : (title.includes('Stability') ? '#EF4444' : '#10B981')
              }}>
                {trend === 'up' ? <ArrowUpRight size={13} /> : trend === 'down' ? <ArrowDownRight size={13} /> : <Minus size={13} />}
                {delta}
              </span>
            )}
            {subtitle && (
              <span style={{ fontSize: '11px', color: 'var(--text-tertiary)' }}>
                {subtitle}
              </span>
            )}
          </div>
        </div>

        {sparklineData && (
          <div style={{ paddingBottom: '4px' }}>
            <Sparkline data={sparklineData} color={sparklineColor} width={90} height={28} />
          </div>
        )}
      </div>
    </div>
  );
}

export default KPICard;
