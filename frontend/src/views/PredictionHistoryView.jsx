import React, { useState } from 'react';
import {
  History,
  Search,
  Filter,
  Download,
  Calendar,
  FileSpreadsheet,
  CheckCircle2,
  TrendingUp,
  BrainCircuit,
  ArrowUpDown
} from 'lucide-react';
import { useMineGuard } from '../context/MineGuardContext';
import { RiskBadge, StatusBadge } from '../components/common/StatusBadge';
import RiskTrendChart from '../components/charts/RiskTrendChart';

export function PredictionHistoryView() {
  const { predictionHistory, telemetryHistory, selectZoneById, setCurrentTab } = useMineGuard();

  const [search, setSearch] = useState('');
  const [filterRisk, setFilterRisk] = useState('ALL');
  const [sortOrder, setSortOrder] = useState('desc');
  const [downloadSuccess, setDownloadSuccess] = useState(false);

  const filteredHistory = predictionHistory
    .filter(item => {
      if (filterRisk !== 'ALL' && item.risk !== filterRisk) return false;
      if (search.trim()) {
        const q = search.toLowerCase();
        return (
          item.zone?.toLowerCase().includes(q) ||
          item.zoneName?.toLowerCase().includes(q) ||
          item.keyTrigger?.toLowerCase().includes(q) ||
          item.actionTaken?.toLowerCase().includes(q)
        );
      }
      return true;
    })
    .sort((a, b) => {
      if (sortOrder === 'asc') return a.score - b.score;
      return b.score - a.score;
    });

  const handleExportCSV = () => {
    setDownloadSuccess(true);
    setTimeout(() => setDownloadSuccess(false), 3000);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '22px' }}>
      {/* Top Banner */}
      <div style={{
        padding: '16px 20px',
        backgroundColor: 'var(--bg-topbar)',
        borderRadius: '8px',
        border: '1px solid var(--border-subtle)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '12px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ padding: '8px', borderRadius: '6px', backgroundColor: 'rgba(56, 189, 248, 0.15)', color: '#38BDF8' }}>
            <History size={20} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <h2 style={{ fontFamily: 'var(--font-heading)', fontSize: '15px', fontWeight: 700, color: '#FFFFFF' }}>
                AI Prediction Logs & Geotechnical Audit Trail
              </h2>
              <span style={{
                fontSize: '10px',
                fontFamily: 'var(--font-mono)',
                fontWeight: 800,
                color: '#38BDF8',
                backgroundColor: 'rgba(56, 189, 248, 0.15)',
                border: '1px solid rgba(56, 189, 248, 0.35)',
                padding: '2px 8px',
                borderRadius: '4px'
              }}>
                DEMO AUDIT LOGS
              </span>
            </div>
            <p style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '2px' }}>
              Historical inference events, model validation outcomes, and shift mitigation actions.
            </p>
          </div>
        </div>

        {/* CSV Export Simulation Button */}
        <button
          onClick={handleExportCSV}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            padding: '8px 14px',
            backgroundColor: downloadSuccess ? '#10B981' : 'var(--bg-card)',
            border: '1px solid var(--border-subtle)',
            borderRadius: '6px',
            color: downloadSuccess ? '#090D14' : 'var(--text-primary)',
            fontSize: '12px',
            fontWeight: 700,
            transition: 'all 0.2s ease'
          }}
        >
          {downloadSuccess ? <CheckCircle2 size={14} /> : <Download size={14} />}
          <span>{downloadSuccess ? 'Audit CSV Downloaded' : 'Export Audit CSV'}</span>
        </button>
      </div>

      {/* Historical Trajectory Chart */}
      <div className="command-card">
        <RiskTrendChart data={telemetryHistory} height={220} title="Historical AI Risk Trend & Critical Thresholds" />
      </div>

      {/* Filter and Search Bar */}
      <div className="command-card" style={{ padding: 0 }}>
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
          {/* Risk Level Filter Pills */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap' }}>
            {['ALL', 'CRITICAL', 'HIGH', 'MODERATE', 'LOW'].map(level => (
              <button
                key={level}
                onClick={() => setFilterRisk(level)}
                style={{
                  padding: '4px 10px',
                  borderRadius: '4px',
                  fontSize: '11px',
                  fontFamily: 'var(--font-mono)',
                  fontWeight: 700,
                  backgroundColor: filterRisk === level ? 'rgba(56, 189, 248, 0.15)' : 'var(--bg-card)',
                  color: filterRisk === level ? '#38BDF8' : 'var(--text-secondary)',
                  border: `1px solid ${filterRisk === level ? 'rgba(56, 189, 248, 0.4)' : 'var(--border-subtle)'}`
                }}
              >
                {level}
              </button>
            ))}
          </div>

          {/* Search & Sort Controls */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
            <button
              onClick={() => setSortOrder(prev => prev === 'desc' ? 'asc' : 'desc')}
              className="topbar-btn"
              style={{ fontSize: '11px', fontFamily: 'var(--font-mono)' }}
              title="Toggle Sort by Risk Score"
            >
              <ArrowUpDown size={13} />
              <span>Score ({sortOrder.toUpperCase()})</span>
            </button>

            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '6px 12px',
              backgroundColor: 'var(--bg-card)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '6px',
              width: 'min(260px, 100%)'
            }}>
              <Search size={14} color="var(--text-tertiary)" />
              <input
                type="text"
                placeholder="Search history by zone or trigger..."
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
        </div>

        {/* Prediction Table */}
        <div className="command-table-container" style={{ border: 'none', borderRadius: 0 }}>
          <table className="command-table">
            <thead>
              <tr>
                <th>Log ID</th>
                <th>Timestamp</th>
                <th>Mine Zone</th>
                <th>Predicted Risk</th>
                <th>Score</th>
                <th>Confidence</th>
                <th>Precursor Mechanism</th>
                <th>Validation Protocol</th>
                <th style={{ textAlign: 'right' }}>Action Logged</th>
              </tr>
            </thead>
            <tbody>
              {filteredHistory.length === 0 ? (
                <tr>
                  <td colSpan="9" style={{ textAlign: 'center', padding: '32px', color: 'var(--text-tertiary)' }}>
                    No prediction history logs found matching current filters.
                  </td>
                </tr>
              ) : (
                filteredHistory.map(item => (
                  <tr
                    key={item.id}
                    className="clickable-row"
                    onClick={() => {
                      selectZoneById(item.zone);
                      setCurrentTab('mine-map');
                    }}
                  >
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--text-accent)', fontWeight: 600 }}>
                      {item.id}
                    </td>

                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--text-tertiary)' }}>
                      {item.timestamp}
                    </td>

                    <td>
                      <div style={{ fontWeight: 600, color: '#FFFFFF' }}>{item.zone}</div>
                      <div style={{ fontSize: '10px', color: 'var(--text-tertiary)' }}>{item.zoneName}</div>
                    </td>

                    <td>
                      <RiskBadge level={item.risk} size="sm" />
                    </td>

                    <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 800, fontSize: '13px', color: '#FFFFFF' }}>
                      {item.score}%
                    </td>

                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: '#10B981', fontWeight: 600 }}>
                      {item.confidence}
                    </td>

                    <td style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
                      {item.keyTrigger}
                    </td>

                    <td style={{ fontSize: '11px', color: 'var(--text-tertiary)' }}>
                      {item.validation}
                    </td>

                    <td style={{ textAlign: 'right', fontSize: '11px', fontWeight: 600, color: item.risk === 'CRITICAL' ? '#EF4444' : 'var(--text-primary)' }}>
                      {item.actionTaken}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default PredictionHistoryView;
