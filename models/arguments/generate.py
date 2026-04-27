"""
models/arguments/generate.py
─────────────────────────────────────────────────────────────────────────────
Argument Generation & Case Improvement Plan Module.

Takes the synthesized signals from the pipeline (judgment probability,
missing evidence, contradictions) and renders them as:
  1. Structured legal arguments FOR and AGAINST the petitioner.
  2. A prioritised, actionable case-improvement plan with clear rationale.

This module is pure text-synthesis logic — no external model loading.
"""

from __future__ import annotations

from typing import Any


# ─────────────────────────────────────────────────────────────────────────────
# Helper utilities
# ─────────────────────────────────────────────────────────────────────────────

def _parse_confidence(value: Any) -> float:
    """Safely parse a confidence string like '72.3%' or a raw float."""
    try:
        return float(str(value).rstrip("%")) / 100.0
    except (ValueError, TypeError):
        return 0.0


def _priority_label(score: float) -> str:
    """Map a 0–1 confidence score to a human-readable priority tier."""
    if score >= 0.70:
        return "HIGH"
    if score >= 0.40:
        return "MEDIUM"
    return "LOW"


# ─────────────────────────────────────────────────────────────────────────────
# Argument Generator
# ─────────────────────────────────────────────────────────────────────────────

def generate_arguments(
    con_dict: dict,
    missing_evidence: list,
    contradictions: dict,
    judgment: dict,
) -> dict:
    """
    Synthesises structured legal arguments from the pipeline signals.

    Returns a dict with keys:
        "summary"          – One-line verdict summary.
        "arguments_for"    – List of argument strings favouring the petitioner.
        "arguments_against"– List of argument strings weakening the case.
        "confidence_note"  – Explanation of the confidence figure.
    """
    args_for: list[str] = []
    args_against: list[str] = []

    # ── Judgment probability signal ──────────────────────────────────────────
    probs = judgment.get("probabilities", {})
    allowed_prob = float(probs.get("allowed", 0.5))
    dismissed_prob = float(probs.get("dismissed", 1 - allowed_prob))
    confidence_raw = _parse_confidence(judgment.get("confidence", "50%"))
    prediction = judgment.get("prediction", "Inconclusive")

    # Argument for petitioner based on statistical precedent
    if allowed_prob > 0.5:
        args_for.append(
            f"Statistical precedent strongly favours the petitioner: {allowed_prob * 100:.1f}% "
            f"of retrieved similar cases were decided in favour of the appellant "
            f"(model confidence: {confidence_raw * 100:.1f}%)."
        )
    else:
        args_against.append(
            f"Statistical precedent weakens the petitioner's position: only {allowed_prob * 100:.1f}% "
            f"of similar cases were allowed, while {dismissed_prob * 100:.1f}% were dismissed."
        )

    # ── RAG signal ───────────────────────────────────────────────────────────
    # (rag_allowed_ratio may appear as a feature in con_dict or judgment dict)
    rag_allowed = float(judgment.get("probabilities", {}).get("allowed", allowed_prob))
    if rag_allowed >= 0.6:
        args_for.append(
            "The case shares substantial factual similarity with historically "
            "allowed precedents in the retrieved corpus."
        )

    # ── Evidence strength ────────────────────────────────────────────────────
    evidence_present = con_dict.get("evidence_present", [])
    if evidence_present:
        evidence_list = ", ".join(evidence_present)
        args_for.append(
            f"The following categories of evidence are present and on record: "
            f"{evidence_list}."
        )
    else:
        args_against.append(
            "No recognised evidence categories were identified in the case record. "
            "This significantly weakens the evidentiary foundation."
        )

    # ── Missing evidence ─────────────────────────────────────────────────────
    for m in missing_evidence:
        score = _parse_confidence(m.get("confidence_score") or m.get("importance", "0%"))
        label = m.get("type") or m.get("evidence", "Unknown evidence")
        strong_rate = m.get("strong_rate", None)

        detail = (
            f"Procuring '{label}' could materially strengthen the case"
            + (f" — present in {strong_rate * 100:.0f}% of similar successful cases."
               if strong_rate is not None else ".")
        )
        args_against.append(
            f"⚠️  Missing evidence [{_priority_label(score)}]: {detail}"
        )

    # ── Contradictions ───────────────────────────────────────────────────────
    for c in contradictions.get("found_contradictions", []):
        severity = float(c.get("severity", 0.5))
        args_against.append(
            f"🔴 Contradiction detected [{_priority_label(severity)}]: "
            f"{c.get('detail', 'An inconsistency was identified in the case record.')} "
            f"(severity: {severity:.2f})"
        )

    # ── Summary line ─────────────────────────────────────────────────────────
    summary = (
        f"AI Prediction: '{prediction}' with {confidence_raw * 100:.1f}% confidence. "
        f"{len(args_for)} supporting argument(s) identified; "
        f"{len(args_against)} risk factor(s) flagged."
    )

    confidence_note = (
        "Confidence is calculated as the weighted outcome probability from the "
        "XGBoost Phi-Vector model (or IDW retrieval fallback). It reflects the "
        "statistical likelihood based on similar historical cases — not a legal guarantee."
    )

    return {
        "summary": summary,
        "arguments_for": args_for,
        "arguments_against": args_against,
        "confidence_note": confidence_note,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Case Improvement Plan Generator
# ─────────────────────────────────────────────────────────────────────────────

def generate_case_improvement_plan(
    missing_evidence: list,
    contradictions: dict,
) -> list[dict]:
    """
    Translates gap-analysis signals into a prioritised, actionable roadmap
    for the advocate to strengthen the case before the next hearing.

    Returns a sorted list of action dicts, each with:
        "priority"     – HIGH / MEDIUM / LOW
        "category"     – 'Evidence' | 'Contradiction'
        "action"       – What to do (human-readable instruction).
        "reason"       – Why this matters (drawn from statistical signals).
        "confidence"   – Numeric score (0–1) for sorting.
    """
    plan: list[dict] = []

    # ── Missing evidence actions ──────────────────────────────────────────────
    for m in missing_evidence:
        score = _parse_confidence(m.get("confidence_score") or m.get("importance", "0%"))
        label = m.get("type") or m.get("evidence", "Unknown Evidence")
        strong_rate = m.get("strong_rate")
        weak_rate = m.get("weak_rate")
        reason_parts = []

        if strong_rate is not None and weak_rate is not None:
            reason_parts.append(
                f"present in {strong_rate * 100:.0f}% of successful cases vs "
                f"{weak_rate * 100:.0f}% of dismissed cases"
            )
        if m.get("log_odds") and float(m.get("log_odds", 0)) > 0:
            reason_parts.append(
                f"positive log-odds signal ({float(m['log_odds']):.2f})"
            )
        if m.get("global_importance") and float(m.get("global_importance", 0)) > 0:
            reason_parts.append(
                f"ranked globally important across the corpus "
                f"(score: {float(m['global_importance']):.2f})"
            )

        reason = (
            "; ".join(reason_parts) + "."
            if reason_parts
            else "This evidence type improves the evidentiary profile of the case."
        )

        plan.append({
            "priority": _priority_label(score),
            "category": "Evidence",
            "action": f"Procure and submit: {label}",
            "reason": reason.capitalize(),
            "confidence": round(score, 4),
        })

    # ── Contradiction resolution actions ─────────────────────────────────────
    for c in contradictions.get("found_contradictions", []):
        severity = float(c.get("severity", 0.5))
        rule_id = c.get("rule_id", c.get("type", "unknown"))
        detail = c.get("detail", "An inconsistency was detected.")

        plan.append({
            "priority": _priority_label(severity),
            "category": "Contradiction",
            "action": f"Resolve '{rule_id}' inconsistency before next hearing.",
            "reason": detail,
            "confidence": round(severity, 4),
        })

    # ── Sort: HIGH first, then by confidence score descending ────────────────
    priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    plan.sort(key=lambda x: (priority_order.get(x["priority"], 3), -x["confidence"]))

    return plan
