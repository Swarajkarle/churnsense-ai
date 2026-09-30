"use client";

import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { modelApi, datasetApi } from "@/lib/api";
import type { MLModel, Dataset } from "@/types";
import { toast } from "sonner";
import { Brain, Play, CheckCircle, Cpu, Loader2, BarChart3 } from "lucide-react";
import { clsx } from "clsx";
import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
} from "recharts";

const ALGORITHMS = [
  { id: "logistic_regression", label: "Logistic Regression", desc: "Fast, interpretable baseline" },
  { id: "decision_tree", label: "Decision Tree", desc: "Simple rule-based learner" },
  { id: "random_forest", label: "Random Forest", desc: "Robust ensemble method" },
  { id: "gradient_boosting", label: "Gradient Boosting", desc: "High-performance sklearn GB" },
  { id: "xgboost", label: "XGBoost", desc: "High-performance gradient boosting" },
];

/**
 * ChurnSense AI — Model Training & Comparison Page
 */
export default function ModelsPage() {
  const [selectedAlgos, setSelectedAlgos] = useState<string[]>(["random_forest", "gradient_boosting"]);
  const [datasetId, setDatasetId] = useState("");
  const [targetCol, setTargetCol] = useState("Churn");
  const [testSplit, setTestSplit] = useState(0.2);
  const [training, setTraining] = useState(false);

  const { data: models = [], refetch: refetchModels } = useQuery<MLModel[]>({
    queryKey: ["models"],
    queryFn: () => modelApi.list().then((r) => r.data),
  });

  const { data: datasets = [] } = useQuery<Dataset[]>({
    queryKey: ["datasets"],
    queryFn: () => datasetApi.list().then((r) => r.data),
  });

  const toggleAlgo = (id: string) => {
    setSelectedAlgos((prev) =>
      prev.includes(id) ? prev.filter((a) => a !== id) : [...prev, id]
    );
  };

  const handleTrain = async () => {
    if (!datasetId) { toast.error("Please select a dataset"); return; }
    if (!targetCol) { toast.error("Please enter the target column name"); return; }
    if (selectedAlgos.length === 0) { toast.error("Select at least one algorithm"); return; }
    setTraining(true);
    try {
      await modelApi.train({
        dataset_id: datasetId,
        target_column: targetCol,
        algorithms: selectedAlgos,
        test_split: testSplit,
        random_state: 42,
      });
      toast.success("Training started! Models will appear below when complete.");
      setTimeout(() => { refetchModels(); setTraining(false); }, 3000);
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Training failed");
      setTraining(false);
    }
  };

  const handleActivate = async (id: string) => {
    try {
      await modelApi.activate(id);
      toast.success("Model activated for predictions!");
      refetchModels();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Activation failed");
    }
  };

  // Build comparison data from all models' test metrics
  const comparisonData = models
    .filter((m) => m.status === "trained" || m.status === "deployed")
    .map((m) => {
      const testMetric = m.metrics?.find((mt) => mt.split === "test");
      return {
        name: m.algorithm.replace("_", "\n"),
        accuracy: testMetric?.accuracy ? +(testMetric.accuracy * 100).toFixed(1) : 0,
        f1: testMetric?.f1_score ? +(testMetric.f1_score * 100).toFixed(1) : 0,
        roc_auc: testMetric?.roc_auc ? +(testMetric.roc_auc * 100).toFixed(1) : 0,
      };
    });

  return (
    <div className="p-8 space-y-8 animate-fade-in">
      <div className="section-header">
        <div>
          <h1 className="section-title">Model Training</h1>
          <p className="section-subtitle">Train, compare, and deploy ML models for churn prediction</p>
        </div>
      </div>

      {/* Training Config */}
      <div className="glass-card">
        <h2 className="text-sm font-semibold text-white mb-5 flex items-center gap-2">
          <Play className="w-4 h-4 text-brand-400" />
          Configure Training
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">Dataset</label>
            <select
              id="training-dataset"
              className="form-input"
              value={datasetId}
              onChange={(e) => setDatasetId(e.target.value)}
            >
              <option value="">Select a dataset…</option>
              {datasets.map((d) => (
                <option key={d.id} value={d.id}>{d.name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">Target Column</label>
            <input
              id="target-column"
              type="text"
              className="form-input"
              placeholder="e.g. Churn"
              value={targetCol}
              onChange={(e) => setTargetCol(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">
              Test Split: {(testSplit * 100).toFixed(0)}%
            </label>
            <input
              type="range"
              min="10" max="40" step="5"
              className="w-full mt-3"
              value={testSplit * 100}
              onChange={(e) => setTestSplit(Number(e.target.value) / 100)}
            />
          </div>
        </div>

        {/* Algorithm Selection */}
        <div className="mb-5">
          <label className="block text-xs font-medium text-slate-300 mb-3">
            Select Algorithms (choose one or more)
          </label>
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-3">
            {ALGORITHMS.map((algo) => {
              const selected = selectedAlgos.includes(algo.id);
              return (
                <button
                  key={algo.id}
                  type="button"
                  onClick={() => toggleAlgo(algo.id)}
                  className={clsx(
                    "rounded-xl border p-3 text-left transition-all",
                    selected
                      ? "border-brand-500 bg-brand-500/10 text-white"
                      : "border-surface-border bg-surface text-slate-400 hover:border-brand-500/50"
                  )}
                >
                  <div className="text-xs font-semibold mb-1">{algo.label}</div>
                  <div className="text-xs opacity-70">{algo.desc}</div>
                </button>
              );
            })}
          </div>
        </div>

        <button
          id="train-btn"
          onClick={handleTrain}
          disabled={training}
          className="btn-primary"
        >
          {training ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
          {training ? "Training in Progress…" : "Start Training"}
        </button>
        <p className="text-xs text-slate-500 mt-2">
          Training runs in the background. Results will appear in the table below.
          Evaluation uses stratified train/test split — F1 and ROC-AUC are primary metrics for imbalanced datasets.
        </p>
      </div>

      {/* Model Comparison Chart */}
      {comparisonData.length > 0 && (
        <div className="glass-card">
          <h2 className="text-sm font-semibold text-white mb-5 flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-brand-400" />
            Model Comparison (Test Set)
          </h2>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={comparisonData} barGap={4}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2a2a45" />
              <XAxis dataKey="name" tick={{ fill: "#94a3b8", fontSize: 11 }} />
              <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} domain={[0, 100]} unit="%" />
              <Tooltip
                contentStyle={{ background: "#161625", border: "1px solid #2a2a45", borderRadius: 8, fontSize: 12 }}
                formatter={(v: number) => `${v}%`}
              />
              <Bar dataKey="accuracy" fill="#6366f1" radius={[4, 4, 0, 0]} name="Accuracy" />
              <Bar dataKey="f1" fill="#06b6d4" radius={[4, 4, 0, 0]} name="F1 Score" />
              <Bar dataKey="roc_auc" fill="#10b981" radius={[4, 4, 0, 0]} name="ROC-AUC" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Models Table */}
      <div className="glass-card p-0 overflow-hidden">
        <div className="px-6 py-4 border-b border-surface-border flex justify-between items-center">
          <h2 className="text-sm font-semibold text-white">Trained Models</h2>
          <button onClick={() => refetchModels()} className="btn-secondary text-xs py-1.5 px-3">
            Refresh
          </button>
        </div>
        {models.length === 0 ? (
          <div className="py-16 text-center">
            <Brain className="w-10 h-10 text-slate-600 mx-auto mb-3" />
            <p className="text-sm text-slate-400">No models trained yet</p>
          </div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Algorithm</th>
                <th>Status</th>
                <th>Accuracy</th>
                <th>F1 Score</th>
                <th>ROC-AUC</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {models.map((m) => {
                const test = m.metrics?.find((mt) => mt.split === "test");
                return (
                  <tr key={m.id}>
                    <td className="font-medium text-white">{m.name}</td>
                    <td className="text-xs text-slate-400">{m.algorithm}</td>
                    <td>
                      <div className="flex items-center gap-2">
                        <span className={clsx("text-xs font-medium capitalize",
                          m.status === "deployed" ? "text-emerald-400" :
                          m.status === "trained" ? "text-brand-400" :
                          m.status === "failed" ? "text-red-400" : "text-slate-400"
                        )}>
                          {m.status}
                        </span>
                        {m.is_active && (
                          <span className="risk-badge risk-badge-low text-xs">Active</span>
                        )}
                      </div>
                    </td>
                    <td>{test?.accuracy ? `${(test.accuracy * 100).toFixed(1)}%` : "—"}</td>
                    <td>{test?.f1_score ? `${(test.f1_score * 100).toFixed(1)}%` : "—"}</td>
                    <td>{test?.roc_auc ? `${(test.roc_auc * 100).toFixed(1)}%` : "—"}</td>
                    <td className="text-xs text-slate-400">
                      {new Date(m.created_at).toLocaleDateString("en-IN")}
                    </td>
                    <td>
                      {!m.is_active && m.status === "trained" && (
                        <button
                          onClick={() => handleActivate(m.id)}
                          className="btn-secondary text-xs py-1.5 px-3"
                        >
                          <CheckCircle className="w-3.5 h-3.5" />
                          Activate
                        </button>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
