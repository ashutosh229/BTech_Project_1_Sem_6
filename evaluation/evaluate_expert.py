"""
evaluation/evaluate_expert.py
──────────────────────────────────────────────────────────────────────────────
Expert Score Evaluation Module
Aggregates human expert evaluations if available in the database.
"""

import json
import os
import csv
from _common import (
    OUTPUT_DIR,
    load_eligible_cases
)

RESULTS_JSON = os.path.join(OUTPUT_DIR, "expert_results.json")
SUMMARY_CSV  = os.path.join(OUTPUT_DIR, "expert_summary.csv")

def evaluate():
    eligible = load_eligible_cases()
    print(f"\n[Expert Score] Compiling expert annotations for {len(eligible)} cases...")

    results = []
    skipped = 0

    for idx, case_entry in enumerate(eligible, 1):
        case_id = case_entry.get("case_id", f"case_{idx}")
        
        # Look for expert annotations in the conclusions data or a separate annotation DB
        # Assuming expert_score might be embedded in case_entry if provided
        expert_score = case_entry.get("expert_score")
        
        if expert_score is None:
            # We don't have expert annotations for this case
            skipped += 1
            continue

        rec = {
            "case_id": case_id,
            "expert_score": float(expert_score)
        }
        results.append(rec)

    if not results:
        print("No expert annotations found in the data.")
        return

    def avg(key):
        vals = [r[key] for r in results]
        return sum(vals)/len(vals) if vals else 0.0

    summary = {
        "total_evaluated": len(results),
        "total_skipped": skipped,
        "avg_expert_score": avg("expert_score")
    }

    with open(RESULTS_JSON, "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "results": results}, f, indent=2)

    with open(SUMMARY_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["case_id", "expert_score"])
        writer.writeheader()
        for r in results:
            writer.writerow({
                "case_id": r["case_id"],
                "expert_score": r["expert_score"]
            })

    print("\n=== EXPERT SCORE SUMMARY ===")
    print(f"Annotated Cases: {summary['total_evaluated']}")
    print(f"Avg Expert Score: {summary['avg_expert_score']:.4f}")

if __name__ == "__main__":
    evaluate()
