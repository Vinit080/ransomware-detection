import { useState } from 'react'
import { Activity, ShieldAlert, Bug, Terminal, FileCode2, PlayCircle, ShieldCheck } from 'lucide-react'
import './index.css'
import { RiskAssessment } from './types'
import RiskCard from './components/RiskCard'
import TelemetryViewer from './components/TelemetryViewer'

function App() {
  const [loading, setLoading] = useState(false)
  const [report, setReport] = useState<RiskAssessment | null>(null)
  
  const runSimulation = async (type: 'ransomware' | 'benign') => {
    setLoading(true)
    try {
      const res = await fetch(`http://localhost:8000/api/v1/simulate/${type}`)
      const data = await res.json()
      setReport(data.report)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app-container">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="logo-area">
          <Bug className="logo-icon" size={28} />
          <span>RansomwareDet API</span>
        </div>
        
        <nav className="nav-menu">
          <a className="nav-item active">
            <Activity size={20} />
            <span>Dashboard</span>
          </a>
          <a className="nav-item">
            <Terminal size={20} />
            <span>Telemetry Stream</span>
          </a>
          <a className="nav-item">
            <ShieldAlert size={20} />
            <span>YARA Rules</span>
          </a>
          <a className="nav-item">
            <FileCode2 size={20} />
            <span>LLM Reports</span>
          </a>
        </nav>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        <header className="dashboard-header">
          <div className="header-title">
            <h1>Analysis Dashboard</h1>
            <p>Real-time GenAI Ransomware Behavioral Sandbox</p>
          </div>
          
          <div className="action-buttons">
            <button className="btn btn-primary" onClick={() => runSimulation('benign')}>
              <ShieldCheck size={18} /> Run Benign Test
            </button>
            <button className="btn btn-danger" onClick={() => runSimulation('ransomware')}>
              <PlayCircle size={18} /> Detonate Ransomware
            </button>
          </div>
        </header>

        {loading && (
          <div className="loading-overlay">
            <div className="spinner"></div>
            <p>Executing payload in isolated VM...</p>
            <p style={{fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '8px'}}>Analyzing AES-256-GCM Telemetry stream...</p>
          </div>
        )}

        {report ? (
          <>
            <div className="grid-2">
              <RiskCard report={report} />
              
              <div className="glass-panel">
                <h3 style={{marginBottom: '16px'}}>Fusion Engine Assessment (GenAI)</h3>
                <div className="ai-explanation">
                  {report.genai_analysis}
                </div>
              </div>
            </div>

            <div className="glass-panel">
              <h3 style={{marginBottom: '16px'}}>Raw Telemetry Events</h3>
              <TelemetryViewer report={report} />
            </div>
          </>
        ) : (
          <div className="glass-panel" style={{ textAlign: 'center', padding: '64px', color: 'var(--text-secondary)' }}>
            <Bug size={48} style={{ opacity: 0.2, margin: '0 auto 16px' }} />
            <h2>Sandbox is Idle</h2>
            <p>Click "Detonate Ransomware" or "Run Benign Test" to inject a payload and begin telemetry analysis.</p>
          </div>
        )}
      </main>
    </div>
  )
}

export default App
