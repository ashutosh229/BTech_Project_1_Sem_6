"""
evaluation/run_all.py
──────────────────────────────────────────────────────────────────────────────
Run all evaluation metrics and generate a consolidated final report.
"""

import os
import json
import csv
from _common import OUTPUT_DIR, PROJECT_ROOT

def run_script(script_name):
    print(f"\n{'='*70}")
    print(f"Executing {script_name}...")
    print(f"{'='*70}")
    os.system(f"python evaluation/{script_name}")

def merge_results():
    print(f"\n{'='*70}")
    print("Merging Results into Final Consolidated Report")
    print(f"{'='*70}")
    
    # Check for outputs
    results = {}
    
    metrics = {
        "rouge": os.path.join(OUTPUT_DIR, "rouge_results.json"),
        "meteor": os.path.join(OUTPUT_DIR, "meteor_results.json"),
        "bertscore": os.path.join(OUTPUT_DIR, "bertscore_results.json"),
        "blanc": os.path.join(OUTPUT_DIR, "blanc_results.json"),
        "geval": os.path.join(OUTPUT_DIR, "geval_results.json"),
        "expert": os.path.join(OUTPUT_DIR, "expert_results.json"),
        "bleu": os.path.join(OUTPUT_DIR, "bleu_results.json")
    }

    consolidated_summary = {}
    per_case_results = {}

    for metric_name, filepath in metrics.items():
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                consolidated_summary[metric_name] = data.get("summary", {})
                
                for res in data.get("results", []):
                    case_id = res["case_id"]
                    if case_id not in per_case_results:
                        per_case_results[case_id] = {}
                    per_case_results[case_id][metric_name] = res

    # Write Consolidated JSON
    final_json = os.path.join(OUTPUT_DIR, "final_evaluation_report.json")
    with open(final_json, "w", encoding="utf-8") as f:
        json.dump({
            "overall_summary": consolidated_summary,
            "case_level_results": per_case_results
        }, f, indent=2)

    # Write Consolidated CSV
    final_csv = os.path.join(OUTPUT_DIR, "final_evaluation_report.csv")
    if per_case_results:
        # Determine all possible fields
        fields = ["case_id"]
        for metric in metrics.keys():
            fields.append(f"{metric}_score")
            
        with open(final_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
            writer.writeheader()
            
            for case_id, scores in per_case_results.items():
                row = {"case_id": case_id}
                
                if "rouge" in scores:
                    row["rouge_score"] = scores["rouge"]["rouge_vs_reasoning"]["rougeL_fmeasure"]
                if "meteor" in scores:
                    row["meteor_score"] = scores["meteor"]["meteor_vs_reasoning"]
                if "bertscore" in scores:
                    row["bertscore_score"] = scores["bertscore"]["bertscore_vs_reasoning"]["f1"]
                if "blanc" in scores:
                    row["blanc_score"] = scores["blanc"].get("blanc_tune", 0.0)
                if "geval" in scores:
                    row["geval_score"] = scores["geval"]["geval_scores"]["overall"]
                if "expert" in scores:
                    row["expert_score"] = scores["expert"]["expert_score"]
                if "bleu" in scores:
                    row["bleu_score"] = scores["bleu"]["bleu_vs_reasoning"]["bleu4"]
                    
                writer.writerow(row)
                
    print(f"Final Report JSON: {final_json}")
    print(f"Final Report CSV: {final_csv}")

def main():
    # To run all scripts, we first need to make sure we are at the project root
    os.chdir(PROJECT_ROOT)
    
    scripts = [
        # "evaluate_bleu.py",  # Original exists in scripts/
        "evaluate_rouge.py",
        "evaluate_meteor.py",
        "evaluate_bertscore.py",
        "evaluate_blanc.py",
        "evaluate_geval.py",
        "evaluate_expert.py"
    ]
    
    print("Starting NyayaRAG Evaluation Suite")
    
    # Let the user know they can run individual scripts or all of them
    for script in scripts:
        print(f"  - {script}")
        
    print("\nNote: BLANC and BERTScore may take a long time to run.")
    print("Note: G-Eval requires GROQ_API_KEY in .env")
    
    # Run them automatically
    for script in scripts:
        run_script(script)
        
    # Merge results from whatever has been run so far
    merge_results()
    
    print("\nDone!")

if __name__ == "__main__":
    main()
