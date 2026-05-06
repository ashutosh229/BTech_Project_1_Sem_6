"""
evaluation/evaluate_blanc.py
──────────────────────────────────────────────────────────────────────────────
BLANC Evaluation Module (BLANC-help & BLANC-tune)
"""

import json
import os
import csv

# Patch transformers.AdamW for older blanc package compatibility
import torch
import transformers
from torch.optim import AdamW
transformers.AdamW = AdamW

from blanc import BlancHelp, BlancTune
from _common import (
    OUTPUT_DIR,
    load_eligible_cases,
    find_case_file,
    run_pipeline_on_case,
    extract_pipeline_reasoning
)

RESULTS_JSON = os.path.join(OUTPUT_DIR, "blanc_results.json")
SUMMARY_CSV  = os.path.join(OUTPUT_DIR, "blanc_summary.csv")

def evaluate():
    eligible = load_eligible_cases()
    print(f"\n[BLANC] Starting evaluation for {len(eligible)} cases...")

    try:
        blanc_help = BlancHelp()
        blanc_tune = BlancTune()
    except Exception as e:
        print(f"Failed to initialize BLANC: {e}")
        return

    results = []
    skipped = 0

    for idx, case_entry in enumerate(eligible, 1):
        case_id = case_entry.get("case_id", f"case_{idx}")
        # BLANC evaluates summary against source document.
        # For our purposes: Document = Ground-Truth Reasoning, Summary = Generated Text
        document = case_entry.get("reasoning", "")
        
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
        if not generated_text or not document:
            print("Empty generated text or reasoning.")
            skipped += 1
            continue

        # Due to BLANC's potential slowness, evaluate one by one
        try:
            score_help = blanc_help.eval_once(document, generated_text)
            score_tune = blanc_tune.eval_once(document, generated_text)
        except Exception as e:
            print(f"Error evaluating BLANC: {e}")
            skipped += 1
            continue

        rec = {
            "case_id": case_id,
            "blanc_help": score_help,
            "blanc_tune": score_tune
        }
        results.append(rec)
        print(f"BLANC-help: {score_help:.4f} | BLANC-tune: {score_tune:.4f}")

    def avg(key):
        vals = [r[key] for r in results]
        return sum(vals)/len(vals) if vals else 0.0

    summary = {
        "total_evaluated": len(results),
        "total_skipped": skipped,
        "avg_blanc_help": avg("blanc_help"),
        "avg_blanc_tune": avg("blanc_tune"),
    }

    with open(RESULTS_JSON, "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "results": results}, f, indent=2)

    with open(SUMMARY_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["case_id", "blanc_help", "blanc_tune"])
        writer.writeheader()
        for r in results:
            writer.writerow({
                "case_id": r["case_id"],
                "blanc_help": r["blanc_help"],
                "blanc_tune": r["blanc_tune"],
            })

    print("\n=== BLANC SUMMARY ===")
    print(f"Evaluated: {summary['total_evaluated']}")
    print(f"Avg BLANC-help: {summary['avg_blanc_help']:.4f}")
    print(f"Avg BLANC-tune: {summary['avg_blanc_tune']:.4f}")

if __name__ == "__main__":
    evaluate()
