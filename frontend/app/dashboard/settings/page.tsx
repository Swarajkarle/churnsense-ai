"use client";

import { useState } from "react";
import { Settings, Shield, Bell, Palette } from "lucide-react";

export default function SettingsPage() {
  const [riskThresholds, setRiskThresholds] = useState({
    medium: 30, high: 50, critical: 75,
  });

  return (
    <div className="p-8 space-y-8 animate-fade-in max-w-2xl">
      <div>
        <h1 className="section-title">Settings</h1>
        <p className="section-subtitle">Configure platform behavior and risk thresholds</p>
      </div>

      {/* Risk Thresholds */}
      <div className="glass-card">
        <h2 className="text-sm font-semibold text-white mb-1 flex items-center gap-2">
          <Shield className="w-4 h-4 text-brand-400" />
          Risk Level Thresholds
        </h2>
        <p className="text-xs text-slate-500 mb-5">
          Configure churn probability thresholds for risk categorization.
          These thresholds are heuristic operational guidelines — they have not been
          validated as scientifically established cutoffs and should be calibrated
          to your specific business context.
        </p>
        <div className="space-y-4">
          {(["medium", "high", "critical"] as const).map((level) => (
            <div key={level}>
              <div className="flex justify-between mb-1">
                <label className={`text-xs font-medium capitalize
                  ${level === "medium" ? "text-amber-400" : level === "high" ? "text-red-400" : "text-purple-400"}`}>
                  {level} Risk starts at: {riskThresholds[level]}%
                </label>
              </div>
              <input
                type="range"
                min={level === "medium" ? 10 : level === "high" ? riskThresholds.medium + 5 : riskThresholds.high + 5}
                max={90}
                className="w-full"
                value={riskThresholds[level]}
                onChange={(e) => setRiskThresholds((t) => ({ ...t, [level]: Number(e.target.value) }))}
              />
            </div>
          ))}
        </div>
        <p className="text-xs text-slate-500 mt-4">
          Note: Threshold changes here are local to this session.
          Backend threshold configuration requires an API call with the model activation.
        </p>
      </div>

      {/* Privacy Notice */}
      <div className="glass-card border border-brand-500/20">
        <h2 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
          <Shield className="w-4 h-4 text-brand-400" />
          Privacy Notice
        </h2>
        <div className="text-xs text-slate-400 space-y-2 leading-relaxed">
          <p>
            <strong className="text-slate-300">Data Handling:</strong> All customer data uploaded to ChurnSense AI
            is stored on your own configured database and server. Customer data is NOT sent to external
            AI services for processing.
          </p>
          <p>
            <strong className="text-slate-300">Data Minimization:</strong> Only data necessary for churn analysis
            is stored. We recommend removing personally identifiable information (PII) from datasets
            before uploading where possible.
          </p>
          <p>
            <strong className="text-slate-300">Deletion:</strong> Datasets can be deleted at any time from the
            Dataset Management page. Deletion removes both the database record and the uploaded file.
          </p>
          <p>
            <strong className="text-slate-300">Model Predictions:</strong> Predictions are stored in your database
            and can be reviewed in the Prediction History page.
          </p>
        </div>
      </div>
    </div>
  );
}
