"use client";
import Navbar from "@/components/Navbar";

const caseTypes = [
  { type: "Service", total: 3412, allowed: 420, dismissed: 580, partial: 1200, unknown: 1212, color: "#3b82f6" },
  { type: "Criminal", total: 2847, allowed: 310, dismissed: 390, partial: 890, unknown: 1257, color: "#f87171" },
  { type: "Property", total: 1891, allowed: 180, dismissed: 65, partial: 780, unknown: 866, color: "#fbbf24" },
  { type: "Civil", total: 984, allowed: 43, dismissed: 22, partial: 420, unknown: 499, color: "#06b6d4" },
  { type: "Matrimonial", total: 541, allowed: 20, dismissed: 8, partial: 223, unknown: 290, color: "#a78bfa" },
];

const evidenceCoverage = [
  { type: "Medical", criminal: 72, service: 8, property: 5, civil: 15 },
  { type: "Witness", criminal: 65, service: 12, property: 18, civil: 22 },
  { type: "FIR/Seizure", criminal: 81, service: 3, property: 2, civil: 6 },
  { type: "Contracts", criminal: 4, service: 35, property: 62, civil: 48 },
  { type: "Deeds", criminal: 2, service: 4, property: 78, civil: 12 },
  { type: "Procedural", criminal: 45, service: 58, property: 34, civil: 41 },
];

const pipelineSteps = [
  { name: "Raw JSON", icon: "📄", time: "2ms" },
  { name: "CON Builder", icon: "🏗️", time: "15ms" },
  { name: "FAISS Retrieval", icon: "🔍", time: "45ms" },
  { name: "Evidence Analysis", icon: "🧬", time: "28ms" },
  { name: "Contradiction", icon: "⚡", time: "8ms" },
  { name: "XGBoost", icon: "🧠", time: "3ms" },
];

function heatColor(value: number) {
  if (value >= 70) return "rgba(59, 130, 246, 0.7)";
  if (value >= 50) return "rgba(59, 130, 246, 0.45)";
  if (value >= 30) return "rgba(59, 130, 246, 0.25)";
  if (value >= 10) return "rgba(59, 130, 246, 0.12)";
  return "rgba(59, 130, 246, 0.04)";
}

