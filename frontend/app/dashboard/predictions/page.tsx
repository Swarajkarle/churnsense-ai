"use client";

import { useState, useRef } from "react";
import { predictionApi } from "@/lib/api";
import type { Prediction } from "@/types";
import { toast } from "sonner";
import { Zap, Upload, Loader2, AlertTriangle, CheckCircle, TrendingDown } from "lucide-react";
import { clsx } from "clsx";

/**
 * ChurnSense AI — Churn Prediction Page
 * Supports both individual (form-based) and bulk (CSV) prediction modes.
 */
export default function PredictionsPage() {
  const [mode, setMode] = useState<"individual" | "bulk">("individual");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<Prediction | null>(null);
  const [bulkResults, setBulkResults] = useState<Prediction[]>([]);
  const fileRef = useRef<HTMLInputElement>(null);

  // Individual prediction fields with default values
  const [features, setFeatures] = useState<Record<string, string>>({
    tenure: "12",
    Contract: "Month-to-month",
    MonthlyCharges: "70.5",
    TotalCharges: "846.0",
    InternetService: "Fiber optic",
    PaymentMethod: "Electronic check",
    SeniorCitizen: "0",
    Partner: "No",
    Dependents: "No",
    PhoneService: "Yes",
    PaperlessBilling: "Yes",
  });
  const [threshold, setThreshold] = useState(0.5);

  const handleIndividualPredict = async () => {
    const cleanedFeatures: Record<string, any> = {};
    for (const [k, v] of Object.entries(features)) {
      cleanedFeatures[k] = isNaN(Number(v)) || v === "" ? v : Number(v);
    }
    setLoading(true);
    try {
      const res = await predictionApi.predictIndividual({ features: cleanedFeatures, threshold });
      setResult(res.data);
      toast.success("Prediction complete!");
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Prediction failed. Is a model activated?");
    } finally { setLoading(false); }
  };

  const handleBulkPredict = async () => {
    const file = fileRef.current?.files?.[0];
    if (!file) { toast.error("Select a CSV file for bulk prediction"); return; }
    setLoading(true);
    try {
      const res = await predictionApi.predictBulk(file, undefined, threshold);
      setBulkResults(res.data);
      toast.success(`${res.data.length} predictions complete!`);
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Bulk prediction failed");
    } finally { setLoading(false); }
  };

  const RISK_ICONS: Record<string, React.ReactNode> = {
    low: <CheckCircle className="w-5 h-5 text-emerald-400" />,
    medium: <AlertTriangle className="w-5 h-5 text-amber-400" />,
    high: <TrendingDown className="w-5 h-5 text-red-400" />,
    critical: <AlertTriangle className="w-5 h-5 text-purple-400" />,
  };

  return (
    <div className="p-8 space-y-8 animate-fade-in">
      <div className="section-header">
        <div>
          <h1 className="section-title">Churn Prediction</h1>
          <p className="section-subtitle">Run churn predictions for individual or multiple customers</p>
        </div>
      </div>

      {/* Mode Toggle */}
      <div className="flex gap-2 p-1 bg-surface rounded-xl border border-surface-border w-fit">
        {(["individual", "bulk"] as const).map((m) => (
          <button
            key={m}
            onClick={() => setMode(m)}
            className={clsx(
              "px-5 py-2 rounded-lg text-sm font-medium transition-all",
              mode === m
                ? "bg-brand-600 text-white shadow-brand"
                : "text-slate-400 hover:text-slate-200"
            )}
          >
            {m === "individual" ? "Individual" : "Bulk CSV"}
          </button>
        ))}
      </div>

      {mode === "individual" ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Input Form */}
          <div className="glass-card">
            <h2 className="text-sm font-semibold text-white mb-5 flex items-center gap-2">
              <Zap className="w-4 h-4 text-brand-400" />
              Customer Features
            </h2>
            <div className="grid grid-cols-2 gap-3 mb-4">
              {Object.keys(features).map((key) => (
                <div key={key}>
                  <label className="block text-xs font-medium text-slate-400 mb-1">{key}</label>
                  <input
                    type="text"
                    className="form-input py-2 text-xs"
                    value={features[key]}
                    onChange={(e) => setFeatures((f) => ({ ...f, [key]: e.target.value }))}
                    placeholder={key}
                  />
                </div>
              ))}
            </div>
            <div className="mb-4">
              <label className="block text-xs font-medium text-slate-400 mb-1">
                Threshold: {(threshold * 100).toFixed(0)}%
              </label>
              <input
                type="range"
                min="10" max="90" step="5"
                className="w-full"
                value={threshold * 100}
                onChange={(e) => setThreshold(Number(e.target.value) / 100)}
              />
            </div>
            <button
              id="predict-btn"
              onClick={handleIndividualPredict}
              disabled={loading}
              className="btn-primary w-full justify-center"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4" />}
              {loading ? "Running Prediction…" : "Predict Churn"}
            </button>
          </div>

          {/* Result */}
          <div className="glass-card">
            <h2 className="text-sm font-semibold text-white mb-5">Prediction Result</h2>
            {result ? (
              <div className="space-y-5">
                {/* Probability */}
                <div className="text-center py-4">
                  <div className="text-7xl font-extrabold text-gradient mb-2">
                    {(result.churn_probability * 100).toFixed(1)}%
                  </div>
                  <div className="text-sm text-slate-400">Churn Probability</div>
                  <div className="mt-4 progress-bar">
                    <div className="progress-fill" style={{ width: `${result.churn_probability * 100}%` }} />
                  </div>
                </div>

                <div className="flex items-center justify-center gap-4">
                  <div className="flex items-center gap-2">
                    {RISK_ICONS[result.risk_level]}
                    <span className={`risk-badge risk-badge-${result.risk_level} text-sm px-3 py-1.5`}>
                      {result.risk_level.toUpperCase()} RISK
                    </span>
                  </div>
                </div>

                {/* Key Risk Factors */}
                {result.explanation?.top_risk_factors && result.explanation.top_risk_factors.length > 0 && (
                  <div>
                    <h3 className="text-xs font-semibold text-red-400 mb-2 uppercase tracking-wider">
                      Top Risk Factors
                    </h3>
                    <div className="space-y-1.5">
                      {result.explanation.top_risk_factors.slice(0, 3).map((f, i) => (
                        <div key={i} className="flex items-center gap-2 text-xs text-slate-300 bg-surface rounded-lg px-3 py-2 border border-surface-border">
                          <span className="text-red-400">↑</span>
                          {f.description}
                        </div>
                      ))}
                    </div>
                    <p className="mt-2 text-xs text-slate-500 italic">
                      Explanations describe model behavior, not guaranteed causal factors.
                    </p>
                  </div>
                )}

                {/* Top Recommendation */}
                {result.recommendations[0] && (
                  <div className="rounded-xl border border-amber-500/20 bg-amber-500/5 p-4">
                    <h3 className="text-xs font-semibold text-amber-400 mb-1">
                      Top Recommendation
                    </h3>
                    <p className="text-xs text-slate-300">{result.recommendations[0].description}</p>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-16 text-center">
                <Zap className="w-10 h-10 text-slate-600 mb-3" />
                <p className="text-sm text-slate-400">No prediction yet</p>
                <p className="text-xs text-slate-500 mt-1">Fill in the customer features and click Predict</p>
              </div>
            )}
          </div>
        </div>
      ) : (
        /* Bulk Mode */
        <div className="glass-card max-w-xl">
          <h2 className="text-sm font-semibold text-white mb-5 flex items-center gap-2">
            <Upload className="w-4 h-4 text-brand-400" />
            Bulk CSV Prediction
          </h2>
          <p className="text-xs text-slate-400 mb-4">
            Upload a CSV with customer features. The same columns used during training are required.
            Predictions will be returned for each row.
          </p>
          <div className="flex items-center gap-3 mb-4">
            <label htmlFor="bulk-csv-input" className="btn-secondary cursor-pointer">
              <Upload className="w-4 h-4" />
              Choose CSV
              <input id="bulk-csv-input" ref={fileRef} type="file" accept=".csv" className="hidden" />
            </label>
            <button
              id="bulk-predict-btn"
              onClick={handleBulkPredict}
              disabled={loading}
              className="btn-primary"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4" />}
              {loading ? "Predicting…" : "Run Bulk Prediction"}
            </button>
          </div>
          {bulkResults.length > 0 && (
            <div className="mt-4 overflow-x-auto">
              <table className="data-table text-xs">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Churn Prob.</th>
                    <th>Risk Level</th>
                    <th>Prediction</th>
                  </tr>
                </thead>
                <tbody>
                  {bulkResults.slice(0, 50).map((p, i) => (
                    <tr key={p.id}>
                      <td>{i + 1}</td>
                      <td>{(p.churn_probability * 100).toFixed(1)}%</td>
                      <td><span className={`risk-badge risk-badge-${p.risk_level}`}>{p.risk_level}</span></td>
                      <td>{p.churn_prediction ? "Churn" : "Stay"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {bulkResults.length > 50 && (
                <p className="text-xs text-slate-500 mt-2 text-center">
                  Showing 50 of {bulkResults.length} results
                </p>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
