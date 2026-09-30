"use client";

import { useQuery } from "@tanstack/react-query";
import { customerApi } from "@/lib/api";
import type { Customer } from "@/types";
import { useParams } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, User, AlertTriangle, TrendingDown, Lightbulb, Clock } from "lucide-react";
import { clsx } from "clsx";

/**
 * ChurnSense AI — Customer 360 Profile Page
 * Shows all available customer data, latest prediction, explanation, and recommendations.
 */
export default function CustomerDetailPage() {
  const { id } = useParams<{ id: string }>();

  const { data: customer, isLoading } = useQuery<Customer>({
    queryKey: ["customer", id],
    queryFn: () => customerApi.get(id).then((r) => r.data),
  });

  if (isLoading) {
    return (
      <div className="p-8 space-y-5 animate-fade-in">
        {[1, 2, 3].map((i) => <div key={i} className="skeleton h-32 rounded-2xl" />)}
      </div>
    );
  }

  if (!customer) {
    return (
      <div className="p-8 text-center py-32">
        <User className="w-12 h-12 text-slate-600 mx-auto mb-3" />
        <h2 className="text-lg font-semibold text-white">Customer Not Found</h2>
        <Link href="/dashboard/customers" className="mt-4 btn-secondary inline-flex">
          <ArrowLeft className="w-4 h-4" /> Back to Customers
        </Link>
      </div>
    );
  }

  const pred = customer.latest_prediction;
  const explanation = pred?.explanation;
  const recommendations = pred?.recommendations || [];

  return (
    <div className="p-8 space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link href="/dashboard/customers" className="btn-secondary py-2 px-3">
          <ArrowLeft className="w-4 h-4" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-white">
            {customer.name || customer.external_id || "Customer Profile"}
          </h1>
          <p className="text-sm text-slate-400 mt-0.5">Customer 360 View</p>
        </div>
        {pred && (
          <div className="ml-auto">
            <span className={`risk-badge risk-badge-${pred.risk_level} text-sm px-3 py-1`}>
              {pred.risk_level.toUpperCase()} RISK
            </span>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Profile */}
        <div className="lg:col-span-1 space-y-5">
          <div className="glass-card">
            <h2 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
              <User className="w-4 h-4 text-brand-400" />
              Customer Info
            </h2>
            <dl className="space-y-3">
              {[
                { label: "Customer ID", value: customer.external_id || customer.id.slice(0, 12) },
                { label: "Email", value: customer.email || "—" },
                { label: "Tenure", value: customer.tenure ? `${customer.tenure} months` : "—" },
                { label: "Contract", value: customer.contract_type || "—" },
                { label: "Monthly Charges", value: customer.monthly_charges ? `₹${customer.monthly_charges.toFixed(2)}` : "—" },
                { label: "Total Charges", value: customer.total_charges ? `₹${customer.total_charges.toFixed(2)}` : "—" },
                { label: "Payment Method", value: customer.payment_method || "—" },
              ].map(({ label, value }) => (
                <div key={label} className="flex justify-between items-start gap-2">
                  <dt className="text-xs text-slate-400">{label}</dt>
                  <dd className="text-xs text-slate-200 text-right">{value}</dd>
                </div>
              ))}
              {customer.services && customer.services.length > 0 && (
                <div>
                  <dt className="text-xs text-slate-400 mb-1.5">Services</dt>
                  <dd className="flex flex-wrap gap-1">
                    {customer.services.map((s) => (
                      <span key={s} className="rounded-full bg-brand-500/10 px-2 py-0.5 text-xs text-brand-300">
                        {s}
                      </span>
                    ))}
                  </dd>
                </div>
              )}
            </dl>
          </div>
        </div>

        {/* Right: Prediction + Explanation + Recommendations */}
        <div className="lg:col-span-2 space-y-5">
          {/* Churn Prediction */}
          {pred ? (
            <div className="glass-card">
              <h2 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-amber-400" />
                Churn Prediction
              </h2>
              <div className="flex items-center gap-6">
                <div className="text-5xl font-extrabold text-gradient">
                  {(pred.churn_probability * 100).toFixed(1)}%
                </div>
                <div>
                  <div className="text-sm font-medium text-slate-300">Churn Probability</div>
                  <div className="text-xs text-slate-500 mt-1">
                    Threshold: {(pred.prediction_threshold * 100).toFixed(0)}% ·{" "}
                    {pred.churn_prediction ? "Predicted to churn" : "Predicted to stay"}
                  </div>
                  <div className="mt-2">
                    <div className="progress-bar">
                      <div
                        className="progress-fill"
                        style={{ width: `${pred.churn_probability * 100}%` }}
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="glass-card text-center py-10">
              <TrendingDown className="w-8 h-8 text-slate-600 mx-auto mb-2" />
              <p className="text-sm text-slate-400">No prediction available for this customer</p>
              <Link href="/dashboard/predictions" className="mt-3 btn-primary inline-flex text-xs">
                Run Prediction
              </Link>
            </div>
          )}

          {/* SHAP Explanation */}
          {explanation && (
            <div className="glass-card">
              <h2 className="text-sm font-semibold text-white mb-1 flex items-center gap-2">
                <TrendingDown className="w-4 h-4 text-red-400" />
                Prediction Explanation
              </h2>
              <p className="text-xs text-slate-500 mb-4">
                ⚠️ These explanations describe the model&apos;s behavior on this input. They are not
                guaranteed causal explanations of why the customer will or will not churn.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h3 className="text-xs font-medium text-red-400 mb-2 uppercase tracking-wider">
                    Risk Factors
                  </h3>
                  <div className="space-y-2">
                    {explanation.top_risk_factors.map((f, i) => (
                      <FactorRow key={i} factor={f} type="risk" />
                    ))}
                    {explanation.top_risk_factors.length === 0 && (
                      <p className="text-xs text-slate-500">No significant risk factors identified</p>
                    )}
                  </div>
                </div>
                <div>
                  <h3 className="text-xs font-medium text-emerald-400 mb-2 uppercase tracking-wider">
                    Protective Factors
                  </h3>
                  <div className="space-y-2">
                    {explanation.top_protective_factors.map((f, i) => (
                      <FactorRow key={i} factor={f} type="protective" />
                    ))}
                    {explanation.top_protective_factors.length === 0 && (
                      <p className="text-xs text-slate-500">No protective factors identified</p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Recommendations */}
          {recommendations.length > 0 && (
            <div className="glass-card">
              <h2 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
                <Lightbulb className="w-4 h-4 text-amber-400" />
                Retention Recommendations
              </h2>
              <p className="text-xs text-slate-500 mb-4">
                Note: These recommendations are suggested actions informed by the model prediction.
                They do not guarantee churn prevention.
              </p>
              <div className="space-y-3">
                {recommendations.sort((a, b) => a.priority - b.priority).map((rec) => (
                  <div key={rec.id} className="rounded-xl border border-surface-border bg-surface p-4">
                    <div className="flex items-start justify-between gap-2 mb-1.5">
                      <h3 className="text-sm font-semibold text-white">{rec.title}</h3>
                      <span className="rounded-full bg-brand-500/10 px-2 py-0.5 text-xs text-brand-300 flex-shrink-0">
                        P{rec.priority}
                      </span>
                    </div>
                    <p className="text-xs text-slate-300 leading-relaxed">{rec.description}</p>
                    {rec.rationale && (
                      <p className="text-xs text-slate-500 mt-2 italic">
                        Why: {rec.rationale}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Prediction History */}
          {customer.prediction_history && customer.prediction_history.length > 0 && (
            <div className="glass-card">
              <h2 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
                <Clock className="w-4 h-4 text-slate-400" />
                Prediction History
              </h2>
              <div className="space-y-2">
                {customer.prediction_history.map((p) => (
                  <div key={p.id} className="flex items-center justify-between rounded-lg bg-surface px-4 py-2 border border-surface-border">
                    <span className="text-xs text-slate-400">
                      {new Date(p.created_at).toLocaleDateString("en-IN", {
                        day: "numeric", month: "short", year: "numeric",
                      })}
                    </span>
                    <span className="text-sm font-semibold text-white">
                      {(p.churn_probability * 100).toFixed(1)}%
                    </span>
                    <span className={`risk-badge risk-badge-${p.risk_level} text-xs`}>
                      {p.risk_level}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function FactorRow({ factor, type }: { factor: any; type: "risk" | "protective" }) {
  const isRisk = type === "risk";
  return (
    <div className="flex items-start gap-2 rounded-lg bg-surface p-2.5 border border-surface-border">
      <span className={`text-lg ${isRisk ? "text-red-400" : "text-emerald-400"}`}>
        {isRisk ? "↑" : "↓"}
      </span>
      <div className="flex-1 min-w-0">
        <div className="text-xs font-medium text-slate-200 truncate">{factor.feature}</div>
        <div className="text-xs text-slate-400 truncate">{factor.description}</div>
      </div>
      <div className="text-xs font-mono text-slate-400 flex-shrink-0">
        {factor.shap_value > 0 ? "+" : ""}{factor.shap_value.toFixed(3)}
      </div>
    </div>
  );
}
