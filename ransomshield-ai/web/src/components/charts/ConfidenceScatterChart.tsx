"use client";

import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ZAxis } from "recharts";
import { useMetricsStore } from "@/store/useMetricsStore";

export default function ConfidenceScatterChart() {
  const { metrics } = useMetricsStore();

  // Transform data for scatter plot
  // X: Heuristic Score, Y: AI Confidence, Z: Dot Size (always 1 for standard dots)
  const data = metrics.map(m => ({
    id: m.run_id,
    x: m.heuristic_cumulative_score,
    y: m.ai_confidence_score * 100, // convert back to 0-100 for display
    z: 100,
    hallucinated: m.hallucination_detected,
    verdict: m.ai_verdict
  }));

  if (data.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <p className="text-gray-500">No data available for chart</p>
      </div>
    );
  }

  // Filter data by categories for different scatter colors
  const maliciousClean = data.filter(d => d.verdict === "MALICIOUS" && !d.hallucinated);
  const benignClean = data.filter(d => d.verdict === "BENIGN" && !d.hallucinated);
  const hallucinated = data.filter(d => d.hallucinated);

  return (
    <div className="flex-1 w-full h-full min-h-[300px]">
      <ResponsiveContainer width="100%" height="100%">
        <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
          <XAxis 
            type="number" 
            dataKey="x" 
            name="Heuristic Score" 
            stroke="#9ca3af"
            label={{ value: 'Mathematical Heuristics', position: 'bottom', fill: '#9ca3af' }} 
          />
          <YAxis 
            type="number" 
            dataKey="y" 
            name="AI Confidence" 
            unit="%" 
            stroke="#9ca3af"
            domain={[0, 100]}
            label={{ value: 'GenAI Confidence', angle: -90, position: 'left', fill: '#9ca3af' }} 
          />
          <ZAxis type="number" dataKey="z" range={[50, 100]} name="Weight" />
          
          <Tooltip 
            cursor={{ strokeDasharray: '3 3' }} 
            contentStyle={{ backgroundColor: 'rgba(17, 24, 39, 0.9)', border: '1px solid rgba(31, 41, 55, 0.8)', borderRadius: '8px', color: '#fff' }}
          />
          
          <Scatter name="Malicious" data={maliciousClean} fill="#ef4444" />
          <Scatter name="Benign" data={benignClean} fill="#06b6d4" />
          <Scatter name="Hallucinated" data={hallucinated} fill="#8b5cf6" />
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
}
