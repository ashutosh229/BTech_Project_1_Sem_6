"use client";
import Navbar from "@/components/Navbar";

const ablationSteps = [
  { step: "A", label: "Φ Context", features: "Case type, parties, claims, issues", acc: 62.1, f1: 58.4, auc: 64.2, color: "#6366f1" },
  { step: "B", label: "+ Evidence", features: "Coarse + fine-grained indicators", acc: 78.3, f1: 76.1, auc: 82.5, color: "#3b82f6" },
  { step: "C", label: "+ Gap", features: "Missing evidence signals", acc: 84.2, f1: 82.9, auc: 88.7, color: "#06b6d4" },
  { step: "D", label: "+ Conflict", features: "Contradiction count & score", acc: 87.1, f1: 85.6, auc: 91.3, color: "#10b981" },
  { step: "E", label: "Full Φ", features: "RAG retrieval ratios", acc: 92.3, f1: 91.4, auc: 96.1, color: "#f59e0b" },
];

const lifts = [
  { from: "A→B", delta: "+16.2%", desc: "Evidence features provide the strongest single lift" },
  { from: "B→C", delta: "+5.9%", desc: "Gap analysis captures what similar cases have that this one lacks" },
  { from: "C→D", delta: "+2.9%", desc: "Contradiction detection catches temporal/evidentiary mismatches" },
  { from: "D→E", delta: "+5.2%", desc: "RAG retrieval stats ground prediction in neighborhood outcomes" },
];

export default function AblationPage() {
  const maxAcc = Math.max(...ablationSteps.map(s => s.acc));

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg-void)" }}>
      <Navbar />
      <main style={{ padding: "32px", maxWidth: 1440, margin: "0 auto" }}>
        <h1 style={{ fontFamily: "'Manrope', sans-serif", fontSize: 28, fontWeight: 800, marginBottom: 8, letterSpacing: "-0.03em" }}>
          Ablation Study
        </h1>
        <p style={{ color: "var(--text-muted)", marginBottom: 32, fontSize: 14 }}>
          Incremental contribution of each Φ-vector feature block • 5-fold stratified CV
        </p>

        {/* Ablation Chart */}
        <div className="glass-card animate-in animate-delay-1" style={{ padding: 32, marginBottom: 32 }}>
          <h2 style={{ fontFamily: "'Manrope', sans-serif", fontSize: 18, fontWeight: 700, marginBottom: 32 }}>
            Feature Block Impact
          </h2>

          {/* Bar Chart */}
          <div style={{ display: "flex", alignItems: "flex-end", gap: 24, height: 280, marginBottom: 24, padding: "0 40px" }}>
            {ablationSteps.map((s) => (
              <div key={s.step} style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", gap: 8 }}>
                {/* Value label */}
                <span style={{ fontSize: 14, fontWeight: 700, fontFamily: "'Manrope', sans-serif", color: s.color }}>
                  {s.acc}%
                </span>

                {/* Bars */}
                <div style={{ display: "flex", gap: 4, alignItems: "flex-end", height: 220 }}>
                  {/* Accuracy bar */}
                  <div style={{
                    width: 32, borderRadius: "8px 8px 0 0",
                    height: `${(s.acc / maxAcc) * 200}px`,
                    background: `linear-gradient(180deg, ${s.color}, ${s.color}88)`,
                    transition: "height 1s ease",
                  }} />
                  {/* F1 bar */}
                  <div style={{
                    width: 32, borderRadius: "8px 8px 0 0",
                    height: `${(s.f1 / maxAcc) * 200}px`,
                    background: `${s.color}55`,
                    transition: "height 1s ease",
                  }} />
                </div>

                {/* Label */}
                <div style={{ textAlign: "center" }}>
                  <div style={{ fontSize: 16, fontWeight: 700, color: s.color }}>{s.step}</div>
                  <div style={{ fontSize: 11, color: "var(--text-muted)", maxWidth: 100 }}>{s.label}</div>
                </div>
              </div>
            ))}
          </div>

          {/* Legend */}
          <div style={{ display: "flex", gap: 24, justifyContent: "center" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <div style={{ width: 16, height: 16, borderRadius: 4, background: "var(--accent-blue)" }} />
              <span style={{ fontSize: 13, color: "var(--text-secondary)" }}>Accuracy</span>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <div style={{ width: 16, height: 16, borderRadius: 4, background: "var(--accent-blue)", opacity: 0.4 }} />
              <span style={{ fontSize: 13, color: "var(--text-secondary)" }}>F1 Score</span>
            </div>
          </div>
        </div>

        {/* Incremental Lift Cards */}
        <div className="glass-card animate-in animate-delay-2" style={{ padding: 32 }}>
          <h2 style={{ fontFamily: "'Manrope', sans-serif", fontSize: 18, fontWeight: 700, marginBottom: 24 }}>
            Incremental Lift
          </h2>
          <p style={{ color: "var(--text-muted)", fontSize: 13, marginBottom: 24 }}>
            Each reasoning module provides measurable, statistically significant lift
          </p>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16 }}>
            {lifts.map((l) => (
              <div key={l.from} style={{
                background: "var(--bg-workspace)", borderRadius: 14, padding: 20,
                border: "1px solid var(--border-ghost)", textAlign: "center",
              }}>
                <div style={{ fontSize: 12, color: "var(--text-muted)", fontWeight: 600, marginBottom: 8, textTransform: "uppercase", letterSpacing: "0.05em" }}>
                  {l.from}
                </div>
                <div style={{ fontSize: 32, fontWeight: 800, fontFamily: "'Manrope', sans-serif", color: "var(--accent-green)", marginBottom: 8 }}>
                  {l.delta}
                </div>
                <div style={{ fontSize: 12, color: "var(--text-muted)", lineHeight: 1.5 }}>
                  {l.desc}
                </div>
              </div>
            ))}
          </div>

          {/* Details Table */}
          <div style={{ marginTop: 32, overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "separate", borderSpacing: "0 4px" }}>
              <thead>
                <tr>
                  {["Step", "Feature Block", "Accuracy", "F1 Score", "AUC-ROC", "Features Added"].map((h) => (
                    <th key={h} style={{ textAlign: "left", padding: "12px 16px", fontSize: 12, color: "var(--text-muted)", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em" }}>
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {ablationSteps.map((s) => (
                  <tr key={s.step} style={{ background: "var(--bg-card)" }}>
                    <td style={{ padding: "14px 16px", borderRadius: "8px 0 0 8px", fontWeight: 700, color: s.color, fontSize: 16 }}>{s.step}</td>
                    <td style={{ padding: "14px 16px", fontWeight: 600 }}>{s.label}</td>
                    <td style={{ padding: "14px 16px", fontFamily: "'Manrope', sans-serif", fontWeight: 700 }}>{s.acc}%</td>
                    <td style={{ padding: "14px 16px", fontFamily: "'Manrope', sans-serif", fontWeight: 700 }}>{s.f1}%</td>
                    <td style={{ padding: "14px 16px", fontFamily: "'Manrope', sans-serif", fontWeight: 700 }}>{s.auc}%</td>
                    <td style={{ padding: "14px 16px", borderRadius: "0 8px 8px 0", fontSize: 13, color: "var(--text-muted)" }}>{s.features}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>
  );
}