export default function CorpusPage() {
  return (
    <div style={{ minHeight: "100vh", background: "var(--bg-void)" }}>
      <Navbar />
      <main style={{ padding: "32px", maxWidth: 1440, margin: "0 auto" }}>
        <h1 style={{ fontFamily: "'Manrope', sans-serif", fontSize: 28, fontWeight: 800, marginBottom: 8, letterSpacing: "-0.03em" }}>
          Corpus Intelligence
        </h1>
        <p style={{ color: "var(--text-muted)", marginBottom: 32, fontSize: 14 }}>
          Analytics across 9,675 high-court cases from the Allahabad High Court
        </p>

        {/* Overview Cards */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 20, marginBottom: 32 }}>
          {[
            { label: "Total Processed", value: "9,675", sub: "JSON case files", icon: "📊", color: "var(--accent-blue)" },
            { label: "Labeled Dataset", value: "2,038", sub: "973 Success / 1,065 Dismissed", icon: "🏷️", color: "var(--accent-green)" },
            { label: "Feature Dimensions", value: "55", sub: "Φ-vector features", icon: "🧬", color: "var(--accent-amber)" },
          ].map((m) => (
            <div key={m.label} className="glass-card animate-in animate-delay-1" style={{ padding: 24 }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
                <span style={{ fontSize: 13, color: "var(--text-secondary)", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em" }}>{m.label}</span>
                <span style={{ fontSize: 20 }}>{m.icon}</span>
              </div>
              <div style={{ fontSize: 36, fontWeight: 800, fontFamily: "'Manrope', sans-serif", color: m.color, letterSpacing: "-0.03em" }}>{m.value}</div>
              <div style={{ fontSize: 13, color: "var(--text-muted)", marginTop: 4 }}>{m.sub}</div>
            </div>
          ))}
        </div>

        {/* Row 2: Distribution + Heatmap */}
        <div style={{ display: "grid", gridTemplateColumns: "1.3fr 1fr", gap: 24, marginBottom: 32 }}>
          {/* Case Type Distribution */}
          <div className="glass-card animate-in animate-delay-2" style={{ padding: 28 }}>
            <h2 style={{ fontFamily: "'Manrope', sans-serif", fontSize: 18, fontWeight: 700, marginBottom: 24 }}>
              Outcome by Case Type
            </h2>
            <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
              {caseTypes.map((ct) => (
                <div key={ct.type}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
                    <span style={{ fontSize: 14, fontWeight: 600, color: ct.color }}>{ct.type}</span>
                    <span style={{ fontSize: 13, color: "var(--text-muted)" }}>{ct.total.toLocaleString()} cases</span>
                  </div>
                  <div style={{ display: "flex", height: 24, borderRadius: 6, overflow: "hidden", gap: 2 }}>
                    <div style={{ width: `${(ct.allowed / ct.total) * 100}%`, background: "var(--accent-green)", borderRadius: "6px 0 0 6px" }} title={`Allowed: ${ct.allowed}`} />
                    <div style={{ width: `${(ct.dismissed / ct.total) * 100}%`, background: "var(--accent-red)" }} title={`Dismissed: ${ct.dismissed}`} />
                    <div style={{ width: `${(ct.partial / ct.total) * 100}%`, background: "var(--accent-amber)" }} title={`Partial: ${ct.partial}`} />
                    <div style={{ width: `${(ct.unknown / ct.total) * 100}%`, background: "var(--bg-card-high)", borderRadius: "0 6px 6px 0" }} title={`Unknown: ${ct.unknown}`} />
                  </div>
                </div>
              ))}
              {/* Legend */}
              <div style={{ display: "flex", gap: 20, marginTop: 8 }}>
                {[
                  { label: "Allowed", color: "var(--accent-green)" },
                  { label: "Dismissed", color: "var(--accent-red)" },
                  { label: "Partial", color: "var(--accent-amber)" },
                  { label: "Unknown", color: "var(--bg-card-high)" },
                ].map((l) => (
                  <div key={l.label} style={{ display: "flex", alignItems: "center", gap: 6 }}>
                    <div style={{ width: 12, height: 12, borderRadius: 3, background: l.color }} />
                    <span style={{ fontSize: 12, color: "var(--text-muted)" }}>{l.label}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Evidence Coverage Heatmap */}
          <div className="glass-card animate-in animate-delay-3" style={{ padding: 28 }}>
            <h2 style={{ fontFamily: "'Manrope', sans-serif", fontSize: 18, fontWeight: 700, marginBottom: 24 }}>
              Evidence Coverage Heatmap
            </h2>
            <table style={{ width: "100%", borderCollapse: "separate", borderSpacing: 4 }}>
              <thead>
                <tr>
                  <th style={{ width: 100 }} />
                  {["Criminal", "Service", "Property", "Civil"].map((h) => (
                    <th key={h} style={{ fontSize: 11, color: "var(--text-muted)", fontWeight: 600, textAlign: "center", padding: 8, textTransform: "uppercase", letterSpacing: "0.05em" }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {evidenceCoverage.map((row) => (
                  <tr key={row.type}>
                    <td style={{ fontSize: 13, fontWeight: 500, padding: "8px 4px", color: "var(--text-secondary)" }}>{row.type}</td>
                    {[row.criminal, row.service, row.property, row.civil].map((v, i) => (
                      <td key={i} style={{
                        textAlign: "center", padding: 12, borderRadius: 8,
                        background: heatColor(v), fontSize: 13, fontWeight: 600,
                        color: v >= 50 ? "white" : "var(--text-secondary)",
                      }}>
                        {v}%
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Pipeline Flow */}
        <div className="glass-card animate-in animate-delay-4" style={{ padding: 28 }}>
          <h2 style={{ fontFamily: "'Manrope', sans-serif", fontSize: 18, fontWeight: 700, marginBottom: 24 }}>
            Pipeline Architecture
          </h2>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "0 16px" }}>
            {pipelineSteps.map((step, i) => (
              <div key={step.name} style={{ display: "flex", alignItems: "center", gap: 0 }}>
                <div style={{
                  background: "var(--bg-workspace)", borderRadius: 16, padding: "20px 24px",
                  border: "1px solid var(--border-ghost)", textAlign: "center", minWidth: 130,
                }}>
                  <div style={{ fontSize: 28, marginBottom: 8 }}>{step.icon}</div>
                  <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 4 }}>{step.name}</div>
                  <div style={{ fontSize: 11, color: "var(--text-muted)" }}>~{step.time}</div>
                </div>
                {i < pipelineSteps.length - 1 && (
                  <div style={{ color: "var(--accent-blue)", fontSize: 20, padding: "0 8px" }}>→</div>
                )}
              </div>
            ))}
          </div>
          <div style={{ textAlign: "center", marginTop: 20, fontSize: 13, color: "var(--text-muted)" }}>
            Total pipeline latency: ~101ms per case • Batch throughput: ~9,675 cases/hour
          </div>
        </div>
      </main>
    </div>
  );
}
