import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";

export const metadata: Metadata = {
  title: "ChurnSense AI — AI-Powered Customer Churn Intelligence",
  description:
    "Predict customer churn before it happens. Understand why customers leave. Take personalized retention action with AI-powered intelligence.",
};

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-surface overflow-hidden">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-8 py-4 border-b border-surface-border bg-surface/80 backdrop-blur-xl">
        <div className="flex items-center gap-3">
          <Image
            src="/logo.png"
            alt="ChurnSense AI"
            width={36}
            height={36}
            className="w-9 h-9 rounded-xl object-contain shadow-brand"
            priority
          />
          <span className="text-white font-bold text-lg">ChurnSense AI</span>
        </div>
        <div className="flex items-center gap-3">
          <Link href="/login" className="btn-secondary text-sm py-2 px-4">
            Sign In
          </Link>
          <Link href="/register" className="btn-primary text-sm py-2 px-4">
            Get Started
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-32 pb-24 px-8">
        {/* Gradient orbs */}
        <div className="absolute top-20 left-1/4 w-96 h-96 rounded-full opacity-10 blur-3xl"
          style={{ background: "radial-gradient(circle, #6366f1, transparent)" }} />
        <div className="absolute top-40 right-1/4 w-80 h-80 rounded-full opacity-10 blur-3xl"
          style={{ background: "radial-gradient(circle, #06b6d4, transparent)" }} />

        <div className="relative max-w-5xl mx-auto text-center animate-fade-in">
          <div className="inline-flex items-center gap-2 rounded-full border border-brand-500/30 bg-brand-500/10 px-4 py-2 text-xs font-medium text-brand-300 mb-8">
            <span className="w-1.5 h-1.5 rounded-full bg-brand-400 animate-pulse-slow" />
            AI-Powered Churn Intelligence
          </div>

          <h1 className="text-6xl font-extrabold text-white leading-tight mb-6">
            Stop Losing Customers<br />
            <span className="text-gradient">Before It&apos;s Too Late</span>
          </h1>

          <p className="text-xl text-slate-400 max-w-3xl mx-auto mb-10 leading-relaxed">
            ChurnSense AI identifies at-risk customers, explains <em>why</em> they&apos;re likely to leave,
            and delivers personalized retention recommendations — all from a single platform.
          </p>

          <div className="flex items-center justify-center gap-4 flex-wrap">
            <Link href="/register" className="btn-primary text-base px-8 py-3">
              Start Analyzing Free
            </Link>
            <Link href="/login" className="btn-secondary text-base px-8 py-3">
              View Dashboard Demo
            </Link>
          </div>
        </div>
      </section>

      {/* Feature Cards */}
      <section className="px-8 pb-24 max-w-6xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[
            {
              icon: "🎯",
              title: "Predict Churn Risk",
              desc: "Train multiple ML models — Logistic Regression, Random Forest, XGBoost and more. Get churn probability for every customer.",
            },
            {
              icon: "🧠",
              title: "Understand Why",
              desc: "SHAP-based explainability shows exactly which factors drive each prediction. No black box — real, interpretable insights.",
            },
            {
              icon: "💡",
              title: "Act with Recommendations",
              desc: "Receive personalized, explainable retention recommendations for every at-risk customer. Contract upgrades, pricing reviews, and more.",
            },
          ].map((f) => (
            <div key={f.title} className="glass-card animate-slide-up">
              <div className="text-4xl mb-4">{f.icon}</div>
              <h3 className="text-lg font-semibold text-white mb-2">{f.title}</h3>
              <p className="text-sm text-slate-400 leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Stats */}
      <section className="px-8 pb-24 max-w-6xl mx-auto">
        <div className="glass-card">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            {[
              { label: "ML Models Supported", value: "5+" },
              { label: "Explainability Methods", value: "SHAP" },
              { label: "Recommendation Types", value: "6" },
              { label: "API Endpoints", value: "20+" },
            ].map((s) => (
              <div key={s.label}>
                <div className="text-4xl font-extrabold text-gradient mb-1">{s.value}</div>
                <div className="text-sm text-slate-400">{s.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-surface-border px-8 py-8 text-center text-xs text-slate-500">
        <p>© 2026 ChurnSense AI · Built by Swaraj Karle · College Software Engineering Project</p>
        <p className="mt-1">
          Open-source libraries used under their respective licenses.{" "}
          <Link href="/login" className="text-brand-400 hover:underline">View Attributions</Link>
        </p>
      </footer>
    </main>
  );
}
