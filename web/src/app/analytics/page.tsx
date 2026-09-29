"use client";

import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import { Loader2, FileText, ChevronRight, AlertTriangle, ShieldCheck, ShieldAlert } from "lucide-react";
import { useMetricsStore, MetricRow } from "@/store/useMetricsStore";
import { useAuthStore } from "@/store/useAuthStore";

interface ReportData {
  run_id: string;
  markdown: string;
  cti_references: string[];
}

export default function Analytics() {
  const { metrics, isLoading: isMetricsLoading, error: metricsError, fetchMetrics } = useMetricsStore();
  const token = useAuthStore((state) => state.token);
  
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null);
  const [report, setReport] = useState<ReportData | null>(null);
  const [isReportLoading, setIsReportLoading] = useState(false);
  const [reportError, setReportError] = useState<string | null>(null);

  useEffect(() => {
    if (metrics.length === 0) {
      fetchMetrics();
    }
  }, [metrics.length, fetchMetrics]);

  const handleSelectRun = async (runId: string) => {
    setSelectedRunId(runId);
    setIsReportLoading(true);
    setReportError(null);
    
    try {
      if (!token) throw new Error("Unauthorized");
      
      const res = await fetch(`/api/v1/sandbox/runs/${runId}/report`, {
        headers: { "Authorization": `Bearer ${token}` }
      });
      
      if (!res.ok) {
        throw new Error(`Report not available (HTTP ${res.status})`);
      }
      
      const data = await res.json();
      setReport(data);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setReportError(err.message);
      } else {
        setReportError("An unknown error occurred.");
      }
      setReport(null);
    } finally {
      setIsReportLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full space-y-4">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-white">Analytics & Reports</h1>
        <p className="text-gray-400 mt-1">Review comprehensive AI-generated threat intelligence reports.</p>
      </div>
      
      <div className="flex flex-1 gap-6 overflow-hidden min-h-0">
        {/* Left Column: List of Runs */}
        <div className="w-1/3 enterprise-panel flex flex-col overflow-hidden">
          <div className="p-4 border-b border-panel-border bg-black">
            <h2 className="font-semibold text-lg flex items-center gap-2">
              <FileText className="h-5 w-5 text-cyber-cyan" />
              Completed Executions
            </h2>
          </div>
          
          <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-[#0a0a0a]">
            {isMetricsLoading && <div className="flex justify-center p-4"><Loader2 className="animate-spin text-cyber-cyan" /></div>}
            
            {!isMetricsLoading && metrics.map((run: MetricRow) => (
              <button
                key={run.run_id}
                onClick={() => handleSelectRun(run.run_id)}
                className={`w-full text-left p-3 rounded border transition-all ${
                  selectedRunId === run.run_id 
                    ? "bg-cyber-cyan/10 border-cyber-cyan shadow-[0_0_10px_rgba(6,182,212,0.2)]" 
                    : "bg-black border-panel-border hover:border-gray-500"
                }`}
              >
                <div className="flex justify-between items-start mb-1">
                  <span className="font-mono text-xs text-gray-400">{run.run_id.substring(0, 8)}...</span>
                  <span className="text-xs text-gray-500">{new Date(run.timestamp).toLocaleDateString()}</span>
                </div>
                <div className="flex items-center gap-2">
                  {run.ai_verdict === "MALICIOUS" ? (
                    <ShieldAlert className="h-4 w-4 text-alert-red" />
                  ) : (
                    <ShieldCheck className="h-4 w-4 text-cyber-cyan" />
                  )}
                  <span className="font-medium truncate">{run.sample_family || "Unknown"}</span>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Right Column: Markdown Report */}
        <div className="w-2/3 enterprise-panel flex flex-col overflow-hidden">
          {selectedRunId ? (
            <>
              <div className="p-4 border-b border-panel-border bg-black flex justify-between items-center">
                <h2 className="font-semibold text-lg font-mono">Report: {selectedRunId}</h2>
                <div className="px-3 py-1 bg-cyber-purple/20 text-cyber-purple text-xs font-bold rounded border border-cyber-purple/30">
                  RAG GENERATED
                </div>
              </div>
              <div className="flex-1 overflow-y-auto p-8 relative bg-[#0a0a0a]">
                {isReportLoading ? (
                  <div className="absolute inset-0 flex flex-col items-center justify-center gap-4 bg-[#0a0a0a]/90">
                    <Loader2 className="h-8 w-8 animate-spin text-cyber-cyan" />
                    <p className="text-gray-400 animate-pulse">Decrypting and streaming report...</p>
                  </div>
                ) : reportError ? (
                  <div className="flex flex-col items-center justify-center h-full text-alert-red gap-2">
                    <AlertTriangle className="h-12 w-12" />
                    <p>{reportError}</p>
                    <p className="text-gray-400 text-sm">Note: Only malicious files trigger a full report.</p>
                  </div>
                ) : report ? (
                  <article className="prose prose-invert prose-cyan max-w-none prose-headings:text-white prose-a:text-cyber-cyan">
                    <ReactMarkdown>{report.markdown}</ReactMarkdown>
                    
                    {report.cti_references && report.cti_references.length > 0 && (
                      <div className="mt-8 p-4 bg-black border border-panel-border rounded-lg">
                        <h3 className="text-cyber-purple font-bold mt-0 flex items-center gap-2">
                          <ChevronRight className="h-5 w-5" /> Threat Intelligence References
                        </h3>
                        <ul className="list-disc pl-5 mb-0 text-sm text-gray-300">
                          {report.cti_references.map((ref, i) => (
                            <li key={i}>{ref}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </article>
                ) : null}
              </div>
            </>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-gray-500 gap-4 bg-[#0a0a0a]">
              <FileText className="h-16 w-16 opacity-20" />
              <p>Select an execution run to view the AI-generated report.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
