"""
scripts/evaluate_bleu.py
─────────────────────────────────────────────────────────────────────────────
BLEU Evaluation Pipeline

For every case in conclusions_data.json that has both a ground-truth
`conclusion` and `reasoning`:

  1. Load the raw case JSON from data/.
  2. Strip out the "Conclusion" and "Court's Reasoning" sections so the
     pipeline cannot see the answer.
  3. Run the sanitised case through run_pipeline() (main_pipeline.py).
  4. Extract the pipeline's generated explanation (LLM-induced reasoning).
  5. Compute corpus-level and sentence-level BLEU scores against:
       • the stored ground-truth conclusion
       • the stored court's reasoning
  6. Save per-case results to outputs/bleu_results.json and a summary CSV
     to outputs/bleu_summary.csv.
"""

import json
import os
import sys
import csv
import copy
import tempfile
import traceback
from pathlib import Path

# ── Make project root importable ─────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from nltk.translate.bleu_score import sentence_bleu, corpus_bleu, SmoothingFunction
import nltk

# Download punkt tokeniser if needed (silent)
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt", quiet=True)
try:
    nltk.data.find("tokenizers/punkt_tab")
except LookupError:
    nltk.download("punkt_tab", quiet=True)

from main_pipeline import run_pipeline

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────
CONCLUSIONS_DB  = str(PROJECT_ROOT / "data" / "conclusions_data.json")
DATA_DIR        = str(PROJECT_ROOT / "data")
OUTPUT_DIR      = str(PROJECT_ROOT / "outputs")
RESULTS_JSON    = os.path.join(OUTPUT_DIR, "bleu_results.json")
SUMMARY_CSV     = os.path.join(OUTPUT_DIR, "bleu_summary.csv")

# Sections to STRIP before running the pipeline (so the model cannot cheat)
SECTIONS_TO_STRIP = {
    "Conclusion", "Court's Reasoning", "Judgment", "Judgement", 
    "Final Order", "Analysis of the law", "Analysis"
}

# How many cases to evaluate (set to None to run all)
MAX_CASES = 200  # Reduced for Groq LLM evaluation

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def tokenize(text: str) -> list[str]:
    """Lower-case word tokenisation."""
    return nltk.word_tokenize(text.lower()) if text else []


def bleu_score(hypothesis: str, reference: str) -> dict:
    """
    Compute sentence-BLEU with smoothing (BLEU-1 through BLEU-4).
    Returns a dict with individual n-gram scores.
    """
    hyp_tokens = tokenize(hypothesis)
    ref_tokens  = tokenize(reference)

    if not hyp_tokens or not ref_tokens:
        return {"bleu1": 0.0, "bleu2": 0.0, "bleu3": 0.0, "bleu4": 0.0}

    sf = SmoothingFunction().method1
    refs = [ref_tokens]   # sentence_bleu expects list of references

    return {
        "bleu1": round(sentence_bleu(refs, hyp_tokens, weights=(1, 0, 0, 0), smoothing_function=sf), 4),
        "bleu2": round(sentence_bleu(refs, hyp_tokens, weights=(0.5, 0.5, 0, 0), smoothing_function=sf), 4),
        "bleu3": round(sentence_bleu(refs, hyp_tokens, weights=(1/3, 1/3, 1/3, 0), smoothing_function=sf), 4),
        "bleu4": round(sentence_bleu(refs, hyp_tokens, weights=(0.25, 0.25, 0.25, 0.25), smoothing_function=sf), 4),
    }


def strip_sections(raw_data: dict) -> dict:
    """
    Return a deep-copy of raw_data with SECTIONS_TO_STRIP removed from
    elements_by_title and all_paragraphs.
    """
    sanitised = copy.deepcopy(raw_data)

    # Remove from elements_by_title
    ebt = sanitised.get("elements_by_title", {})
    for sec in SECTIONS_TO_STRIP:
        ebt.pop(sec, None)

    # Remove from all_paragraphs
    if "all_paragraphs" in sanitised:
        sanitised["all_paragraphs"] = [
            p for p in sanitised["all_paragraphs"]
            if p.get("title") not in SECTIONS_TO_STRIP
        ]

    return sanitised


_CASE_FILE_CACHE = None

def find_case_file(case_entry: dict) -> str | None:
    """
    Locate the raw JSON file for a case using its case_id.
    Builds a cache of filenames in DATA_DIR to handle prefixes like 'delhiorders_2019_'.
    """
    global _CASE_FILE_CACHE
    if _CASE_FILE_CACHE is None:
        _CASE_FILE_CACHE = {}
        if os.path.exists(DATA_DIR):
            for fname in os.listdir(DATA_DIR):
                if fname.endswith(".json"):
                    # Filenames are typically court_year_id.json or id.json
                    # The ID is the last segment before .json
                    base = fname.rsplit(".", 1)[0]
                    cid = base.split("_")[-1]
                    _CASE_FILE_CACHE[cid] = os.path.join(DATA_DIR, fname)

    case_id = case_entry.get("case_id")
    if case_id and case_id in _CASE_FILE_CACHE:
        return _CASE_FILE_CACHE[case_id]

    return None


