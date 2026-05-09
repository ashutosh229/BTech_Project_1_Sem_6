"""
evaluation/evaluate_meteor.py
──────────────────────────────────────────────────────────────────────────────
METEOR Evaluation Module
"""

import json
import os
import csv
import nltk
from nltk.translate.meteor_score import single_meteor_score
from _common import (
    OUTPUT_DIR,
    load_eligible_cases,
    find_case_file,
    run_pipeline_on_case,
    extract_pipeline_reasoning
)

try:
    nltk.data.find("corpora/wordnet")
except LookupError:
    nltk.download("wordnet", quiet=True)
try:
    nltk.data.find("corpora/omw-1.4")
except LookupError:
    nltk.download("omw-1.4", quiet=True)


RESULTS_JSON = os.path.join(OUTPUT_DIR, "meteor_results.json")
SUMMARY_CSV  = os.path.join(OUTPUT_DIR, "meteor_summary.csv")

def tokenize(text: str) -> list[str]:
    return nltk.word_tokenize(text) if text else []

def evaluate():
    eligible = load_eligible_cases()
    print(f"\n[METEOR] Starting evaluation for {len(eligible)} cases...")

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

        gen_tokens = tokenize(generated_text)
        gt_c_tokens = tokenize(gt_conclusion)
        gt_r_tokens = tokenize(gt_reasoning)

        score_c = single_meteor_score(gt_c_tokens, gen_tokens) if gt_c_tokens and gen_tokens else 0.0
        score_r = single_meteor_score(gt_r_tokens, gen_tokens) if gt_r_tokens and gen_tokens else 0.0

        rec = {
            "case_id": case_id,
            "meteor_vs_conclusion": score_c,
            "meteor_vs_reasoning": score_r
        }
        results.append(rec)
        print(f"METEOR(C): {score_c:.4f} | METEOR(R): {score_r:.4f}")

    def avg(key):
        vals = [r[key] for r in results]
        return sum(vals)/len(vals) if vals else 0.0

    summary = {
        "total_evaluated": len(results),
        "total_skipped": skipped,
        "avg_meteor_vs_conclusion": avg("meteor_vs_conclusion"),
        "avg_meteor_vs_reasoning": avg("meteor_vs_reasoning"),
    }

    with open(RESULTS_JSON, "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "results": results}, f, indent=2)

    with open(SUMMARY_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["case_id", "meteor_c", "meteor_r"])
        writer.writeheader()
        for r in results:
            writer.writerow({
                "case_id": r["case_id"],
                "meteor_c": r["meteor_vs_conclusion"],
                "meteor_r": r["meteor_vs_reasoning"],
            })

    print("\n=== METEOR SUMMARY ===")
    print(f"Evaluated: {summary['total_evaluated']}")
    print(f"METEOR vs Conclusion: {summary['avg_meteor_vs_conclusion']:.4f}")
    print(f"METEOR vs Reasoning : {summary['avg_meteor_vs_reasoning']:.4f}")

if __name__ == "__main__":
    evaluate()
