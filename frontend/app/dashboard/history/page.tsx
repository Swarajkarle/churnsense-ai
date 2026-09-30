"use client";

import { useQuery } from "@tanstack/react-query";
import { predictionApi } from "@/lib/api";
import type { Prediction } from "@/types";
import { History, TrendingDown } from "lucide-react";

export default function HistoryPage() {
  const { data: predictions = [], isLoading } = useQuery<Prediction[]>({
    queryKey: ["prediction-history"],
    queryFn: () => predictionApi.list(1, 50).then((r) => r.data),
  });

  return (
    <div className="p-8 space-y-6 animate-fade-in">
      <div className="section-header">
        <div>
          <h1 className="section-title">Prediction History</h1>
          <p className="section-subtitle">All recent churn predictions across your organization</p>
        </div>
      </div>
      <div className="glass-card p-0 overflow-hidden">
        {isLoading ? (
          <div className="p-6 space-y-3">
            {[1,2,3,4,5].map((i) => <div key={i} className="skeleton h-12 rounded-xl" />)}
          </div>
        ) : predictions.length === 0 ? (
          <div className="py-16 text-center">
            <History className="w-10 h-10 text-slate-600 mx-auto mb-3" />
            <p className="text-sm text-slate-400">No predictions yet</p>
          </div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Prediction ID</th>
                <th>Customer</th>
                <th>Probability</th>
                <th>Risk Level</th>
                <th>Predicted</th>
                <th>Mode</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              {predictions.map((p) => (
                <tr key={p.id}>
                  <td className="font-mono text-xs text-slate-400">{p.id.slice(0, 12)}</td>
                  <td className="text-xs">{p.customer_id?.slice(0, 12) || "—"}</td>
                  <td className="font-semibold">{(p.churn_probability * 100).toFixed(1)}%</td>
                  <td><span className={`risk-badge risk-badge-${p.risk_level}`}>{p.risk_level}</span></td>
                  <td>{p.churn_prediction ? <span className="text-red-400">Churn</span> : <span className="text-emerald-400">Stay</span>}</td>
                  <td className="text-xs capitalize text-slate-400">{p.mode || "individual"}</td>
                  <td className="text-xs text-slate-400">{new Date(p.created_at).toLocaleString("en-IN")}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
