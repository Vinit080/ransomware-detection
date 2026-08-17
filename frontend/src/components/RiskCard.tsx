import { ShieldAlert, Crosshair } from 'lucide-react'
import { RiskAssessment } from '../types'

interface Props {
  report: RiskAssessment
}

export default function RiskCard({ report }: Props) {
  const getSeverityClass = (level: string) => {
    if (level === 'CRITICAL') return 'critical'
    if (level === 'HIGH') return 'high'
    return 'low'
  }

  return (
    <div className="glass-panel risk-card">
      <div>
        <div className="risk-header">
          <div>
            <h3 style={{ color: 'var(--text-secondary)', marginBottom: '8px' }}>Risk Score</h3>
            <div className={`risk-score ${getSeverityClass(report.threat_level)}`}>
              {report.risk_score}
              <span style={{ fontSize: '1rem', color: 'var(--text-secondary)' }}>/100</span>
            </div>
          </div>
          <span className={`badge badge-${getSeverityClass(report.threat_level).toLowerCase()}`}>
            {report.threat_level}
          </span>
        </div>
        
        <div style={{ marginTop: '24px' }}>
          <h4 style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
            <ShieldAlert size={16} color="var(--accent-warning)" />
            Rule-Based Findings (YARA)
          </h4>
          
          {report.rule_based_findings.length === 0 ? (
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>No known signatures detected.</p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {report.rule_based_findings.map((hit, idx) => (
                <div key={idx} style={{ background: 'rgba(0,0,0,0.2)', padding: '10px', borderRadius: '6px' }}>
                  <div style={{ fontWeight: 600, color: 'var(--accent-danger)', fontSize: '0.9rem' }}>
                    {hit.rule}
                  </div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
                    {hit.meta.description || 'No description'}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
      
      <div style={{ marginTop: '24px', paddingTop: '16px', borderTop: '1px solid var(--panel-border)' }}>
        <h4 style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
          <Crosshair size={16} color="var(--accent-primary)" />
          Session Identifier
        </h4>
        <code style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{report.session_id}</code>
      </div>
    </div>
  )
}
