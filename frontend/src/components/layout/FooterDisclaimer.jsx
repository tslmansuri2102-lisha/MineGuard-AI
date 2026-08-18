import React from 'react';
import { ShieldCheck, Info } from 'lucide-react';

export function FooterDisclaimer() {
  return (
    <footer style={{
      padding: '16px 24px',
      borderTop: '1px solid var(--border-subtle)',
      backgroundColor: 'var(--bg-card-subtle)',
      marginTop: 'auto',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      flexWrap: 'wrap',
      gap: '12px',
      fontSize: '11px',
      color: 'var(--text-tertiary)'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', maxWidth: '820px' }}>
        <Info size={14} style={{ flexShrink: 0, color: 'var(--text-accent)' }} />
        <span>
          <strong>Safety Prototype Notice:</strong> MineGuard AI is a decision-support and risk estimation prototype. Mine safety and evacuation decisions must follow certified geotechnical engineering procedures and applicable regulations.
        </span>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '16px', fontFamily: 'var(--font-mono)' }}>
        <span>MINEGUARD AI v1.0.0 (SIH 2026)</span>
        <span>STANDALONE DEMO ENGINE</span>
      </div>
    </footer>
  );
}

export default FooterDisclaimer;
