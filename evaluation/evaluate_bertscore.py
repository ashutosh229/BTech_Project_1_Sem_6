"""
evaluation/evaluate_bertscore.py
──────────────────────────────────────────────────────────────────────────────
BERTScore Evaluation Module
"""

import json
import os
import csv
from bert_score import score
from _common import (
    OUTPUT_DIR,
    load_eligible_cases,
    find_case_file,
    run_pipeline_on_case,
    extract_pipeline_reasoning
)

RESULTS_JSON = os.path.join(OUTPUT_DIR, "bertscore_results.json")
SUMMARY_CSV  = os.path.join(OUTPUT_DIR, "bertscore_summary.csv")

def evaluate():
    eligible = load_eligible_cases()
    print(f"\n[BERTScore] Starting evaluation for {len(eligible)} cases...")

    results = []
    skipped = 0

    hypotheses = []
    references_c = []
    references_r = []
    case_ids = []

    for idx, case_entry in enumerate(eligible, 1):
        case_id = case_entry.get("case_id", f"case_{idx}")
        gt_conclusion = case_entry.get("conclusion", "")
        gt_reasoning  = case_entry.get("reasoning", "")
        
        print(f"[{idx}/{len(eligible)}] {case_id} (Collecting data)", end=" ... ")

        case_file = find_case_file(case_entry)
        if not case_file:
            print("File not found.")
            skipped += 1
            continue

        pipeline_result = run_pipeline_on_case(case_file)
        if not pipeline_result:
            skipped += 1
            continue

        generated_text = extract_pipeline_reasoning(pipeline_result)
        if not generated_text:
            print("Empty generated text.")
            skipped += 1
            continue

        hypotheses.append(generated_text)
        references_c.append(gt_conclusion)
        references_r.append(gt_reasoning)
        case_ids.append(case_id)
        print("Done.")

    if not hypotheses:
        print("No cases to evaluate.")
        return

    print("\nRunning BERTScore vs Conclusion...")
    P_c, R_c, F1_c = score(hypotheses, references_c, lang='en', verbose=True)
    
    print("\nRunning BERTScore vs Reasoning...")
    P_r, R_r, F1_r = score(hypotheses, references_r, lang='en', verbose=True)

    for i in range(len(hypotheses)):
        rec = {
            "case_id": case_ids[i],
            "bertscore_vs_conclusion": {
                "precision": float(P_c[i]),
                "recall": float(R_c[i]),
                "f1": float(F1_c[i]),
            },
            "bertscore_vs_reasoning": {
                "precision": float(P_r[i]),
                "recall": float(R_r[i]),
                "f1": float(F1_r[i]),
            }
        }
        results.append(rec)

    def avg(key, subkey):
        vals = [r[key][subkey] for r in results]
        return sum(vals)/len(vals) if vals else 0.0

    summary = {
        "total_evaluated": len(results),
        "total_skipped": skipped,
        "avg_f1_vs_conclusion": avg("bertscore_vs_conclusion", "f1"),
        "avg_f1_vs_reasoning": avg("bertscore_vs_reasoning", "f1"),
    }

    with open(RESULTS_JSON, "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "results": results}, f, indent=2)

    with open(SUMMARY_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["case_id", "p_c", "r_c", "f1_c", "p_r", "r_r", "f1_r"])
        writer.writeheader()
        for r in results:
            writer.writerow({
                "case_id": r["case_id"],
                "p_c": r["bertscore_vs_conclusion"]["precision"],
                "r_c": r["bertscore_vs_conclusion"]["recall"],
                "f1_c": r["bertscore_vs_conclusion"]["f1"],
                "p_r": r["bertscore_vs_reasoning"]["precision"],
                "r_r": r["bertscore_vs_reasoning"]["recall"],
                "f1_r": r["bertscore_vs_reasoning"]["f1"],
            })

    print("\n=== BERTSCORE SUMMARY ===")
    print(f"Evaluated: {summary['total_evaluated']}")
    print(f"Avg F1 vs Conclusion: {summary['avg_f1_vs_conclusion']:.4f}")
    print(f"Avg F1 vs Reasoning : {summary['avg_f1_vs_reasoning']:.4f}")

if __name__ == "__main__":
    evaluate()
