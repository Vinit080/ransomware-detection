export interface ProcessEvent {
  pid: number;
  process_name: str;
  command_line: string;
  parent_pid: number | null;
  timestamp: string;
}

export interface FileEvent {
  file_path: string;
  action: string;
  is_encrypted: boolean;
  entropy: number | null;
  timestamp: string;
}

export interface NetworkEvent {
  source_ip: string;
  destination_ip: string;
  destination_port: number;
  protocol: string;
  bytes_sent: number;
  bytes_received: number;
  timestamp: string;
}

export interface YaraHit {
  rule: string;
  meta: {
    description?: string;
    severity?: string;
  };
  strings: string[];
}

export interface RiskAssessment {
  session_id: string;
  risk_score: number;
  threat_level: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  rule_based_findings: YaraHit[];
  genai_analysis: string;
  rag_context_used: string;
}

export interface SimulationReport {
  status: string;
  report: RiskAssessment;
  raw_telemetry?: {
    processes: ProcessEvent[];
    files: FileEvent[];
    networks: NetworkEvent[];
  }
}