def extract_pipeline_reasoning(result: dict) -> str:
    """
    Pull the pipeline's generated explanation text.
    Uses explanation.summary_narrative (the full LLM-induced reasoning narrative).
    Falls back to joining logical_steps.
    """
    explanation = result.get("explanation", {})

    # Prefer the full narrative
    narrative = explanation.get("summary_narrative", "")
    if narrative:
        return narrative

    # Fallback: join logical steps
    steps = explanation.get("logical_steps", [])
    if steps:
        return " ".join(steps)

    # Last resort: stringify the judgment_probability reasoning dict
    jp = result.get("judgment_probability", {})
    reasoning = jp.get("reasoning", {})
    legal_logic = reasoning.get("legal_logic", [])
    if legal_logic:
        return " ".join(legal_logic)

    return ""


# ─────────────────────────────────────────────────────────────────────────────
# Main evaluation loop
# ─────────────────────────────────────────────────────────────────────────────

def run_evaluation():
    print("\n📂 Loading conclusions database...")
    with open(CONCLUSIONS_DB, "r", encoding="utf-8") as f:
        db = json.load(f)

    all_cases = db.get("conclusions", [])

    # Keep only cases that have BOTH ground-truth fields AND whose raw JSON exists
    eligible = []
    print(f"🔍 Filtering cases (need both fields + file existence)...")
    for c in all_cases:
        if c.get("conclusion") and c.get("reasoning"):
            if find_case_file(c):
                eligible.append(c)
                if MAX_CASES is not None and len(eligible) >= MAX_CASES:
                    break

    print(f"✓ Total cases in DB         : {len(all_cases)}")
    print(f"✓ Eligible cases found      : {len(eligible)}")

    results = []
    skipped = 0

    # Corpus-level accumulators
    hyp_tokens_vs_conclusion = []
    ref_tokens_vs_conclusion = []
    hyp_tokens_vs_reasoning  = []
    ref_tokens_vs_reasoning  = []

    for idx, case_entry in enumerate(eligible, 1):
        case_id = case_entry.get("case_id", f"case_{idx}")
        gt_conclusion = case_entry.get("conclusion", "")
        gt_reasoning  = case_entry.get("reasoning", "")

        print(f"\n[{idx}/{len(eligible)}] {case_id}", end=" ... ")

        # ── Find raw JSON file ───────────────────────────────────────────────
        case_file = find_case_file(case_entry)
        if not case_file:
            print("⚠️  File not found — skipped")
            skipped += 1
            continue

        # ── Sanitise: strip Conclusion + Court's Reasoning ───────────────────
        try:
            with open(case_file, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
        except Exception as e:
            print(f"✗ JSON read error: {e}")
            skipped += 1
            continue

        sanitised = strip_sections(raw_data)

        # Write to a temp file so run_pipeline (which expects a path) can load it
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".json", delete=False, encoding="utf-8"
            ) as tmp:
                json.dump(sanitised, tmp, ensure_ascii=False)
                tmp_path = tmp.name
        except Exception as e:
            print(f"✗ Temp file error: {e}")
            skipped += 1
            continue

        # ── Run pipeline ─────────────────────────────────────────────────────
        try:
            pipeline_result = run_pipeline(tmp_path)
        except Exception as e:
            print(f"✗ Pipeline error: {e}")
            traceback.print_exc()
            skipped += 1
            os.unlink(tmp_path)
            continue
        finally:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass

        # ── Extract generated reasoning ──────────────────────────────────────
        generated_text = extract_pipeline_reasoning(pipeline_result)

        if not generated_text:
            print("⚠️  Empty pipeline output — skipped")
            skipped += 1
            continue

        # ── BLEU against ground-truth conclusion ─────────────────────────────
        scores_vs_conclusion = bleu_score(generated_text, gt_conclusion)

        # ── BLEU against ground-truth court's reasoning ──────────────────────
        scores_vs_reasoning = bleu_score(generated_text, gt_reasoning)

        # Accumulate for corpus-level BLEU
        hyp_tok = tokenize(generated_text)
        hyp_tokens_vs_conclusion.append(hyp_tok)
        ref_tokens_vs_conclusion.append([tokenize(gt_conclusion)])
        hyp_tokens_vs_reasoning.append(hyp_tok)
        ref_tokens_vs_reasoning.append([tokenize(gt_reasoning)])

        record = {
            "case_id"              : case_id,
            "case_title"           : case_entry.get("case_title", ""),
            "url"                  : case_entry.get("url", ""),
            "generated_reasoning"  : generated_text,
            "gt_conclusion_length" : len(gt_conclusion),
            "gt_reasoning_length"  : len(gt_reasoning),
            "bleu_vs_conclusion"   : scores_vs_conclusion,
            "bleu_vs_reasoning"    : scores_vs_reasoning,
        }
        results.append(record)

        avg_c = scores_vs_conclusion["bleu4"]
        avg_r = scores_vs_reasoning["bleu4"]
        print(f"✓  BLEU-4 vs Conclusion: {avg_c:.4f} | vs Reasoning: {avg_r:.4f}")

    # ── Corpus-level BLEU ────────────────────────────────────────────────────
    sf = SmoothingFunction().method1
    corpus_bleu_conclusion = 0.0
    corpus_bleu_reasoning  = 0.0

    if hyp_tokens_vs_conclusion:
        corpus_bleu_conclusion = round(
            corpus_bleu(ref_tokens_vs_conclusion, hyp_tokens_vs_conclusion,
                        smoothing_function=sf), 4
        )
    if hyp_tokens_vs_reasoning:
        corpus_bleu_reasoning = round(
            corpus_bleu(ref_tokens_vs_reasoning, hyp_tokens_vs_reasoning,
                        smoothing_function=sf), 4
        )

    # ── Compute per-field averages ────────────────────────────────────────────
    def avg(key, subkey):
        vals = [r["bleu_vs_" + key][subkey] for r in results]
        return round(sum(vals) / len(vals), 4) if vals else 0.0

    summary = {
        "total_evaluated"                     : len(results),
        "total_skipped"                       : skipped,
        "corpus_bleu4_vs_conclusion"          : corpus_bleu_conclusion,
        "corpus_bleu4_vs_reasoning"           : corpus_bleu_reasoning,
        "avg_sentence_bleu1_vs_conclusion"    : avg("conclusion", "bleu1"),
        "avg_sentence_bleu2_vs_conclusion"    : avg("conclusion", "bleu2"),
        "avg_sentence_bleu3_vs_conclusion"    : avg("conclusion", "bleu3"),
        "avg_sentence_bleu4_vs_conclusion"    : avg("conclusion", "bleu4"),
        "avg_sentence_bleu1_vs_reasoning"     : avg("reasoning",  "bleu1"),
        "avg_sentence_bleu2_vs_reasoning"     : avg("reasoning",  "bleu2"),
        "avg_sentence_bleu3_vs_reasoning"     : avg("reasoning",  "bleu3"),
        "avg_sentence_bleu4_vs_reasoning"     : avg("reasoning",  "bleu4"),
    }

    # ── Save full results JSON ────────────────────────────────────────────────
    output_blob = {
        "summary" : summary,
        "results" : results,
    }
    with open(RESULTS_JSON, "w", encoding="utf-8") as f:
        json.dump(output_blob, f, indent=2, ensure_ascii=False)

    # ── Save CSV summary ──────────────────────────────────────────────────────
    csv_fields = [
        "case_id", "case_title",
        "bleu1_vs_conclusion", "bleu2_vs_conclusion",
        "bleu3_vs_conclusion", "bleu4_vs_conclusion",
        "bleu1_vs_reasoning",  "bleu2_vs_reasoning",
        "bleu3_vs_reasoning",  "bleu4_vs_reasoning",
    ]
    with open(SUMMARY_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=csv_fields)
        writer.writeheader()
        for r in results:
            writer.writerow({
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

    # ── Print summary ─────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("📊 BLEU EVALUATION SUMMARY")
    print("=" * 70)
    print(f"  Cases evaluated            : {summary['total_evaluated']}")
    print(f"  Cases skipped              : {summary['total_skipped']}")
    print(f"\n  ── vs Ground-Truth CONCLUSION ──")
    print(f"  Corpus BLEU-4              : {summary['corpus_bleu4_vs_conclusion']}")
    print(f"  Avg Sentence BLEU-1        : {summary['avg_sentence_bleu1_vs_conclusion']}")
    print(f"  Avg Sentence BLEU-2        : {summary['avg_sentence_bleu2_vs_conclusion']}")
    print(f"  Avg Sentence BLEU-3        : {summary['avg_sentence_bleu3_vs_conclusion']}")
    print(f"  Avg Sentence BLEU-4        : {summary['avg_sentence_bleu4_vs_conclusion']}")
    print(f"\n  ── vs Ground-Truth COURT'S REASONING ──")
    print(f"  Corpus BLEU-4              : {summary['corpus_bleu4_vs_reasoning']}")
    print(f"  Avg Sentence BLEU-1        : {summary['avg_sentence_bleu1_vs_reasoning']}")
    print(f"  Avg Sentence BLEU-2        : {summary['avg_sentence_bleu2_vs_reasoning']}")
    print(f"  Avg Sentence BLEU-3        : {summary['avg_sentence_bleu3_vs_reasoning']}")
    print(f"  Avg Sentence BLEU-4        : {summary['avg_sentence_bleu4_vs_reasoning']}")
    print("=" * 70)
    print(f"\n💾  Full results → {RESULTS_JSON}")
    print(f"📋  Per-case CSV  → {SUMMARY_CSV}\n")


if __name__ == "__main__":
    run_evaluation()
