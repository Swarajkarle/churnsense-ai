"use client";

import { useQuery } from "@tanstack/react-query";
import { analyticsApi } from "@/lib/api";
import type { OverviewAnalytics, ChurnTrendPoint, SegmentAnalytics } from "@/types";
import {
  ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip,
  BarChart, Bar, CartesianGrid, PieChart, Pie, Cell,
} from "recharts";
import { BarChart3 } from "lucide-react";

export default function AnalyticsPage() {
  const { data: overview } = useQuery<OverviewAnalytics>({
    queryKey: ["analytics-overview"],
    queryFn: () => analyticsApi.overview().then((r) => r.data),
  });
  const { data: trend } = useQuery<ChurnTrendPoint[]>({
    queryKey: ["churn-trend"],
    queryFn: () => analyticsApi.churnTrend().then((r) => r.data),
  });
  const { data: segments } = useQuery<SegmentAnalytics>({
    queryKey: ["segments"],
    queryFn: () => analyticsApi.segments().then((r) => r.data),
  });

  const RISK_COLORS: Record<string, string> = {
    low: "#10b981", medium: "#f59e0b", high: "#ef4444", critical: "#7c3aed",
  };

  return (
    <div className="p-8 space-y-8 animate-fade-in">
      <div className="section-header">
        <div>
          <h1 className="section-title">Exploratory Analytics</h1>
          <p className="section-subtitle">Deep-dive into churn patterns across your customer base</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Churn Trend */}
        <div className="glass-card">
          <h2 className="text-sm font-semibold text-white mb-4">Monthly Churn Rate Trend</h2>
          {trend && trend.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={trend}>
                <CartesianGrid strokeDasharray="3 3" stroke="#2a2a45" />
                <XAxis dataKey="period" tick={{ fill: "#94a3b8", fontSize: 10 }} />
                <YAxis tick={{ fill: "#94a3b8", fontSize: 10 }} tickFormatter={(v) => `${(v*100).toFixed(0)}%`} />
                <Tooltip contentStyle={{ background: "#161625", border: "1px solid #2a2a45", borderRadius: 8, fontSize: 12 }}
                  formatter={(v: number) => [`${(v*100).toFixed(1)}%`, "Churn Rate"]} />
                <Line type="monotone" dataKey="churn_rate" stroke="#6366f1" strokeWidth={2.5} dot={{ fill: "#6366f1", r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          ) : <EmptyViz />}
        </div>

        {/* Risk Distribution */}
        <div className="glass-card">
          <h2 className="text-sm font-semibold text-white mb-4">Risk Level Distribution</h2>
          {segments?.risk_distribution && segments.risk_distribution.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie data={segments.risk_distribution} dataKey="count" nameKey="risk_level"
                  cx="50%" cy="50%" outerRadius={85}
                  label={({ risk_level, percent }) => `${risk_level} ${((percent||0)*100).toFixed(0)}%`}>
                  {segments.risk_distribution.map((e) => (
                    <Cell key={e.risk_level} fill={RISK_COLORS[e.risk_level] || "#6366f1"} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ background: "#161625", border: "1px solid #2a2a45", borderRadius: 8, fontSize: 12 }} />
              </PieChart>
            </ResponsiveContainer>
          ) : <EmptyViz />}
        </div>

        {/* By Contract */}
        <div className="glass-card">
          <h2 className="text-sm font-semibold text-white mb-4">Churn Rate by Contract Type</h2>
          {segments?.by_contract && segments.by_contract.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={segments.by_contract}>
                <CartesianGrid strokeDasharray="3 3" stroke="#2a2a45" />
                <XAxis dataKey="contract_type" tick={{ fill: "#94a3b8", fontSize: 10 }} />
                <YAxis tick={{ fill: "#94a3b8", fontSize: 10 }} tickFormatter={(v) => `${(v*100).toFixed(0)}%`} />
                <Tooltip contentStyle={{ background: "#161625", border: "1px solid #2a2a45", borderRadius: 8, fontSize: 12 }}
                  formatter={(v: number) => [`${(v*100).toFixed(1)}%`, "Churn Rate"]} />
                <Bar dataKey="churn_rate" fill="#6366f1" radius={[6,6,0,0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : <EmptyViz />}
        </div>

        {/* By Payment Method */}
        <div className="glass-card">
          <h2 className="text-sm font-semibold text-white mb-4">Churn Rate by Payment Method</h2>
          {segments?.by_payment_method && segments.by_payment_method.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={segments.by_payment_method} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#2a2a45" />
                <XAxis type="number" tick={{ fill: "#94a3b8", fontSize: 10 }} tickFormatter={(v) => `${(v*100).toFixed(0)}%`} />
                <YAxis dataKey="payment_method" type="category" tick={{ fill: "#94a3b8", fontSize: 9 }} width={120} />
                <Tooltip contentStyle={{ background: "#161625", border: "1px solid #2a2a45", borderRadius: 8, fontSize: 12 }}
                  formatter={(v: number) => [`${(v*100).toFixed(1)}%`, "Churn Rate"]} />
                <Bar dataKey="churn_rate" fill="#06b6d4" radius={[0,6,6,0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : <EmptyViz />}
        </div>
      </div>
    </div>
  );
}

function EmptyViz() {
  return (
    <div className="h-48 flex items-center justify-center">
      <p className="text-xs text-slate-500 text-center">
        No data available yet.<br/>Run predictions to populate analytics.
      </p>
    </div>
  );
}
