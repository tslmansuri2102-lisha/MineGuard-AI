import React from 'react';

export function Sparkline({ data = [], color = '#38BDF8', height = 32, width = 110, showGradient = true }) {
  if (!data || data.length < 2) return null;

  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min === 0 ? 1 : max - min;
  const padding = 2;
  const effectiveHeight = height - padding * 2;
  const effectiveWidth = width - padding * 2;

  const points = data.map((val, idx) => {
    const x = padding + (idx / (data.length - 1)) * effectiveWidth;
    const y = height - padding - ((val - min) / range) * effectiveHeight;
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  });

  const pathD = `M ${points.join(' L ')}`;
  const fillD = `${pathD} L ${width - padding},${height} L ${padding},${height} Z`;
  const gradId = `spark-grad-${color.replace('#', '')}-${Math.random().toString(36).substr(2, 5)}`;

  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} style={{ overflow: 'visible' }}>
      <defs>
        <linearGradient id={gradId} x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor={color} stopOpacity={0.4} />
          <stop offset="100%" stopColor={color} stopOpacity={0.0} />
        </linearGradient>
      </defs>
      {showGradient && <path d={fillD} fill={`url(#${gradId})`} />}
      <path d={pathD} fill="none" stroke={color} strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
      {/* Current point indicator */}
      {points.length > 0 && (
        <circle 
          cx={points[points.length - 1].split(',')[0]} 
          cy={points[points.length - 1].split(',')[1]} 
          r={2.5} 
          fill={color} 
          stroke="#090D14" 
          strokeWidth={1} 
        />
      )}
    </svg>
  );
}

export default Sparkline;
