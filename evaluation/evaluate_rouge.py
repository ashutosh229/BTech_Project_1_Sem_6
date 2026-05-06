"""
evaluation/evaluate_rouge.py
──────────────────────────────────────────────────────────────────────────────
ROUGE Evaluation Module (ROUGE-1, ROUGE-2, ROUGE-L)
"""

import json
import os
import csv
from rouge_score import rouge_scorer
from _common import (
    OUTPUT_DIR,
    load_eligible_cases,
    find_case_file,
    run_pipeline_on_case,
    extract_pipeline_reasoning
)

RESULTS_JSON = os.path.join(OUTPUT_DIR, "rouge_results.json")
SUMMARY_CSV  = os.path.join(OUTPUT_DIR, "rouge_summary.csv")

def evaluate():
    eligible = load_eligible_cases()
    print(f"\n[ROUGE] Starting evaluation for {len(eligible)} cases...")

    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    results = []
    skipped = 0

    for idx, case_entry in enumerate(eligible, 1):
        case_id = case_entry.get("case_id", f"case_{idx}")
        gt_conclusion = case_entry.get("conclusion", "")
        gt_reasoning  = case_entry.get("reasoning", "")
        
        print(f"[{idx}/{len(eligible)}] {case_id}", end=" ... ")

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

        # Evaluate against Conclusion
        scores_c = scorer.score(gt_conclusion, generated_text)
        # Evaluate against Reasoning
        scores_r = scorer.score(gt_reasoning, generated_text)

        rec = {
            "case_id": case_id,
            "rouge_vs_conclusion": {
                "rouge1_fmeasure": scores_c['rouge1'].fmeasure,
                "rouge2_fmeasure": scores_c['rouge2'].fmeasure,
                "rougeL_fmeasure": scores_c['rougeL'].fmeasure,
            },
            "rouge_vs_reasoning": {
                "rouge1_fmeasure": scores_r['rouge1'].fmeasure,
                "rouge2_fmeasure": scores_r['rouge2'].fmeasure,
                "rougeL_fmeasure": scores_r['rougeL'].fmeasure,
            }
        }
        results.append(rec)
        print(f"R-L(C): {scores_c['rougeL'].fmeasure:.4f} | R-L(R): {scores_r['rougeL'].fmeasure:.4f}")

    # Compute Averages
    def avg(key, subkey):
        vals = [r[key][subkey] for r in results]
        return sum(vals)/len(vals) if vals else 0.0

    summary = {
        "total_evaluated": len(results),
        "total_skipped": skipped,
        "avg_rouge1_vs_conclusion": avg("rouge_vs_conclusion", "rouge1_fmeasure"),
        "avg_rouge2_vs_conclusion": avg("rouge_vs_conclusion", "rouge2_fmeasure"),
        "avg_rougeL_vs_conclusion": avg("rouge_vs_conclusion", "rougeL_fmeasure"),
        "avg_rouge1_vs_reasoning": avg("rouge_vs_reasoning", "rouge1_fmeasure"),
        "avg_rouge2_vs_reasoning": avg("rouge_vs_reasoning", "rouge2_fmeasure"),
        "avg_rougeL_vs_reasoning": avg("rouge_vs_reasoning", "rougeL_fmeasure"),
    }

    with open(RESULTS_JSON, "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "results": results}, f, indent=2)

    with open(SUMMARY_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["case_id", "rouge1_c", "rouge2_c", "rougeL_c", "rouge1_r", "rouge2_r", "rougeL_r"])
        writer.writeheader()
        for r in results:
            writer.writerow({
                "case_id": r["case_id"],
                "rouge1_c": r["rouge_vs_conclusion"]["rouge1_fmeasure"],
                "rouge2_c": r["rouge_vs_conclusion"]["rouge2_fmeasure"],
                "rougeL_c": r["rouge_vs_conclusion"]["rougeL_fmeasure"],
                "rouge1_r": r["rouge_vs_reasoning"]["rouge1_fmeasure"],
                "rouge2_r": r["rouge_vs_reasoning"]["rouge2_fmeasure"],
                "rougeL_r": r["rouge_vs_reasoning"]["rougeL_fmeasure"],
            })

    print("\n=== ROUGE SUMMARY ===")
    print(f"Evaluated: {summary['total_evaluated']}")
    print(f"R-L vs Conclusion: {summary['avg_rougeL_vs_conclusion']:.4f}")
    print(f"R-L vs Reasoning : {summary['avg_rougeL_vs_reasoning']:.4f}")

if __name__ == "__main__":
    evaluate()
