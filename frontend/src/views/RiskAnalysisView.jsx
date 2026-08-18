import React from 'react';
import {
  BrainCircuit,
  ShieldAlert,
  Activity,
  Cpu,
  Layers,
  CheckCircle2,
  Clock,
  ArrowUpRight,
  Sparkles,
  FileText,
  AlertTriangle
} from 'lucide-react';
import { useMineGuard } from '../context/MineGuardContext';
import { RiskBadge, StatusBadge } from '../components/common/StatusBadge';
import RiskTrendChart from '../components/charts/RiskTrendChart';
import FeatureImportanceBar from '../components/charts/FeatureImportanceBar';
import { MOCK_AI_MODEL_INFO } from '../data/mockPredictions';

export function RiskAnalysisView() {
  const { currentRisk, riskFactors, predictionHistory, telemetryHistory, selectZoneById, setCurrentTab } = useMineGuard();

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '22px' }}>
      {/* Top Banner with AI Warning */}
      <div style={{
        padding: '16px 20px',
        backgroundColor: 'var(--bg-topbar)',
        border: '1px solid rgba(56, 189, 248, 0.3)',
        borderRadius: '8px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '12px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ padding: '8px', borderRadius: '6px', backgroundColor: 'rgba(56, 189, 248, 0.15)', color: '#38BDF8' }}>
            <BrainCircuit size={20} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <h2 style={{ fontFamily: 'var(--font-heading)', fontSize: '15px', fontWeight: 700, color: '#FFFFFF' }}>
                AI Geotechnical Risk & Rockfall Explainability Engine
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
                DEMO AI OUTPUT
              </span>
            </div>
            <p style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '2px' }}>
              Multi-sensor spatio-temporal graph neural network analyzing continuous strain rates, pore pressures, and seismic waveform kinematics.
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--text-tertiary)' }}>
          <span>MODEL: {MOCK_AI_MODEL_INFO.version}</span>
          <span>•</span>
          <span>LATENCY: {MOCK_AI_MODEL_INFO.inferenceLatency}</span>
        </div>
      </div>

      {/* 4 Core AI Output KPI Tiles */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
        <div className="command-card" style={{ borderLeft: '4px solid #F97316' }}>
          <span style={{ fontSize: '11px', color: 'var(--text-tertiary)', textTransform: 'uppercase', fontFamily: 'var(--font-heading)', fontWeight: 700 }}>
            CURRENT RISK
          </span>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '6px' }}>
            <span style={{ fontSize: '28px', fontWeight: 800, fontFamily: 'var(--font-mono)', color: currentRisk.currentRisk === 'CRITICAL' ? '#EF4444' : '#F97316' }}>
              {currentRisk.currentRisk}
            </span>
          </div>
          <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Primary target: <strong>{currentRisk.affectedPrimaryZone}</strong>
          </div>
        </div>

        <div className="command-card">
          <span style={{ fontSize: '11px', color: 'var(--text-tertiary)', textTransform: 'uppercase', fontFamily: 'var(--font-heading)', fontWeight: 700 }}>
            RISK SCORE
          </span>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '4px', marginTop: '6px' }}>
            <span style={{ fontSize: '28px', fontWeight: 800, fontFamily: 'var(--font-mono)', color: '#FFFFFF' }}>
              {currentRisk.riskScore}
            </span>
            <span style={{ fontSize: '14px', color: 'var(--text-tertiary)' }}>/ 100</span>
          </div>
          <div style={{ fontSize: '11px', color: '#EF4444', fontWeight: 600, marginTop: '4px' }}>
            Threshold exceeded (Warning: 60, Crit: 80)
          </div>
        </div>

        <div className="command-card">
          <span style={{ fontSize: '11px', color: 'var(--text-tertiary)', textTransform: 'uppercase', fontFamily: 'var(--font-heading)', fontWeight: 700 }}>
            PREDICTION STATUS
          </span>
          <div style={{ fontSize: '16px', fontWeight: 700, fontFamily: 'var(--font-mono)', color: '#F97316', marginTop: '8px' }}>
            {currentRisk.predictionStatus}
          </div>
          <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '6px' }}>
            Estimated time to failure: <strong>{currentRisk.projectedTimeToCritical}</strong>
          </div>
        </div>

        <div className="command-card">
          <span style={{ fontSize: '11px', color: 'var(--text-tertiary)', textTransform: 'uppercase', fontFamily: 'var(--font-heading)', fontWeight: 700 }}>
            MODEL CONFIDENCE
          </span>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '4px', marginTop: '6px' }}>
            <span style={{ fontSize: '28px', fontWeight: 800, fontFamily: 'var(--font-mono)', color: '#10B981' }}>
              {currentRisk.confidence}
            </span>
          </div>
          <div style={{ fontSize: '11px', color: 'var(--text-tertiary)', marginTop: '4px' }}>
            F1-Score: {MOCK_AI_MODEL_INFO.f1Score} | ROC-AUC: {MOCK_AI_MODEL_INFO.rocAuc}
          </div>
        </div>
      </div>

      {/* Main Two-Column: Factor Decomposition vs 24H Risk Curve */}
      <div className="grid-two-column">
        {/* Risk Factor Decomposition */}
        <div className="command-card">
          <div className="card-header-row">
            <div className="card-title-group">
              <Layers size={16} color="var(--text-accent)" />
              <h3 className="card-title">Geotechnical Risk Factor Weights</h3>
            </div>
            <span style={{ fontSize: '10px', color: 'var(--text-tertiary)', fontFamily: 'var(--font-mono)' }}>
              SHAP / Feature Attribution
            </span>
          </div>

          <FeatureImportanceBar factors={riskFactors} />
        </div>

        {/* 24-Hour Risk Curve */}
        <div className="command-card">
          <RiskTrendChart data={telemetryHistory} height={250} title="AI Predicted Risk Progression" />
          
          <div style={{ marginTop: '16px', padding: '12px', backgroundColor: 'var(--bg-card-subtle)', borderRadius: '6px', border: '1px solid var(--border-subtle)', fontSize: '12px', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
            <strong style={{ color: '#FFFFFF' }}>AI Model Inference Rationale: </strong>
            {currentRisk.modelSummary}
          </div>
        </div>
      </div>

      {/* Recent Prediction Timeline */}
      <div className="command-card" style={{ padding: 0 }}>
        <div style={{
          padding: '14px 18px',
          borderBottom: '1px solid var(--border-subtle)',
          backgroundColor: 'var(--bg-topbar)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <div className="card-title-group">
            <Clock size={16} color="#38BDF8" />
            <h3 className="card-title">Recent AI Prediction Event Timeline</h3>
          </div>
          <span style={{ fontSize: '10px', color: '#38BDF8', fontFamily: 'var(--font-mono)' }}>
            DEMO AUDIT LOGS
          </span>
        </div>

        <div className="command-table-container" style={{ border: 'none', borderRadius: 0 }}>
          <table className="command-table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Target Zone</th>
                <th>Predicted Risk</th>
                <th>Score</th>
                <th>Confidence</th>
                <th>Trigger Precursor</th>
                <th>Validation Protocol</th>
                <th style={{ textAlign: 'right' }}>Response Taken</th>
              </tr>
            </thead>
            <tbody>
              {predictionHistory.map(item => (
                <tr
                  key={item.id}
                  className="clickable-row"
                  onClick={() => {
                    selectZoneById(item.zone);
                    setCurrentTab('mine-map');
                  }}
                >
                  <td style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--text-tertiary)' }}>
                    {item.timestamp}
                  </td>
                  <td>
                    <span style={{ fontWeight: 600, color: 'var(--text-accent)' }}>{item.zone}</span>
                    <span style={{ fontSize: '10px', color: 'var(--text-tertiary)', marginLeft: '6px' }}>({item.zoneName})</span>
                  </td>
                  <td>
                    <RiskBadge level={item.risk} size="sm" />
                  </td>
                  <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: '#FFFFFF' }}>
                    {item.score}%
                  </td>
                  <td style={{ fontFamily: 'var(--font-mono)', color: '#10B981' }}>
                    {item.confidence}
                  </td>
                  <td style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
                    {item.keyTrigger}
                  </td>
                  <td style={{ fontSize: '11px', color: 'var(--text-tertiary)' }}>
                    {item.validation}
                  </td>
                  <td style={{ textAlign: 'right', fontSize: '11px', fontWeight: 600, color: item.risk === 'CRITICAL' ? '#EF4444' : '#FFFFFF' }}>
                    {item.actionTaken}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default RiskAnalysisView;
