import { create } from "zustand";
import { useAuthStore } from "./useAuthStore";

export interface MetricRow {
  run_id: string;
  timestamp: string;
  dataset_identifier: string;
  sample_family: string;
  heuristic_cumulative_score: number;
  ai_verdict: string;
  ai_confidence_score: number;
  hallucination_detected: boolean;
}

interface MetricsState {
  metrics: MetricRow[];
  totalScans: number;
  maliciousCount: number;
  avgConfidence: number;
  isLoading: boolean;
  error: string | null;
  fetchMetrics: () => Promise<void>;
}

export const useMetricsStore = create<MetricsState>((set) => ({
  metrics: [],
  totalScans: 0,
  maliciousCount: 0,
  avgConfidence: 0,
  isLoading: false,
  error: null,

  fetchMetrics: async () => {
    set({ isLoading: true, error: null });
    try {
      const token = useAuthStore.getState().token;
      if (!token) throw new Error("Unauthorized");

      const res = await fetch("/api/v1/metrics/export?format=json", {
        headers: {
          "Authorization": `Bearer ${token}`
        }
      });
      
      if (!res.ok) {
        throw new Error(`API Error: ${res.status}`);
      }
      
      const data = await res.json();
      const rows: MetricRow[] = data.metrics || [];
      
      // Calculate Aggregates
      const totalScans = rows.length;
      const maliciousCount = rows.filter(r => r.ai_verdict === "MALICIOUS").length;
      
      let sumConf = 0;
      let confCount = 0;
      rows.forEach(r => {
        if (r.ai_verdict !== "UNKNOWN") {
          sumConf += r.ai_confidence_score;
          confCount += 1;
        }
      });
      const avgConfidence = confCount > 0 ? (sumConf / confCount) * 100 : 0;

      set({
        metrics: rows,
        totalScans,
        maliciousCount,
        avgConfidence: Math.round(avgConfidence),
        isLoading: false
      });
      
    } catch (err: unknown) {
      if (err instanceof Error) {
        set({ error: err.message, isLoading: false });
      } else {
        set({ error: "An unknown error occurred.", isLoading: false });
      }
    }
  }
}));
