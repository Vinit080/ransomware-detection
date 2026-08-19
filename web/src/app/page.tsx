"use client";

import { useEffect, useState } from "react";

export default function Home() {
  const [status, setStatus] = useState<string>("Initializing...");

  useEffect(() => {
    // Test the API proxy to the FastAPI backend
    fetch("/api/v1/auth/login", { method: "POST" })
      .then((res) => {
        if (res.status === 422 || res.status === 200 || res.status === 401) {
          setStatus("Backend Online");
        } else {
          setStatus(`Error: HTTP ${res.status}`);
        }
      })
      .catch(() => setStatus("Backend Offline"));
  }, []);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-8">
      <main className="flex flex-col items-center gap-12 w-full max-w-4xl">
        <div className="text-center space-y-4">
          <h1 className="text-5xl font-extrabold tracking-tight bg-gradient-to-r from-cyber-cyan to-cyber-purple bg-clip-text text-transparent">
            RansomShield AI
          </h1>
          <p className="text-lg text-gray-400 max-w-2xl mx-auto">
            Advanced Zero-Day Ransomware Sandbox & Heuristics Engine
          </p>
        </div>

        <div className="glass-panel p-8 w-full">
          <div className="flex items-center justify-between border-b border-panel-border pb-6 mb-6">
            <div>
              <h2 className="text-2xl font-bold text-white">System Status</h2>
              <p className="text-sm text-gray-400">Core API Connection</p>
            </div>
            <div className="flex items-center gap-3">
              <div className="relative flex h-4 w-4">
                {status === "Backend Online" ? (
                  <>
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyber-cyan opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-4 w-4 bg-cyber-cyan"></span>
                  </>
                ) : (
                  <span className="relative inline-flex rounded-full h-4 w-4 bg-alert-red"></span>
                )}
              </div>
              <span className="font-mono text-sm tracking-widest uppercase">
                {status}
              </span>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-4 rounded-lg bg-black/40 border border-panel-border">
              <h3 className="text-gray-400 text-sm mb-1 uppercase tracking-wider">Active Samples</h3>
              <p className="text-3xl font-bold text-cyber-cyan">0</p>
            </div>
            <div className="p-4 rounded-lg bg-black/40 border border-panel-border">
              <h3 className="text-gray-400 text-sm mb-1 uppercase tracking-wider">Threats Blocked</h3>
              <p className="text-3xl font-bold text-alert-red">0</p>
            </div>
            <div className="p-4 rounded-lg bg-black/40 border border-panel-border">
              <h3 className="text-gray-400 text-sm mb-1 uppercase tracking-wider">AI Confidence</h3>
              <p className="text-3xl font-bold text-cyber-purple">N/A</p>
            </div>
          </div>
        </div>
        
        <div className="w-full flex gap-4 justify-center">
          <button className="px-6 py-3 rounded-full bg-cyber-cyan text-black font-semibold shadow-[0_0_15px_rgba(6,182,212,0.5)] hover:shadow-[0_0_25px_rgba(6,182,212,0.7)] transition-all">
            Enter Dashboard
          </button>
          <button className="px-6 py-3 rounded-full border border-panel-border text-white hover:bg-white/5 transition-all">
            View Analytics
          </button>
        </div>
      </main>
    </div>
  );
}
