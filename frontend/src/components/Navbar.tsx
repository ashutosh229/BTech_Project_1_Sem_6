"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

const tabs = [
  { label: "Analyze Case", href: "/analyze", primary: true },
  { label: "Dashboard", href: "/" },
  { label: "Performance", href: "/performance" },
  { label: "Ablation", href: "/ablation" },
  { label: "Corpus", href: "/corpus" },
];

export default function Navbar() {
  const pathname = usePathname();

  return (
    <nav style={{
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      padding: "14px 32px",
      background: "var(--bg-workspace)",
      borderBottom: "1px solid var(--border-ghost)",
      position: "sticky",
      top: 0,
      zIndex: 100,
      backdropFilter: "blur(12px)",
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 32 }}>
        <Link href="/" style={{ display: "flex", alignItems: "center", gap: 12, textDecoration: "none", color: "inherit" }}>
          <div style={{
            width: 34, height: 34, borderRadius: 9,
            background: "linear-gradient(135deg, var(--accent-blue), var(--accent-blue-glow))",
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: 17,
          }}>⚖</div>
          <span style={{
            fontFamily: "'Manrope', sans-serif",
            fontSize: 17, fontWeight: 700,
            letterSpacing: "-0.02em",
          }}>
            Legal Intelligence
          </span>
        </Link>

        <div style={{ display: "flex", gap: 4 }}>
          {tabs.map((t) => (
            <Link
              key={t.href}
              href={t.href}
              className={`nav-tab ${pathname === t.href ? "active" : ""}`}
              style={t.primary && pathname !== t.href ? {
                background: "linear-gradient(135deg, var(--accent-blue), var(--accent-blue-glow))",
                color: "white",
                fontWeight: 600,
              } : undefined}
            >
              {t.label}
            </Link>
          ))}
        </div>
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
        <span style={{ fontSize: 12, color: "var(--text-muted)" }}>
          9,675 cases indexed
        </span>
        <div style={{
          width: 34, height: 34, borderRadius: "50%",
          background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
          display: "flex", alignItems: "center", justifyContent: "center",
          fontSize: 13, fontWeight: 600, color: "white",
        }}>A</div>
      </div>
    </nav>
  );
}
