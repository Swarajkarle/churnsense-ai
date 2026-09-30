"use client";

import { useQuery } from "@tanstack/react-query";
import { predictionApi } from "@/lib/api";
import type { Prediction } from "@/types";
import { Lightbulb } from "lucide-react";

export default function RecommendationsPage() {
  const { data: predictions = [], isLoading } = useQuery<Prediction[]>({
    queryKey: ["predictions-recs"],
    queryFn: () => predictionApi.list(1, 100).then((r) => r.data),
  });

  const allRecs = predictions
    .flatMap((p) =>
      (p.recommendations || []).map((r) => ({ ...r, prediction: p }))
    )
    .sort((a, b) => a.priority - b.priority);

  const categoryColors: Record<string, string> = {
    contract_upgrade: "text-brand-400 bg-brand-500/10",
    loyalty_incentive: "text-amber-400 bg-amber-500/10",
    pricing_review: "text-emerald-400 bg-emerald-500/10",
    personalized_support: "text-cyan-400 bg-cyan-500/10",
    service_resolution: "text-orange-400 bg-orange-500/10",
    success_outreach: "text-red-400 bg-red-500/10",
  };

  return (
    <div className="p-8 space-y-6 animate-fade-in">
      <div className="section-header">
        <div>
          <h1 className="section-title">Retention Recommendations</h1>
          <p className="section-subtitle">
            AI-generated retention actions for at-risk customers
          </p>
        </div>
      </div>

      <div className="glass-card border border-amber-500/20 mb-2">
        <p className="text-xs text-amber-400/80">
          ⚠️ Disclaimer: These recommendations are suggested actions informed by model predictions.
          They do not guarantee that a customer will or will not churn. Use them as data-informed
          starting points for your retention strategy.
        </p>
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {[1,2,3].map((i) => <div key={i} className="skeleton h-24 rounded-2xl" />)}
        </div>
      ) : allRecs.length === 0 ? (
        <div className="glass-card text-center py-16">
          <Lightbulb className="w-10 h-10 text-slate-600 mx-auto mb-3" />
          <p className="text-sm text-slate-400">No recommendations yet</p>
          <p className="text-xs text-slate-500 mt-1">
            Run predictions on customers to generate retention recommendations.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {allRecs.slice(0, 30).map((rec) => (
            <div key={rec.id} className="glass-card p-4">
              <div className="flex items-start justify-between gap-2 mb-2">
                <span className={`text-xs font-semibold px-2.5 py-0.5 rounded-full ${categoryColors[rec.category] || "text-brand-400 bg-brand-500/10"}`}>
                  {rec.category.replace(/_/g, " ")}
                </span>
                <span className={`risk-badge risk-badge-${rec.prediction.risk_level} text-xs`}>
                  {rec.prediction.risk_level} risk
                </span>
              </div>
              <h3 className="text-sm font-semibold text-white mb-1">{rec.title}</h3>
              <p className="text-xs text-slate-300 leading-relaxed mb-2">{rec.description}</p>
              {rec.rationale && (
                <p className="text-xs text-slate-500 italic">Why: {rec.rationale}</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
