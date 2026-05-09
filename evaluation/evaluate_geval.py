"""
evaluation/evaluate_geval.py
──────────────────────────────────────────────────────────────────────────────
G-Eval Evaluation Module (LLM-as-a-Judge via Groq)
Uses a Groq LLM to evaluate the generated reasoning against ground-truth.
"""

import json
import os
import csv
from _common import (
    OUTPUT_DIR,
    load_eligible_cases,
    find_case_file,
    run_pipeline_on_case,
    extract_pipeline_reasoning,
    PROJECT_ROOT
)
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

RESULTS_JSON = os.path.join(OUTPUT_DIR, "geval_results.json")
SUMMARY_CSV  = os.path.join(OUTPUT_DIR, "geval_summary.csv")

def evaluate():
    load_dotenv(os.path.join(PROJECT_ROOT, ".env"))
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        print("GROQ_API_KEY not found. G-Eval requires Groq API.")
        return

    llm = ChatGroq(
        groq_api_key=groq_api_key,
        model_name="llama-3.3-70b-versatile",
        temperature=0.0
    )

    eligible = load_eligible_cases()
    print(f"\n[G-Eval] Starting evaluation for {len(eligible)} cases...")

    results = []
    skipped = 0

    system_prompt = """You are an expert legal evaluator (G-Eval framework).
You will be given a Reference Legal Reasoning and a Generated Legal Reasoning.
Score the Generated Reasoning from 1 to 5 based on:
1. Relevance (Does it address the same issues?)
2. Coherence (Is it logically sound?)
3. Factuality (Is it consistent with the reference?)
4. Overall Quality

Return ONLY a valid JSON object with the following keys, and no other text:
{
  "relevance": float,
  "coherence": float,
  "factuality": float,
  "overall": float
}
"""

    for idx, case_entry in enumerate(eligible, 1):
        case_id = case_entry.get("case_id", f"case_{idx}")
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

        user_prompt = f"Reference Reasoning:\n{gt_reasoning}\n\nGenerated Reasoning:\n{generated_text}"

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]

        try:
            response = llm.invoke(messages)
            content = response.content.strip()
            if content.startswith("```json"):
                content = content.strip("```json").strip("```").strip()
            
            scores = json.loads(content)
            
            rec = {
                "case_id": case_id,
                "geval_scores": {
                    "relevance": scores.get("relevance", 0.0),
                    "coherence": scores.get("coherence", 0.0),
                    "factuality": scores.get("factuality", 0.0),
                    "overall": scores.get("overall", 0.0),
                }
            }
            results.append(rec)
            print(f"G-Eval Overall: {scores.get('overall', 0.0)}")

        except Exception as e:
            print(f"G-Eval LLM error: {e}")
            skipped += 1
            continue

    def avg(subkey):
        vals = [r["geval_scores"][subkey] for r in results]
        return sum(vals)/len(vals) if vals else 0.0

    summary = {
        "total_evaluated": len(results),
        "total_skipped": skipped,
        "avg_relevance": avg("relevance"),
        "avg_coherence": avg("coherence"),
        "avg_factuality": avg("factuality"),
        "avg_overall": avg("overall"),
    }

    with open(RESULTS_JSON, "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "results": results}, f, indent=2)

    with open(SUMMARY_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["case_id", "relevance", "coherence", "factuality", "overall"])
        writer.writeheader()
        for r in results:
            writer.writerow({
                "case_id": r["case_id"],
                "relevance": r["geval_scores"]["relevance"],
                "coherence": r["geval_scores"]["coherence"],
                "factuality": r["geval_scores"]["factuality"],
                "overall": r["geval_scores"]["overall"],
            })

    print("\n=== G-EVAL SUMMARY ===")
    print(f"Evaluated: {summary['total_evaluated']}")
    print(f"Avg Overall: {summary['avg_overall']:.4f}")

if __name__ == "__main__":
    evaluate()
