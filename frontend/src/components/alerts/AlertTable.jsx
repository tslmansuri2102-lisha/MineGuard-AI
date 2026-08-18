import React, { useState } from 'react';
import { Search, Filter, AlertTriangle, ArrowUpRight, ExternalLink } from 'lucide-react';
import { RiskBadge, StatusBadge } from '../common/StatusBadge';
import { useMineGuard } from '../../context/MineGuardContext';

export function AlertTable({ alerts = [], onSelectAlert = null, initialFilter = 'ALL' }) {
  const [filter, setFilter] = useState(initialFilter);
  const [search, setSearch] = useState('');

  const filtered = alerts.filter(alert => {
    // Severity Filter
    if (filter !== 'ALL') {
      if (filter === 'RESOLVED') {
        if (alert.status !== 'RESOLVED') return false;
      } else {
        if (alert.severity !== filter) return false;
      }
    }

    // Search Query
    if (search.trim()) {
      const q = search.toLowerCase();
      const matchTitle = alert.title?.toLowerCase().includes(q);
      const matchZone = alert.zoneName?.toLowerCase().includes(q) || alert.zoneId?.toLowerCase().includes(q);
      const matchDesc = alert.description?.toLowerCase().includes(q);
      if (!matchTitle && !matchZone && !matchDesc) return false;
    }

    return true;
  });

  return (
    <div className="command-card" style={{ padding: '0', overflow: 'hidden' }}>
      {/* Search & Filter Toolbar */}
      <div style={{
        padding: '14px 18px',
        backgroundColor: 'var(--bg-topbar)',
        borderBottom: '1px solid var(--border-subtle)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '12px'
      }}>
        {/* Severity Tabs */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap' }}>
          {['ALL', 'CRITICAL', 'HIGH', 'MODERATE', 'LOW', 'RESOLVED'].map(sev => (
            <button
              key={sev}
              onClick={() => setFilter(sev)}
              style={{
                padding: '4px 10px',
                borderRadius: '4px',
                fontSize: '11px',
                fontWeight: 700,
                fontFamily: 'var(--font-mono)',
                backgroundColor: filter === sev ? 'rgba(56, 189, 248, 0.15)' : 'var(--bg-card)',
                color: filter === sev ? '#38BDF8' : 'var(--text-secondary)',
                border: `1px solid ${filter === sev ? 'rgba(56, 189, 248, 0.4)' : 'var(--border-subtle)'}`
              }}
            >
              {sev}
            </button>
          ))}
        </div>

        {/* Search Field */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          padding: '6px 12px',
          backgroundColor: 'var(--bg-card)',
          border: '1px solid var(--border-subtle)',
          borderRadius: '6px',
          width: 'min(280px, 100%)'
        }}>
          <Search size={14} color="var(--text-tertiary)" />
          <input
            type="text"
            placeholder="Search alerts or zones..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            style={{
              background: 'transparent',
              border: 'none',
              outline: 'none',
              fontSize: '12px',
              color: '#FFFFFF',
              width: '100%'
            }}
          />
        </div>
      </div>

      {/* Table Element */}
      <div className="command-table-container" style={{ border: 'none', borderRadius: 0 }}>
        <table className="command-table">
          <thead>
            <tr>
              <th>Severity</th>
              <th>Alert Description</th>
              <th>Mine Zone</th>
              <th>Category</th>
              <th>Time</th>
              <th>Status</th>
              <th style={{ textAlign: 'right' }}>Action</th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 ? (
              <tr>
                <td colSpan="7" style={{ textAlign: 'center', padding: '32px', color: 'var(--text-tertiary)' }}>
                  No active geotechnical alerts matching filter criteria.
                </td>
              </tr>
            ) : (
              filtered.map(alert => (
                <tr
                  key={alert.id}
                  className="clickable-row"
                  onClick={() => onSelectAlert && onSelectAlert(alert)}
                >
                  <td style={{ width: '110px' }}>
                    <RiskBadge level={alert.severity} size="sm" />
                  </td>

                  <td>
                    <div style={{ fontWeight: 600, color: '#FFFFFF', fontSize: '13px' }}>
                      {alert.title}
                    </div>
                    <div style={{ fontSize: '11px', color: 'var(--text-tertiary)', marginTop: '2px', maxWidth: '420px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {alert.description}
                    </div>
                  </td>

                  <td>
                    <div style={{ fontWeight: 600, color: 'var(--text-accent)', fontSize: '12px' }}>
                      {alert.zoneId}
                    </div>
                    <div style={{ fontSize: '11px', color: 'var(--text-tertiary)' }}>
                      {alert.zoneName}
                    </div>
                  </td>

                  <td>
                    <span style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
                      {alert.category}
                    </span>
                  </td>

                  <td>
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--text-tertiary)' }}>
                      {alert.time}
                    </span>
                  </td>

                  <td>
                    <StatusBadge status={alert.status} />
                  </td>

                  <td style={{ textAlign: 'right' }}>
                    <button
                      style={{
                        padding: '4px 8px',
                        borderRadius: '4px',
                        backgroundColor: 'rgba(255, 255, 255, 0.05)',
                        border: '1px solid var(--border-subtle)',
                        color: 'var(--text-secondary)',
                        fontSize: '11px',
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '4px'
                      }}
                    >
                      <span>Inspect</span>
                      <ExternalLink size={12} />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default AlertTable;
