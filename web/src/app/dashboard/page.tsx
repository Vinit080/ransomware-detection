"use client";

import { useEffect } from "react";
import { Activity, ShieldAlert, Cpu, Loader2, AlertTriangle } from "lucide-react";
import { useMetricsStore } from "@/store/useMetricsStore";
import ThreatDistributionChart from "@/components/charts/ThreatDistributionChart";
import ConfidenceScatterChart from "@/components/charts/ConfidenceScatterChart";

export default function Dashboard() {
  const { totalScans, maliciousCount, avgConfidence, isLoading, error, fetchMetrics } = useMetricsStore();

  useEffect(() => {
    fetchMetrics();
  }, [fetchMetrics]);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white">Dashboard Overview</h1>
          <p className="text-gray-400 mt-1">Real-time metrics from the Sandbox Orchestrator</p>
        </div>
        
        {isLoading && (
          <div className="flex items-center gap-2 text-cyber-cyan">
            <Loader2 className="h-4 w-4 animate-spin" />
            <span className="text-sm">Syncing Data...</span>
          </div>
        )}
      </div>
      
      {error && (
        <div className="p-4 bg-alert-red/20 border border-alert-red rounded-lg flex items-center gap-3 text-alert-red">
          <AlertTriangle className="h-5 w-5" />
          <p>Failed to load API data: {error}</p>
        </div>
      )}
      
      {/* Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="enterprise-panel p-6 flex flex-col gap-2">
          <div className="flex items-center gap-2 text-gray-400">
            <Activity className="h-5 w-5 text-cyber-cyan" />
            <h3 className="font-semibold uppercase tracking-wider text-sm">Total Scans</h3>
          </div>
          <p className="text-4xl font-bold">{totalScans}</p>
        </div>
        
        <div className="enterprise-panel p-6 flex flex-col gap-2">
          <div className="flex items-center gap-2 text-gray-400">
            <ShieldAlert className="h-5 w-5 text-alert-red" />
            <h3 className="font-semibold uppercase tracking-wider text-sm">Malicious Detected</h3>
          </div>
          <p className="text-4xl font-bold">{maliciousCount}</p>
        </div>
        
        <div className="enterprise-panel p-6 flex flex-col gap-2">
          <div className="flex items-center gap-2 text-gray-400">
            <Cpu className="h-5 w-5 text-cyber-purple" />
            <h3 className="font-semibold uppercase tracking-wider text-sm">Avg. AI Confidence</h3>
          </div>
          <p className="text-4xl font-bold">{avgConfidence}%</p>
        </div>
      </div>
      
      {/* Main Charts Area */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="enterprise-panel p-6 min-h-[400px] flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold">Threat Distribution</h2>
            <div className="flex gap-2">
              <span className="flex items-center text-xs text-gray-400 gap-1"><div className="w-2 h-2 rounded-full bg-alert-red"></div> Malicious</span>
              <span className="flex items-center text-xs text-gray-400 gap-1"><div className="w-2 h-2 rounded-full bg-cyber-cyan"></div> Benign</span>
            </div>
          </div>
          <div className="flex-1 border border-dashed border-panel-border rounded-lg flex items-center justify-center bg-black/20">
            <ThreatDistributionChart />
          </div>
        </div>
        
        <div className="enterprise-panel p-6 min-h-[400px] flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold">Confidence Matrix</h2>
            <div className="flex gap-2">
              <span className="flex items-center text-xs text-gray-400 gap-1"><div className="w-2 h-2 rounded-full bg-cyber-purple"></div> Hallucinated</span>
            </div>
          </div>
          <div className="flex-1 border border-dashed border-panel-border rounded-lg flex items-center justify-center p-4 bg-black/20">
            <ConfidenceScatterChart />
          </div>
        </div>
      </div>
    </div>
  );
}
