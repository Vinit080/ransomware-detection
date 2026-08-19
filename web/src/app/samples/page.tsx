"use client";

import { useState, useEffect, useRef } from "react";
import { Upload, Play, Terminal, TerminalSquare, RefreshCw } from "lucide-react";

interface TelemetryEvent {
  id: number;
  timestamp: string;
  source: string;
  event: string;
  details: string;
}

const MOCK_EVENTS = [
  { source: "kernel32.dll", event: "ProcessCreate", details: '{"image": "cmd.exe", "pid": 4192, "parent": "explorer.exe"}' },
  { source: "ntdll.dll", event: "ApiHook", details: '{"function": "NtWriteVirtualMemory", "target_pid": 4192}' },
  { source: "WS2_32.dll", event: "NetworkConnect", details: '{"ip": "185.15.22.1", "port": 443, "protocol": "TCP"}' },
  { source: "advapi32.dll", event: "RegSetValue", details: '{"key": "HKCU\\\\Software\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\Run", "value": "Updater"}' },
  { source: "kernel32.dll", event: "FileWrite", details: '{"path": "C:\\\\Users\\\\Admin\\\\Documents\\\\Important.docx.locked", "bytes": 10240}' },
  { source: "kernel32.dll", event: "FileDelete", details: '{"path": "C:\\\\Users\\\\Admin\\\\Documents\\\\Important.docx"}' },
  { source: "crypt32.dll", event: "CryptoAPI", details: '{"function": "CryptGenKey", "alg": "RSA"}' },
];

export default function SamplesSandbox() {
  const [isRunning, setIsRunning] = useState(false);
  const [logs, setLogs] = useState<TelemetryEvent[]>([]);
  const terminalRef = useRef<HTMLDivElement>(null);

  // Auto-scroll terminal
  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [logs]);

  // Simulate streaming telemetry
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isRunning) {
      interval = setInterval(() => {
        setLogs(prev => {
          if (prev.length > 100) return prev; // Stop after 100 events to prevent memory issues in mock
          const randomEvent = MOCK_EVENTS[Math.floor(Math.random() * MOCK_EVENTS.length)];
          const newEvent = {
            id: Date.now(),
            timestamp: new Date().toISOString().split('T')[1].replace('Z', ''),
            ...randomEvent
          };
          return [...prev, newEvent];
        });
      }, 150); // Stream an event every 150ms
    }
    return () => clearInterval(interval);
  }, [isRunning]);

  const handleStartSimulation = () => {
    setLogs([]);
    setIsRunning(true);
    setTimeout(() => {
      setIsRunning(false);
    }, 15000); // Auto-stop after 15 seconds
  };

  return (
    <div className="flex flex-col h-full space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-white">Sandbox Execution</h1>
        <p className="text-gray-400 mt-1">Upload samples and monitor live OS telemetry.</p>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Upload Panel */}
        <div className="lg:col-span-1 enterprise-panel p-6 flex flex-col gap-6">
          <h2 className="text-xl font-bold">Submit Sample</h2>
          
          <div className="flex-1 border-2 border-dashed border-panel-border rounded flex flex-col items-center justify-center p-6 text-center hover:bg-white/5 transition-colors cursor-pointer group bg-black/50">
            <div className="p-4 bg-cyber-cyan/10 rounded-full mb-4 group-hover:scale-110 transition-transform">
              <Upload className="h-8 w-8 text-cyber-cyan" />
            </div>
            <p className="font-semibold text-gray-300">Drag & Drop Executable</p>
            <p className="text-sm text-gray-500 mt-2">Supports .exe, .dll, .pdf, .docx</p>
            <button className="mt-6 px-4 py-2 rounded bg-black border border-panel-border text-sm hover:border-cyber-cyan transition-colors">
              Browse Files
            </button>
          </div>

          <button 
            onClick={handleStartSimulation}
            disabled={isRunning}
            className={`w-full py-3 rounded flex items-center justify-center gap-2 font-bold transition-all ${
              isRunning 
                ? "bg-gray-800 text-gray-500 cursor-not-allowed"
                : "bg-cyber-cyan text-black shadow-[0_0_15px_rgba(6,182,212,0.3)] hover:shadow-[0_0_25px_rgba(6,182,212,0.5)]"
            }`}
          >
            {isRunning ? (
              <><RefreshCw className="h-5 w-5 animate-spin" /> Executing in Sandbox...</>
            ) : (
              <><Play className="h-5 w-5" /> Simulate Execution</>
            )}
          </button>
        </div>

        {/* Live Terminal Panel */}
        <div className="lg:col-span-2 enterprise-panel flex flex-col overflow-hidden">
          <div className="p-3 border-b border-panel-border bg-black flex items-center justify-between">
            <div className="flex items-center gap-2">
              <TerminalSquare className="h-5 w-5 text-cyber-cyan" />
              <span className="font-mono text-sm tracking-wider font-bold">ETW Telemetry Stream</span>
            </div>
            <div className="flex gap-2">
              <div className="w-3 h-3 rounded-full bg-red-500"></div>
              <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
              <div className="w-3 h-3 rounded-full bg-green-500"></div>
            </div>
          </div>
          
          <div 
            ref={terminalRef}
            className="flex-1 p-4 font-mono text-xs md:text-sm overflow-y-auto bg-[#0a0a0a]"
          >
            {logs.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-gray-600 gap-3">
                <Terminal className="h-12 w-12 opacity-20" />
                <p>Waiting for sandbox execution...</p>
              </div>
            ) : (
              <div className="space-y-1">
                {logs.map((log) => (
                  <div key={log.id} className="flex gap-3 hover:bg-white/5 p-1 rounded">
                    <span className="text-gray-500 shrink-0">[{log.timestamp}]</span>
                    <span className="text-cyber-purple w-24 shrink-0 truncate" title={log.source}>{log.source}</span>
                    <span className="text-alert-red font-bold w-32 shrink-0">{log.event}</span>
                    <span className="text-cyber-cyan break-all">{log.details}</span>
                  </div>
                ))}
                {isRunning && (
                  <div className="flex items-center gap-2 text-cyber-cyan mt-2">
                    <span className="animate-pulse">_</span>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
