"use client";
import Navbar from "@/components/Navbar";
import Link from "next/link";

const metrics = [
  { label: "Cases in Corpus", value: "9,675", icon: "📊", color: "var(--accent-blue)" },
  { label: "Prediction Accuracy", value: "87.4%", icon: "🎯", color: "var(--accent-green)" },
  { label: "Evidence Signals", value: "55", icon: "🧬", color: "var(--accent-amber)" },
  { label: "Validated Dataset", value: "2,038", icon: "🔬", color: "var(--accent-orange)" },
];

const features = [
  {
    icon: "🧠",
    title: "AI Outcome Prediction",
    desc: "XGBoost model trained on 2,038 labeled High Court cases predicts whether your case is likely to succeed or face dismissal.",
  },
  {
    icon: "📋",
    title: "Missing Evidence Detection",
    desc: "Identifies which evidence you're missing and how much gathering it would improve your chances — ranked by counterfactual impact.",
  },
  {
    icon: "🔍",
    title: "Precedent Retrieval",
    desc: "Finds the most similar cases from 9,675 High Court judgments using InLegalBERT semantic embeddings and FAISS indexing.",
  },
  {
    icon: "⚡",
    title: "Contradiction Detection",
    desc: "Flags temporal mismatches and evidentiary inconsistencies that could weaken your case before you file.",
  },
];

export default function HomePage() {
  return (
    <div style={{ minHeight: "100vh", background: "var(--bg-void)" }}>
      <Navbar />

      <main style={{ padding: "32px", maxWidth: 1200, margin: "0 auto" }}>
        {/* Hero */}
        <div style={{ textAlign: "center", padding: "64px 0 48px" }}>
          <div style={{ fontSize: 13, color: "var(--accent-blue-light)", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 16 }}>
            Evidence-Aware Judicial Intelligence
          </div>
          <h1 style={{
            fontFamily: "'Manrope', sans-serif", fontSize: 48, fontWeight: 800,
            letterSpacing: "-0.03em", lineHeight: 1.15, marginBottom: 20,
            maxWidth: 700, margin: "0 auto 20px",
          }}>
            Know Your Case Strength{" "}
            <span style={{ color: "var(--accent-blue)" }}>Before</span>{" "}
            You File
          </h1>
          <p style={{ color: "var(--text-muted)", fontSize: 17, maxWidth: 560, margin: "0 auto 36px", lineHeight: 1.6 }}>
            AI-powered case analysis trained on 9,675 High Court judgments.
            Predict outcomes, find missing evidence, and discover precedents.
          </p>
          <Link href="/analyze">
            <button className="btn-primary" style={{ fontSize: 17, padding: "16px 48px", borderRadius: 14 }}>
              ⚖️ Analyze Your Case
            </button>
          </Link>
        </div>

        {/* Metrics */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 20, marginBottom: 64 }}>
          {metrics.map((m, i) => (
            <div key={m.label} className={`glass-card metric-card animate-in animate-delay-${i + 1}`}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span className="metric-label">{m.label}</span>
                <span style={{ fontSize: 20 }}>{m.icon}</span>
              </div>
              <div className="metric-value" style={{ color: m.color }}>{m.value}</div>
            </div>
          ))}
        </div>

        {/* Features */}
        <div style={{ marginBottom: 64 }}>
          <h2 style={{ fontFamily: "'Manrope', sans-serif", fontSize: 24, fontWeight: 800, textAlign: "center", marginBottom: 32, letterSpacing: "-0.02em" }}>
            What You Get
          </h2>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 20 }}>
            {features.map((f) => (
              <div key={f.title} className="glass-card" style={{ padding: 28 }}>
                <div style={{ fontSize: 32, marginBottom: 16 }}>{f.icon}</div>
                <h3 style={{ fontFamily: "'Manrope', sans-serif", fontSize: 18, fontWeight: 700, marginBottom: 8 }}>
                  {f.title}
                </h3>
                <p style={{ fontSize: 14, color: "var(--text-secondary)", lineHeight: 1.6, margin: 0 }}>
                  {f.desc}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* CTA */}
        <div className="glass-card" style={{
          padding: "48px", textAlign: "center", marginBottom: 48,
          background: "linear-gradient(135deg, rgba(59,130,246,0.06), rgba(99,102,241,0.04))",
          border: "1px solid rgba(59,130,246,0.15)",
        }}>
          <h2 style={{ fontFamily: "'Manrope', sans-serif", fontSize: 24, fontWeight: 800, marginBottom: 12, letterSpacing: "-0.02em" }}>
            Ready to Strengthen Your Case?
          </h2>
          <p style={{ color: "var(--text-muted)", fontSize: 15, marginBottom: 24 }}>
            Enter your case details and get AI-powered insights in seconds.
          </p>
          <Link href="/analyze">
            <button className="btn-primary" style={{ fontSize: 16, padding: "14px 40px", borderRadius: 14 }}>
              Start Analysis →
            </button>
          </Link>
        </div>

        {/* Footer */}
        <div style={{ textAlign: "center", padding: "24px 0", fontSize: 12, color: "var(--text-muted)" }}>
          Built on research-grade ML • Allahabad High Court corpus • For informational purposes only
        </div>
      </main>
    </div>
  );
}
