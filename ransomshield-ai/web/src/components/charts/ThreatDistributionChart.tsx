"use client";

import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { useMetricsStore } from "@/store/useMetricsStore";

export default function ThreatDistributionChart() {
  const { metrics } = useMetricsStore();

  const data = [
    { name: "Malicious", value: metrics.filter(m => m.ai_verdict === "MALICIOUS").length, color: "#ef4444" }, // alert-red
    { name: "Benign", value: metrics.filter(m => m.ai_verdict === "BENIGN").length, color: "#06b6d4" },       // cyber-cyan
    { name: "Unknown", value: metrics.filter(m => m.ai_verdict === "UNKNOWN").length, color: "#9ca3af" }      // gray
  ].filter(item => item.value > 0);

  if (data.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <p className="text-gray-500">No data available for chart</p>
      </div>
    );
  }

  return (
    <div className="flex-1 w-full h-full min-h-[300px]">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={80}
            outerRadius={110}
            paddingAngle={5}
            dataKey="value"
            stroke="none"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip 
            contentStyle={{ backgroundColor: 'rgba(17, 24, 39, 0.9)', border: '1px solid rgba(31, 41, 55, 0.8)', borderRadius: '8px' }}
            itemStyle={{ color: '#fff' }}
          />
          <Legend verticalAlign="bottom" height={36} iconType="circle" />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
