import React from 'react';
import { AlertCircle, Cpu, ShieldCheck } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer style={{
      background: 'var(--bg-panel)',
      borderTop: '1px solid var(--border-subtle)',
      padding: '16px 24px',
      marginTop: 'auto',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      flexWrap: 'wrap',
      gap: '12px',
      fontSize: '0.75rem',
      color: 'var(--text-muted)',
    }}>
      {/* Model Disclosure */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <Cpu size={15} color="#38bdf8" />
        <span>
          <strong style={{ color: 'var(--text-secondary)' }}>AI Engine:</strong> Multi-Criteria Geotechnical Risk Model (Rule-Based Baseline). Extensible interface prepared for future trained ML (Random Forest / XGBoost / LSTM).
        </span>
      </div>

      {/* Safety Disclaimer */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#fbbf24' }}>
        <AlertCircle size={14} />
        <span>PROTOTYPE EARLY WARNING DEMO — Not certified for life-critical autonomous operations.</span>
      </div>

      {/* Team / SIH */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
        <ShieldCheck size={14} color="#10b981" />
        <span>MineGuard AI — Smart India Hackathon (SIH) 2026</span>
      </div>
    </footer>
  );
};
