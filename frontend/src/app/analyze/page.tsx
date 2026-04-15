"use client";
import Navbar from "@/components/Navbar";
import { useState } from "react";

const CASE_TYPES = ["Criminal", "Civil", "Service", "Property", "Matrimonial"];

const EVIDENCE_OPTIONS = [
  { key: "medical", label: "Medical / FSL Reports", icon: "🩺", desc: "Injury reports, forensic lab results, postmortem" },
  { key: "witness", label: "Witness Testimony", icon: "👁️", desc: "Prosecution or defense witness statements" },
  { key: "fir", label: "FIR / Seizure Memo", icon: "📋", desc: "First information report, seizure records" },
  { key: "contracts", label: "Agreements & Contracts", icon: "📝", desc: "Sale agreements, employment contracts, MoUs" },
  { key: "deeds", label: "Property Deeds", icon: "🏠", desc: "Title deeds, registry documents, mutation records" },
  { key: "procedural", label: "Procedural Documents", icon: "📂", desc: "Notice, summons, court orders, affidavits" },
];

type AnalysisResult = {
  prediction: string;
  confidence: number;
  contradictions: { count: number; score: number; details: string[] };
  missingEvidence: { type: string; importance: number; lift: string; reason: string }[];
  similarCases: { id: string; outcome: string; similarity: number; year: string }[];
  evidenceDensity: number;
};

// Mock analysis — in production this would call your Python backend
function runMockAnalysis(formData: {
  caseType: string;
  parties: string;
  facts: string;
  evidence: string[];
  reliefs: string;
}): AnalysisResult {
  const evCount = formData.evidence.length;
  const baseConf = 45 + evCount * 8 + (formData.facts.length > 200 ? 10 : 0);
  const conf = Math.min(94, baseConf + Math.floor(Math.random() * 10));
  const pred = conf > 60 ? "Allowed / Success Likely" : "Dismissed / Weak Likely";

  const allEvidence = EVIDENCE_OPTIONS.map((e) => e.key);
  const missing = allEvidence.filter((e) => !formData.evidence.includes(e));

  const missingRanked = missing.map((key, i) => {
    const opt = EVIDENCE_OPTIONS.find((e) => e.key === key)!;
    const imp = Math.max(20, 90 - i * 18 - Math.floor(Math.random() * 10));
    return {
      type: opt.label,
      importance: imp,
      lift: `+${(imp * 0.15).toFixed(1)}%`,
      reason: `Present in ${50 + Math.floor(Math.random() * 40)}% of successful ${formData.caseType.toLowerCase()} cases in the corpus. Adding this evidence could strengthen your position.`,
    };
  }).sort((a, b) => b.importance - a.importance);

  return {
    prediction: pred,
    confidence: conf,
    contradictions: {
      count: Math.floor(Math.random() * 2),
      score: +(Math.random() * 0.3).toFixed(2),
      details: Math.random() > 0.5
        ? ["Timeline inconsistency: incident date and FIR filing date are 5 days apart"]
        : [],
    },
    missingEvidence: missingRanked,
    similarCases: [
      { id: "allahabad_2015_3099880", outcome: "Allowed", similarity: 87, year: "2015" },
      { id: "allahabad_2015_2847201", outcome: "Dismissed", similarity: 82, year: "2015" },
      { id: "allahabad_2015_1923744", outcome: "Allowed", similarity: 79, year: "2015" },
      { id: "allahabad_2015_4412098", outcome: "Partial", similarity: 74, year: "2015" },
      { id: "allahabad_2015_5501332", outcome: "Allowed", similarity: 71, year: "2015" },
    ],
    evidenceDensity: +(evCount / 6).toFixed(2),
  };
}

