"""
evaluation/evaluate_bleu.py
──────────────────────────────────────────────────────────────────────────────
BLEU Evaluation  (BLEU-1 / 2 / 3 / 4)

For every eligible case in conclusions_data.json:
  1. Strip answer sections from the raw case JSON.
  2. Run run_pipeline() to obtain the generated reasoning narrative.
  3. Compute sentence-BLEU (with smoothing) and corpus-BLEU against both
     the stored ground-truth conclusion and the court's reasoning.

Outputs
  outputs/bleu_results.json   – per-case records + summary
  outputs/bleu_summary.csv    – per-case BLEU scores (spreadsheet-friendly)
"""

import json
import os
import sys
import csv
import copy
import tempfile
import traceback
from pathlib import Path

# ── Project root on sys.path ──────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import nltk
from nltk.translate.bleu_score import sentence_bleu, corpus_bleu, SmoothingFunction

try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt", quiet=True)
try:
    nltk.data.find("tokenizers/punkt_tab")
except LookupError:
    nltk.download("punkt_tab", quiet=True)

from main_pipeline import run_pipeline

# ── Config ────────────────────────────────────────────────────────────────────
CONCLUSIONS_DB = str(PROJECT_ROOT / "data" / "conclusions_data.json")
DATA_DIR       = str(PROJECT_ROOT / "data")
OUTPUT_DIR     = str(PROJECT_ROOT / "outputs")
RESULTS_JSON   = os.path.join(OUTPUT_DIR, "bleu_results.json")
SUMMARY_CSV    = os.path.join(OUTPUT_DIR, "bleu_summary.csv")

SECTIONS_TO_STRIP = {
    "Conclusion", "Court's Reasoning", "Judgment", "Judgement",
    "Final Order", "Analysis of the law", "Analysis",
}

MAX_CASES = 200  # set None to run all

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

def tokenize(text: str) -> list[str]:
    return nltk.word_tokenize(text.lower()) if text else []


def bleu_score(hypothesis: str, reference: str) -> dict:
    """Sentence-BLEU (BLEU-1 through 4) with Chen & Cherry smoothing."""
    hyp = tokenize(hypothesis)
    ref = tokenize(reference)
    if not hyp or not ref:
        return {"bleu1": 0.0, "bleu2": 0.0, "bleu3": 0.0, "bleu4": 0.0}
    sf   = SmoothingFunction().method1
    refs = [ref]
    return {
        "bleu1": round(sentence_bleu(refs, hyp, weights=(1, 0, 0, 0), smoothing_function=sf), 4),
        "bleu2": round(sentence_bleu(refs, hyp, weights=(0.5, 0.5, 0, 0), smoothing_function=sf), 4),
        "bleu3": round(sentence_bleu(refs, hyp, weights=(1/3, 1/3, 1/3, 0), smoothing_function=sf), 4),
        "bleu4": round(sentence_bleu(refs, hyp, weights=(0.25, 0.25, 0.25, 0.25), smoothing_function=sf), 4),
    }


def strip_sections(raw_data: dict) -> dict:
    sanitised = copy.deepcopy(raw_data)
    ebt = sanitised.get("elements_by_title", {})
    for sec in SECTIONS_TO_STRIP:
        ebt.pop(sec, None)
    if "all_paragraphs" in sanitised:
        sanitised["all_paragraphs"] = [
            p for p in sanitised["all_paragraphs"]
            if p.get("title") not in SECTIONS_TO_STRIP
        ]
    return sanitised


_CASE_FILE_CACHE = None

def find_case_file(case_entry: dict) -> str | None:
    global _CASE_FILE_CACHE
    if _CASE_FILE_CACHE is None:
        _CASE_FILE_CACHE = {}
        if os.path.exists(DATA_DIR):
            for fname in os.listdir(DATA_DIR):
                if fname.endswith(".json"):
                    base = fname.rsplit(".", 1)[0]
                    cid  = base.split("_")[-1]
                    _CASE_FILE_CACHE[cid] = os.path.join(DATA_DIR, fname)
    case_id = case_entry.get("case_id")
    return _CASE_FILE_CACHE.get(case_id) if case_id else None


