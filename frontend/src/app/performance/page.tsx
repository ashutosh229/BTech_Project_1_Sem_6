"use client";
import Navbar from "@/components/Navbar";

const evalMetrics = [
  { name: "Accuracy", value: "92.3%", bar: 92.3, color: "var(--accent-green)" },
  { name: "F1 Score", value: "0.914", bar: 91.4, color: "var(--accent-blue)" },
  { name: "Precision", value: "92.3%", bar: 92.3, color: "var(--accent-amber)" },
  { name: "Recall", value: "91.6%", bar: 91.6, color: "var(--accent-orange)" },
  { name: "AUC-ROC", value: "0.961", bar: 96.1, color: "var(--accent-blue-glow)" },
];

const confusionMatrix = [
  { label: "True Neg", value: 991, row: "Dismissed", col: "Dismissed", color: "var(--accent-green)", opacity: 0.85 },
  { label: "False Pos", value: 74, row: "Dismissed", col: "Allowed", color: "var(--accent-red)", opacity: 0.3 },
  { label: "False Neg", value: 82, row: "Allowed", col: "Dismissed", color: "var(--accent-red)", opacity: 0.35 },
  { label: "True Pos", value: 891, row: "Allowed", col: "Allowed", color: "var(--accent-green)", opacity: 0.8 },
];

const topFeatures = [
  { name: "rag_weighted_outcome", score: 100 },
  { name: "ev_witness", score: 87 },
  { name: "ev_medical", score: 82 },
  { name: "missing_count", score: 71 },
  { name: "conflict_score", score: 65 },
  { name: "rag_similarity_mean", score: 59 },
  { name: "fg_medical_report", score: 52 },
  { name: "num_issues", score: 44 },
  { name: "ev_memo", score: 38 },
  { name: "is_criminal", score: 31 },
];

export default function PerformancePage() {
  return (
    <div style={{ minHeight: "100vh", background: "var(--bg-void)" }}>
      <Navbar />
      <main style={{ padding: "32px", maxWidth: 1440, margin: "0 auto" }}>
        <h1 style={{ fontFamily: "'Manrope', sans-serif", fontSize: 28, fontWeight: 800, marginBottom: 8, letterSpacing: "-0.03em" }}>
          Model Performance
        </h1>
        <p style={{ color: "var(--text-muted)", marginBottom: 32, fontSize: 14 }}>
          XGBoost classifier trained on 2,038 labeled cases • 5-fold stratified cross-validation
        </p>

        {/* Row 1: Confusion Matrix + Metrics */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24, marginBottom: 32 }}>
          {/* Confusion Matrix */}
          <div className="glass-card animate-in animate-delay-1" style={{ padding: 28 }}>
            <h2 style={{ fontFamily: "'Manrope', sans-serif", fontSize: 18, fontWeight: 700, marginBottom: 24 }}>
              Confusion Matrix
            </h2>
            <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
              <div style={{ display: "flex", flexDirection: "column", gap: 4, fontSize: 12, color: "var(--text-muted)", textAlign: "right", width: 80 }}>
                <div style={{ height: 120, display: "flex", alignItems: "center", justifyContent: "flex-end" }}>Dismissed</div>
                <div style={{ height: 120, display: "flex", alignItems: "center", justifyContent: "flex-end" }}>Allowed</div>
              </div>
              <div>
                <div style={{ display: "flex", gap: 4, marginBottom: 8, paddingLeft: 4 }}>
                  <div style={{ width: 120, textAlign: "center", fontSize: 12, color: "var(--text-muted)" }}>Pred: Dismissed</div>
                  <div style={{ width: 120, textAlign: "center", fontSize: 12, color: "var(--text-muted)" }}>Pred: Allowed</div>
                </div>
                <div style={{ display: "grid", gridTemplateColumns: "120px 120px", gap: 4 }}>
                  {confusionMatrix.map((cell) => (
                    <div key={cell.label} style={{
                      height: 120, borderRadius: 12, display: "flex", flexDirection: "column",
                      alignItems: "center", justifyContent: "center",
                      background: `${cell.color}${Math.round(cell.opacity * 25).toString(16).padStart(2, '0')}`,
                      border: `1px solid ${cell.color}22`,
                    }}>
                      <span style={{ fontSize: 28, fontWeight: 700, fontFamily: "'Manrope', sans-serif", color: cell.color }}>
                        {cell.value}
                      </span>
                      <span style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 4 }}>{cell.label}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Evaluation Metrics */}
          <div className="glass-card animate-in animate-delay-2" style={{ padding: 28 }}>
            <h2 style={{ fontFamily: "'Manrope', sans-serif", fontSize: 18, fontWeight: 700, marginBottom: 24 }}>
              Evaluation Metrics
            </h2>
            <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
              {evalMetrics.map((m) => (
                <div key={m.name}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
                    <span style={{ fontSize: 14, fontWeight: 500 }}>{m.name}</span>
                    <span style={{ fontSize: 14, fontWeight: 700, fontFamily: "'Manrope', sans-serif", color: m.color }}>{m.value}</span>
                  </div>
                  <div className="progress-bar" style={{ height: 8 }}>
                    <div className="progress-fill" style={{ width: `${m.bar}%`, background: m.color }} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Row 2: Feature Importance */}
        <div className="glass-card animate-in animate-delay-3" style={{ padding: 28 }}>
          <h2 style={{ fontFamily: "'Manrope', sans-serif", fontSize: 18, fontWeight: 700, marginBottom: 24 }}>
            🔥 Top 10 Feature Importance
          </h2>
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {topFeatures.map((f, i) => (
              <div key={f.name} style={{ display: "flex", alignItems: "center", gap: 16 }}>
                <span style={{ fontSize: 12, color: "var(--text-muted)", width: 24, textAlign: "right" }}>#{i + 1}</span>
                <span style={{ fontSize: 13, fontWeight: 500, width: 200, fontFamily: "'Courier New', monospace", color: "var(--accent-blue-light)" }}>
                  {f.name}
                </span>
                <div style={{ flex: 1 }}>
                  <div className="progress-bar" style={{ height: 10, borderRadius: 5 }}>
                    <div className="progress-fill" style={{
                      width: `${f.score}%`, borderRadius: 5,
                      background: `linear-gradient(90deg, var(--accent-blue), var(--accent-blue-glow))`,
                    }} />
                  </div>
                </div>
                <span style={{ fontSize: 13, fontWeight: 600, width: 40, textAlign: "right", color: "var(--text-secondary)" }}>
                  {f.score}%
                </span>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
