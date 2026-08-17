import { useState } from 'react'
import { Server, File, Network, Activity } from 'lucide-react'
import { format } from 'date-fns'

interface Props {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  report: any
}

export default function TelemetryViewer({ report }: Props) {
  const [activeTab, setActiveTab] = useState<'process' | 'file' | 'network'>('process')
  
  const raw = report.raw_telemetry;
  const hasRawTelemetry = !!raw;

  return (
    <div>
      <div className="tabs">
        <div className={`tab ${activeTab === 'process' ? 'active' : ''}`} onClick={() => setActiveTab('process')}>
          <Activity size={16} style={{display:'inline', marginRight:'8px', verticalAlign:'text-bottom'}}/>
          Processes ({raw?.processes?.length || 0})
        </div>
        <div className={`tab ${activeTab === 'file' ? 'active' : ''}`} onClick={() => setActiveTab('file')}>
          <File size={16} style={{display:'inline', marginRight:'8px', verticalAlign:'text-bottom'}}/>
          File System ({raw?.files?.length || 0})
        </div>
        <div className={`tab ${activeTab === 'network' ? 'active' : ''}`} onClick={() => setActiveTab('network')}>
          <Network size={16} style={{display:'inline', marginRight:'8px', verticalAlign:'text-bottom'}}/>
          Network Traffic ({raw?.networks?.length || 0})
        </div>
      </div>

      <div className="event-list">
        {!hasRawTelemetry && (
           <div style={{color: 'var(--text-secondary)', padding: '20px', textAlign: 'center'}}>
             No raw telemetry payload found.
           </div>
        )}
        
        {hasRawTelemetry && activeTab === 'process' && raw.processes.map((p: any, i: number) => (
          <div className="event-item" key={i}>
            <Activity className="event-icon" size={18} />
            <div className="event-details">
              <div className="event-title">
                {p.process_name} (PID: {p.pid})
                <span className="event-time">{p.timestamp ? format(new Date(p.timestamp), 'HH:mm:ss.SSS') : ''}</span>
              </div>
              <div className="event-desc">{p.command_line}</div>
              {p.parent_pid && <div style={{fontSize: '0.75rem', color: 'var(--text-secondary)'}}>Parent PID: {p.parent_pid}</div>}
            </div>
          </div>
        ))}

        {hasRawTelemetry && activeTab === 'file' && raw.files.map((f: any, i: number) => (
          <div className="event-item" key={i}>
            <File className="event-icon" size={18} color={f.is_encrypted ? 'var(--accent-danger)' : 'var(--text-secondary)'} />
            <div className="event-details">
              <div className="event-title">
                {f.action.toUpperCase()}
                <span className="event-time">{f.timestamp ? format(new Date(f.timestamp), 'HH:mm:ss.SSS') : ''}</span>
              </div>
              <div className="event-desc">{f.file_path}</div>
              <div style={{display: 'flex', gap: '8px', marginTop: '4px'}}>
                {f.entropy && <span className="badge" style={{background: f.entropy > 7.5 ? 'rgba(239,68,68,0.2)' : 'rgba(255,255,255,0.1)'}}>Entropy: {f.entropy.toFixed(2)}</span>}
                {f.is_encrypted && <span className="badge badge-critical">Encrypted</span>}
              </div>
            </div>
          </div>
        ))}

        {hasRawTelemetry && activeTab === 'network' && raw.networks.map((n: any, i: number) => (
          <div className="event-item" key={i}>
            <Network className="event-icon" size={18} color={n.destination_port === 4444 ? 'var(--accent-warning)' : 'var(--text-secondary)'} />
            <div className="event-details">
              <div className="event-title">
                {n.protocol} to {n.destination_ip}:{n.destination_port}
                <span className="event-time">{n.timestamp ? format(new Date(n.timestamp), 'HH:mm:ss.SSS') : ''}</span>
              </div>
              <div className="event-desc">{n.source_ip} -> {n.destination_ip}:{n.destination_port}</div>
              <div style={{fontSize: '0.75rem', color: 'var(--text-secondary)'}}>
                Sent: {n.bytes_sent}B | Recv: {n.bytes_received}B
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