def extract_pipeline_reasoning(result: dict) -> str:
    explanation = result.get("explanation", {})
    narrative   = explanation.get("summary_narrative", "")
    if narrative:
        return narrative
    steps = explanation.get("logical_steps", [])
    if steps:
        return " ".join(steps)
    jp      = result.get("judgment_probability", {})
    ll      = jp.get("reasoning", {}).get("legal_logic", [])
    return " ".join(ll) if ll else ""


# ── Evaluation loop ───────────────────────────────────────────────────────────

def run_evaluation():
    print("\n📂 Loading conclusions database …")
    with open(CONCLUSIONS_DB, "r", encoding="utf-8") as f:
        db = json.load(f)

    all_cases = db.get("conclusions", [])
    eligible  = []
    for c in all_cases:
        if c.get("conclusion") and c.get("reasoning") and find_case_file(c):
            eligible.append(c)
            if MAX_CASES and len(eligible) >= MAX_CASES:
                break

    print(f"✓ Total in DB  : {len(all_cases)}")
    print(f"✓ Eligible     : {len(eligible)}")

    results, skipped = [], 0
    hyp_c, ref_c, hyp_r, ref_r = [], [], [], []

    for idx, entry in enumerate(eligible, 1):
        case_id      = entry.get("case_id", f"case_{idx}")
        gt_conclusion = entry["conclusion"]
        gt_reasoning  = entry["reasoning"]
        print(f"\n[{idx}/{len(eligible)}] {case_id}", end=" … ")

        case_file = find_case_file(entry)
        if not case_file:
            print("⚠️  file not found — skipped"); skipped += 1; continue

        try:
            with open(case_file, "r", encoding="utf-8") as f:
                raw = json.load(f)
        except Exception as e:
            print(f"✗ read error: {e}"); skipped += 1; continue

        sanitised = strip_sections(raw)

        try:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".json", delete=False, encoding="utf-8"
            ) as tmp:
                json.dump(sanitised, tmp, ensure_ascii=False)
                tmp_path = tmp.name
        except Exception as e:
            print(f"✗ temp file: {e}"); skipped += 1; continue

        try:
            pipeline_result = run_pipeline(tmp_path)
        except Exception as e:
            print(f"✗ pipeline: {e}"); traceback.print_exc()
            skipped += 1; os.unlink(tmp_path); continue
        finally:
            try: os.unlink(tmp_path)
            except Exception: pass

        gen_text = extract_pipeline_reasoning(pipeline_result)
        if not gen_text:
            print("⚠️  empty output — skipped"); skipped += 1; continue

        sc = bleu_score(gen_text, gt_conclusion)
        sr = bleu_score(gen_text, gt_reasoning)

        hyp_tok = tokenize(gen_text)
        hyp_c.append(hyp_tok); ref_c.append([tokenize(gt_conclusion)])
        hyp_r.append(hyp_tok); ref_r.append([tokenize(gt_reasoning)])

        results.append({
            "case_id"             : case_id,
            "case_title"          : entry.get("case_title", ""),
            "url"                 : entry.get("url", ""),
            "generated_reasoning" : gen_text,
            "bleu_vs_conclusion"  : sc,
            "bleu_vs_reasoning"   : sr,
        })
        print(f"✓  BLEU-4 vs Conclusion: {sc['bleu4']:.4f} | vs Reasoning: {sr['bleu4']:.4f}")

    # Corpus-level BLEU
    sf = SmoothingFunction().method1
    cb_c = round(corpus_bleu(ref_c, hyp_c, smoothing_function=sf), 4) if hyp_c else 0.0
    cb_r = round(corpus_bleu(ref_r, hyp_r, smoothing_function=sf), 4) if hyp_r else 0.0

    def avg(field, key):
        vals = [r[f"bleu_vs_{field}"][key] for r in results]
        return round(sum(vals) / len(vals), 4) if vals else 0.0

    summary = {
        "metric"                              : "BLEU",
        "total_evaluated"                     : len(results),
        "total_skipped"                       : skipped,
        "corpus_bleu4_vs_conclusion"          : cb_c,
        "corpus_bleu4_vs_reasoning"           : cb_r,
        "avg_sentence_bleu1_vs_conclusion"    : avg("conclusion", "bleu1"),
        "avg_sentence_bleu2_vs_conclusion"    : avg("conclusion", "bleu2"),
        "avg_sentence_bleu3_vs_conclusion"    : avg("conclusion", "bleu3"),
        "avg_sentence_bleu4_vs_conclusion"    : avg("conclusion", "bleu4"),
        "avg_sentence_bleu1_vs_reasoning"     : avg("reasoning",  "bleu1"),
        "avg_sentence_bleu2_vs_reasoning"     : avg("reasoning",  "bleu2"),
        "avg_sentence_bleu3_vs_reasoning"     : avg("reasoning",  "bleu3"),
        "avg_sentence_bleu4_vs_reasoning"     : avg("reasoning",  "bleu4"),
    }

    with open(RESULTS_JSON, "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "results": results}, f, indent=2, ensure_ascii=False)

    csv_fields = [
        "case_id", "case_title",
        "bleu1_vs_conclusion", "bleu2_vs_conclusion",
        "bleu3_vs_conclusion", "bleu4_vs_conclusion",
        "bleu1_vs_reasoning",  "bleu2_vs_reasoning",
        "bleu3_vs_reasoning",  "bleu4_vs_reasoning",
    ]
    with open(SUMMARY_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=csv_fields)
        w.writeheader()
        for r in results:
            w.writerow({
                "case_id"             : r["case_id"],
                "case_title"          : r["case_title"],
                "bleu1_vs_conclusion" : r["bleu_vs_conclusion"]["bleu1"],
                "bleu2_vs_conclusion" : r["bleu_vs_conclusion"]["bleu2"],
                "bleu3_vs_conclusion" : r["bleu_vs_conclusion"]["bleu3"],
                "bleu4_vs_conclusion" : r["bleu_vs_conclusion"]["bleu4"],
                "bleu1_vs_reasoning"  : r["bleu_vs_reasoning"]["bleu1"],
                "bleu2_vs_reasoning"  : r["bleu_vs_reasoning"]["bleu2"],
                "bleu3_vs_reasoning"  : r["bleu_vs_reasoning"]["bleu3"],
                "bleu4_vs_reasoning"  : r["bleu_vs_reasoning"]["bleu4"],
            })

    print("\n" + "=" * 70)
    print("📊 BLEU EVALUATION SUMMARY")
    print("=" * 70)
    print(f"  Cases evaluated      : {summary['total_evaluated']}")
    print(f"  Cases skipped        : {summary['total_skipped']}")
    print(f"\n  ── vs Ground-Truth CONCLUSION ──")
    print(f"  Corpus BLEU-4        : {summary['corpus_bleu4_vs_conclusion']}")
    print(f"  Avg Sentence BLEU-1  : {summary['avg_sentence_bleu1_vs_conclusion']}")
    print(f"  Avg Sentence BLEU-4  : {summary['avg_sentence_bleu4_vs_conclusion']}")
    print(f"\n  ── vs Ground-Truth COURT'S REASONING ──")
    print(f"  Corpus BLEU-4        : {summary['corpus_bleu4_vs_reasoning']}")
    print(f"  Avg Sentence BLEU-4  : {summary['avg_sentence_bleu4_vs_reasoning']}")
    print("=" * 70)
    print(f"\n💾  {RESULTS_JSON}")
    print(f"📋  {SUMMARY_CSV}\n")

    return summary


if __name__ == "__main__":
    run_evaluation()