export default function AnalyzePage() {
  const [step, setStep] = useState<"input" | "results">("input");
  const [caseType, setCaseType] = useState("");
  const [parties, setParties] = useState("");
  const [facts, setFacts] = useState("");
  const [reliefs, setReliefs] = useState("");
  const [evidence, setEvidence] = useState<string[]>([]);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);

  function toggleEvidence(key: string) {
    setEvidence((prev) => prev.includes(key) ? prev.filter((e) => e !== key) : [...prev, key]);
  }

  function handleAnalyze() {
    if (!caseType || !facts.trim()) return;
    setLoading(true);
    // Simulate API call
    setTimeout(() => {
      const res = runMockAnalysis({ caseType, parties, facts, evidence, reliefs });
      setResult(res);
      setStep("results");
      setLoading(false);
    }, 1500);
  }

  function handleReset() {
    setStep("input");
    setResult(null);
  }

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg-void)" }}>
      <Navbar />
      <main style={{ padding: "32px", maxWidth: 1100, margin: "0 auto" }}>

        {step === "input" && (
          <div className="animate-in">
            {/* Header */}
            <div style={{ textAlign: "center", marginBottom: 40 }}>
              <h1 style={{ fontFamily: "'Manrope', sans-serif", fontSize: 32, fontWeight: 800, letterSpacing: "-0.03em", marginBottom: 8 }}>
                Analyze Your Case
              </h1>
              <p style={{ color: "var(--text-muted)", fontSize: 15, maxWidth: 500, margin: "0 auto" }}>
                Enter your case details below. Our AI will predict the likely outcome,
                identify missing evidence, and find similar precedents.
              </p>
            </div>

            <div className="glass-card" style={{ padding: 36 }}>
              {/* Case Type */}
              <div style={{ marginBottom: 28 }}>
                <label style={{ display: "block", fontSize: 13, fontWeight: 600, color: "var(--text-secondary)", marginBottom: 10, textTransform: "uppercase", letterSpacing: "0.05em" }}>
                  Case Type *
                </label>
                <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
                  {CASE_TYPES.map((t) => (
                    <button
                      key={t}
                      onClick={() => setCaseType(t)}
                      style={{
                        padding: "10px 22px", borderRadius: 10, fontSize: 14, fontWeight: 600,
                        border: caseType === t ? "2px solid var(--accent-blue)" : "1px solid var(--border-ghost)",
                        background: caseType === t ? "rgba(59,130,246,0.12)" : "var(--bg-card)",
                        color: caseType === t ? "var(--accent-blue-light)" : "var(--text-secondary)",
                        cursor: "pointer", transition: "all 0.2s",
                      }}
                    >
                      {t}
                    </button>
                  ))}
                </div>
              </div>

              {/* Parties */}
              <div style={{ marginBottom: 28 }}>
                <label style={{ display: "block", fontSize: 13, fontWeight: 600, color: "var(--text-secondary)", marginBottom: 10, textTransform: "uppercase", letterSpacing: "0.05em" }}>
                  Parties Involved
                </label>
                <input
                  type="text"
                  placeholder="e.g., Ramesh Kumar vs. State of UP"
                  value={parties}
                  onChange={(e) => setParties(e.target.value)}
                  style={{
                    width: "100%", padding: "14px 18px", borderRadius: 10,
                    background: "var(--bg-card-high)", border: "1px solid var(--border-ghost)",
                    color: "var(--text-primary)", fontSize: 14, outline: "none",
                  }}
                />
              </div>

              {/* Facts */}
              <div style={{ marginBottom: 28 }}>
                <label style={{ display: "block", fontSize: 13, fontWeight: 600, color: "var(--text-secondary)", marginBottom: 10, textTransform: "uppercase", letterSpacing: "0.05em" }}>
                  Case Facts & Background *
                </label>
                <textarea
                  placeholder="Describe the facts of your case in detail. Include key events, dates, and circumstances. The more detail you provide, the better our analysis..."
                  value={facts}
                  onChange={(e) => setFacts(e.target.value)}
                  rows={6}
                  style={{
                    width: "100%", padding: "14px 18px", borderRadius: 10,
                    background: "var(--bg-card-high)", border: "1px solid var(--border-ghost)",
                    color: "var(--text-primary)", fontSize: 14, outline: "none",
                    resize: "vertical", lineHeight: 1.6, fontFamily: "inherit",
                  }}
                />
                <div style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 6 }}>
                  {facts.length} characters • minimum 50 recommended
                </div>
              </div>

              {/* Evidence Checklist */}
              <div style={{ marginBottom: 28 }}>
                <label style={{ display: "block", fontSize: 13, fontWeight: 600, color: "var(--text-secondary)", marginBottom: 10, textTransform: "uppercase", letterSpacing: "0.05em" }}>
                  Evidence You Have
                </label>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
                  {EVIDENCE_OPTIONS.map((e) => {
                    const selected = evidence.includes(e.key);
                    return (
                      <button
                        key={e.key}
                        onClick={() => toggleEvidence(e.key)}
                        style={{
                          display: "flex", alignItems: "center", gap: 14,
                          padding: "14px 18px", borderRadius: 12, textAlign: "left",
                          background: selected ? "rgba(52,211,153,0.08)" : "var(--bg-card)",
                          border: selected ? "1px solid rgba(52,211,153,0.3)" : "1px solid var(--border-ghost)",
                          cursor: "pointer", transition: "all 0.2s",
                        }}
                      >
                        <span style={{ fontSize: 24 }}>{selected ? "✅" : e.icon}</span>
                        <div>
                          <div style={{ fontSize: 14, fontWeight: 600, color: selected ? "var(--accent-green)" : "var(--text-primary)" }}>
                            {e.label}
                          </div>
                          <div style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 2 }}>{e.desc}</div>
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Relief Sought */}
              <div style={{ marginBottom: 32 }}>
                <label style={{ display: "block", fontSize: 13, fontWeight: 600, color: "var(--text-secondary)", marginBottom: 10, textTransform: "uppercase", letterSpacing: "0.05em" }}>
                  Relief Sought
                </label>
                <input
                  type="text"
                  placeholder="e.g., Quashing of FIR, Compensation, Injunction..."
                  value={reliefs}
                  onChange={(e) => setReliefs(e.target.value)}
                  style={{
                    width: "100%", padding: "14px 18px", borderRadius: 10,
                    background: "var(--bg-card-high)", border: "1px solid var(--border-ghost)",
                    color: "var(--text-primary)", fontSize: 14, outline: "none",
                  }}
                />
              </div>

              {/* Submit */}
              <button
                onClick={handleAnalyze}
                disabled={loading || !caseType || !facts.trim()}
                className="btn-primary"
                style={{
                  width: "100%", padding: "16px", fontSize: 16, borderRadius: 14,
                  opacity: (!caseType || !facts.trim()) ? 0.5 : 1,
                }}
              >
                {loading ? "⏳ Analyzing with AI..." : "⚖️ Analyze Case"}
              </button>
            </div>
          </div>
        )}

        {step === "results" && result && (
          <div className="animate-in">
            {/* Back button */}
            <button onClick={handleReset} style={{
              background: "none", border: "none", color: "var(--accent-blue-light)",
              fontSize: 14, cursor: "pointer", marginBottom: 24, display: "flex", alignItems: "center", gap: 8,
            }}>
              ← Analyze Another Case
            </button>

            {/* Prediction Hero */}
            <div className="glass-card" style={{
              padding: 36, marginBottom: 24, textAlign: "center",
              background: result.confidence > 60
                ? "linear-gradient(135deg, rgba(52,211,153,0.08), rgba(16,185,129,0.04))"
                : "linear-gradient(135deg, rgba(248,113,113,0.08), rgba(239,68,68,0.04))",
              border: result.confidence > 60
                ? "1px solid rgba(52,211,153,0.2)"
                : "1px solid rgba(248,113,113,0.2)",
            }}>
              <div style={{ fontSize: 13, color: "var(--text-muted)", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 12 }}>
                AI Outcome Prediction
              </div>
              <div style={{
                fontSize: 28, fontWeight: 800, fontFamily: "'Manrope', sans-serif",
                color: result.confidence > 60 ? "var(--accent-green)" : "var(--accent-red)",
                marginBottom: 12,
              }}>
                {result.prediction}
              </div>
              <div style={{ display: "flex", justifyContent: "center", alignItems: "center", gap: 16, marginBottom: 16 }}>
                <div className="progress-bar" style={{ width: 300 }}>
                  <div className="progress-fill" style={{
                    width: `${result.confidence}%`,
                    background: result.confidence > 60
                      ? "linear-gradient(90deg, var(--accent-green), #10b981)"
                      : "linear-gradient(90deg, var(--accent-red), #ef4444)",
                  }} />
                </div>
                <span style={{ fontSize: 36, fontWeight: 800, fontFamily: "'Manrope', sans-serif", color: result.confidence > 60 ? "var(--accent-green)" : "var(--accent-red)" }}>
                  {result.confidence}%
                </span>
              </div>
              <div style={{ display: "flex", justifyContent: "center", gap: 24 }}>
                <span className="badge badge-blue">{caseType}</span>
                <span style={{ fontSize: 13, color: "var(--text-muted)" }}>
                  Evidence Density: <strong>{result.evidenceDensity}</strong>
                </span>
                <span style={{ fontSize: 13, color: "var(--text-muted)" }}>
                  Contradictions: <strong style={{ color: result.contradictions.score > 0.2 ? "var(--accent-red)" : "var(--accent-green)" }}>
                    {result.contradictions.score}
                  </strong>
                </span>
              </div>
            </div>

            {/* Two columns */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24, marginBottom: 24 }}>

              {/* Missing Evidence */}
              <div className="glass-card" style={{ padding: 28 }}>
                <h2 style={{ fontFamily: "'Manrope', sans-serif", fontSize: 18, fontWeight: 700, marginBottom: 6 }}>
                  📋 Evidence You Should Gather
                </h2>
                <p style={{ fontSize: 13, color: "var(--text-muted)", marginBottom: 20 }}>
                  Ranked by impact on your case outcome
                </p>

                {result.missingEvidence.length === 0 ? (
                  <div style={{ textAlign: "center", padding: 32, color: "var(--accent-green)" }}>
                    ✅ You have all key evidence types covered!
                  </div>
                ) : (
                  <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                    {result.missingEvidence.map((e, i) => (
                      <div key={e.type} style={{
                        background: "var(--bg-workspace)", borderRadius: 12, padding: 16,
                        border: "1px solid var(--border-ghost)",
                        borderLeft: `3px solid ${i === 0 ? "var(--accent-red)" : i === 1 ? "var(--accent-orange)" : "var(--accent-amber)"}`,
                      }}>
                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
                          <span style={{ fontSize: 14, fontWeight: 600 }}>{e.type}</span>
                          <span className={`badge ${i === 0 ? "badge-red" : i === 1 ? "badge-orange" : "badge-amber"}`}>
                            {e.lift} lift
                          </span>
                        </div>
                        <div className="progress-bar" style={{ marginBottom: 8 }}>
                          <div className="progress-fill" style={{
                            width: `${e.importance}%`,
                            background: "linear-gradient(90deg, var(--accent-blue), var(--accent-blue-glow))",
                          }} />
                        </div>
                        <p style={{ fontSize: 12, color: "var(--text-muted)", lineHeight: 1.5, margin: 0 }}>
                          {e.reason}
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Similar Cases */}
              <div className="glass-card" style={{ padding: 28 }}>
                <h2 style={{ fontFamily: "'Manrope', sans-serif", fontSize: 18, fontWeight: 700, marginBottom: 6 }}>
                  🔍 Similar Precedents
                </h2>
                <p style={{ fontSize: 13, color: "var(--text-muted)", marginBottom: 20 }}>
                  Most relevant cases from the 9,675-case corpus
                </p>
                <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                  {result.similarCases.map((c, i) => (
                    <div key={c.id} style={{
                      display: "flex", alignItems: "center", justifyContent: "space-between",
                      background: "var(--bg-workspace)", borderRadius: 10, padding: "12px 16px",
                      border: "1px solid var(--border-ghost)",
                    }}>
                      <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                        <span style={{ fontSize: 13, color: "var(--text-muted)", fontWeight: 600 }}>#{i + 1}</span>
                        <div>
                          <div style={{ fontSize: 13, fontWeight: 500, fontFamily: "'Courier New', monospace", color: "var(--accent-blue-light)" }}>
                            {c.id}
                          </div>
                          <div style={{ fontSize: 12, color: "var(--text-muted)" }}>Year: {c.year}</div>
                        </div>
                      </div>
                      <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                        <span className={`badge ${c.outcome === "Allowed" ? "badge-green" : c.outcome === "Dismissed" ? "badge-red" : "badge-amber"}`}>
                          {c.outcome}
                        </span>
                        <span style={{ fontSize: 13, fontWeight: 700, fontFamily: "'Manrope', sans-serif", color: "var(--accent-blue-light)" }}>
                          {c.similarity}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Contradictions */}
            {result.contradictions.count > 0 && (
              <div className="glass-card" style={{
                padding: 24, borderLeft: "3px solid var(--accent-amber)",
              }}>
                <h3 style={{ fontFamily: "'Manrope', sans-serif", fontSize: 16, fontWeight: 700, marginBottom: 12, display: "flex", alignItems: "center", gap: 8 }}>
                  ⚠️ Potential Contradictions Detected
                </h3>
                {result.contradictions.details.map((d, i) => (
                  <div key={i} style={{ fontSize: 14, color: "var(--text-secondary)", padding: "8px 0", borderTop: i > 0 ? "1px solid var(--border-ghost)" : "none" }}>
                    {d}
                  </div>
                ))}
                <div style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 8 }}>
                  Severity: {result.contradictions.score} — {result.contradictions.score < 0.2 ? "Low (likely not impactful)" : "Moderate (address before filing)"}
                </div>
              </div>
            )}

            {/* Disclaimer */}
            <div style={{
              textAlign: "center", padding: 24, marginTop: 32,
              fontSize: 12, color: "var(--text-muted)", lineHeight: 1.6,
            }}>
              ⚖️ This analysis is for informational purposes only and does not constitute legal advice.
              Predictions are based on statistical patterns in 9,675 historical High Court cases.
              Always consult with a qualified legal professional.
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
