"use client";

import { useQuery } from "@tanstack/react-query";
import { analyticsApi } from "@/lib/api";
import type { OverviewAnalytics, ChurnTrendPoint, SegmentAnalytics } from "@/types";
import {
  Users, AlertTriangle, TrendingDown, Activity,
  Target, Cpu, Percent, BarChart2, RefreshCw
} from "lucide-react";
import {
  ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip,
  PieChart, Pie, Cell, BarChart, Bar, CartesianGrid, Legend,
} from "recharts";

/**
 * ChurnSense AI — Executive Dashboard
 * Displays real-time KPIs, churn trends, and segment analytics.
 * Empty states are shown when no data/model is available.
 */
export default function DashboardPage() {
  const { data: overview, isLoading: overviewLoading } = useQuery<OverviewAnalytics>({
    queryKey: ["analytics-overview"],
    queryFn: () => analyticsApi.overview().then((r) => r.data),
  });

  const { data: trendData } = useQuery<ChurnTrendPoint[]>({
    queryKey: ["churn-trend"],
    queryFn: () => analyticsApi.churnTrend().then((r) => r.data),
  });

  const { data: segments } = useQuery<SegmentAnalytics>({
    queryKey: ["segments"],
    queryFn: () => analyticsApi.segments().then((r) => r.data),
  });

  const RISK_COLORS: Record<string, string> = {
    low: "#10b981",
    medium: "#f59e0b",
    high: "#ef4444",
    critical: "#7c3aed",
  };

  return (
    <div className="p-8 space-y-8 animate-fade-in">
      {/* Header */}
      <div className="section-header">
        <div>
          <h1 className="section-title">Executive Dashboard</h1>
          <p className="section-subtitle">Real-time churn intelligence for your organization</p>
        </div>
        <button
          onClick={() => window.location.reload()}
          className="btn-secondary text-xs py-2 px-3 gap-1.5"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          Refresh
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-5">
        <KpiCard
          icon={<Users className="w-5 h-5" />}
          label="Total Customers"
          value={overviewLoading ? "—" : String(overview?.total_customers ?? 0)}
          color="brand"
        />
        <KpiCard
          icon={<AlertTriangle className="w-5 h-5" />}
          label="At Risk"
          value={overviewLoading ? "—" : String(overview?.customers_at_risk ?? 0)}
          color="amber"
          sub="High + Critical risk"
        />
        <KpiCard
          icon={<TrendingDown className="w-5 h-5" />}
          label="Predicted Churners"
          value={overviewLoading ? "—" : String(overview?.predicted_churners ?? 0)}
          color="red"
        />
        <KpiCard
          icon={<Activity className="w-5 h-5" />}
          label="Avg Churn Probability"
          value={
            overviewLoading
              ? "—"
              : `${((overview?.average_churn_probability ?? 0) * 100).toFixed(1)}%`
          }
          color="cyan"
        />
      </div>

      {/* Model Metrics */}
      {overview?.active_model_name ? (
        <div className="glass-card">
          <div className="flex items-center justify-between mb-5">
            <div>
              <h2 className="text-sm font-semibold text-white">Active Model Performance</h2>
              <p className="text-xs text-slate-400 mt-0.5">{overview.active_model_name}</p>
            </div>
            <span className="risk-badge risk-badge-low">Deployed</span>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {[
              { label: "Accuracy", value: overview.active_model_accuracy, icon: <Target className="w-4 h-4" /> },
              { label: "Precision", value: overview.active_model_precision, icon: <Percent className="w-4 h-4" /> },
              { label: "Recall", value: overview.active_model_recall, icon: <BarChart2 className="w-4 h-4" /> },
              { label: "F1 Score", value: overview.active_model_f1, icon: <Activity className="w-4 h-4" /> },
              { label: "ROC-AUC", value: overview.active_model_roc_auc, icon: <Cpu className="w-4 h-4" /> },
            ].map((m) => (
              <div key={m.label} className="rounded-xl bg-surface p-4 text-center border border-surface-border">
                <div className="flex justify-center mb-2 text-brand-400">{m.icon}</div>
                <div className="text-xl font-bold text-white">
                  {m.value !== undefined && m.value !== null
                    ? `${(m.value * 100).toFixed(1)}%`
                    : "—"}
                </div>
                <div className="text-xs text-slate-400 mt-1">{m.label}</div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="glass-card text-center py-12">
          <Cpu className="w-10 h-10 text-slate-600 mx-auto mb-3" />
          <h3 className="text-sm font-medium text-slate-300">No Active Model</h3>
          <p className="text-xs text-slate-500 mt-1">
            Upload a dataset and train a model to see performance metrics here.
          </p>
        </div>
      )}

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Churn Trend */}
        <div className="glass-card">
          <h2 className="text-sm font-semibold text-white mb-5">Monthly Churn Trend</h2>
          {trendData && trendData.length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={trendData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#2a2a45" />
                <XAxis dataKey="period" tick={{ fill: "#94a3b8", fontSize: 11 }} />
                <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} tickFormatter={(v) => `${(v * 100).toFixed(0)}%`} />
                <Tooltip
                  contentStyle={{ background: "#161625", border: "1px solid #2a2a45", borderRadius: 8, fontSize: 12 }}
                  formatter={(v: number) => [`${(v * 100).toFixed(1)}%`, "Churn Rate"]}
                />
                <Line type="monotone" dataKey="churn_rate" stroke="#6366f1" strokeWidth={2} dot={{ fill: "#6366f1", r: 4 }} />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <EmptyChart message="No prediction history yet. Run predictions to see trend data." />
          )}
        </div>

        {/* Risk Distribution */}
        <div className="glass-card">
          <h2 className="text-sm font-semibold text-white mb-5">Risk Distribution</h2>
          {segments?.risk_distribution && segments.risk_distribution.length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={segments.risk_distribution}
                  dataKey="count"
                  nameKey="risk_level"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  label={({ risk_level, percent }) =>
                    `${risk_level} ${((percent || 0) * 100).toFixed(0)}%`
                  }
                  labelLine={false}
                >
                  {segments.risk_distribution.map((entry) => (
                    <Cell
                      key={entry.risk_level}
                      fill={RISK_COLORS[entry.risk_level] || "#6366f1"}
                    />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ background: "#161625", border: "1px solid #2a2a45", borderRadius: 8, fontSize: 12 }}
                />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <EmptyChart message="No risk data yet. Run predictions to see distribution." />
          )}
        </div>
      </div>

      {/* Contract Churn Breakdown */}
      <div className="glass-card">
        <h2 className="text-sm font-semibold text-white mb-5">Churn Rate by Contract Type</h2>
        {segments?.by_contract && segments.by_contract.length > 0 ? (
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={segments.by_contract}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2a2a45" />
              <XAxis dataKey="contract_type" tick={{ fill: "#94a3b8", fontSize: 11 }} />
              <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} tickFormatter={(v) => `${(v * 100).toFixed(0)}%`} />
              <Tooltip
                contentStyle={{ background: "#161625", border: "1px solid #2a2a45", borderRadius: 8, fontSize: 12 }}
                formatter={(v: number) => [`${(v * 100).toFixed(1)}%`, "Churn Rate"]}
              />
              <Bar dataKey="churn_rate" fill="#6366f1" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <EmptyChart message="No customer or contract data available yet." />
        )}
      </div>
    </div>
  );
}

/* ── Sub-components ─────────────────────────────────────────────────────── */

function KpiCard({
  icon, label, value, color = "brand", sub,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  color?: string;
  sub?: string;
}) {
  const colorMap: Record<string, string> = {
    brand: "text-brand-400 bg-brand-500/10",
    amber: "text-amber-400 bg-amber-500/10",
    red: "text-red-400 bg-red-500/10",
    cyan: "text-cyan-400 bg-cyan-500/10",
  };

  return (
    <div className="stat-card">
      <div className="flex items-start justify-between mb-4">
        <div className={`p-2 rounded-lg ${colorMap[color]}`}>{icon}</div>
      </div>
      <div className="text-3xl font-bold text-white mb-1">{value}</div>
      <div className="text-sm text-slate-400">{label}</div>
      {sub && <div className="text-xs text-slate-500 mt-0.5">{sub}</div>}
    </div>
  );
}

function EmptyChart({ message }: { message: string }) {
  return (
    <div className="h-48 flex items-center justify-center text-center">
      <p className="text-xs text-slate-500 max-w-48">{message}</p>
    </div>
  );
}
