"""
evaluation/_common.py
──────────────────────────────────────────────────────────────────────────────
Shared utilities for every evaluation metric module.

All metric scripts import from here to avoid code duplication:
  - Project-root path setup
  - Loading / filtering the conclusions DB
  - Finding case raw JSON files
  - Stripping ground-truth sections before running the pipeline
  - Running the main_pipeline and extracting the generated reasoning text
"""

import copy
import json
import os
import sys
import tempfile
import traceback
from pathlib import Path

# ── Make project root importable ─────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# ─────────────────────────────────────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────────────────────────────────────
CONCLUSIONS_DB = str(PROJECT_ROOT / "data" / "conclusions_data.json")
DATA_DIR       = str(PROJECT_ROOT / "data")
OUTPUT_DIR     = str(PROJECT_ROOT / "outputs")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Sections removed from raw JSON before sending to the pipeline so the model
# cannot "see" the ground-truth answer.
SECTIONS_TO_STRIP = {
    "Conclusion", "Court's Reasoning", "Judgment", "Judgement",
    "Final Order", "Analysis of the law", "Analysis",
}

# ─────────────────────────────────────────────────────────────────────────────
# Case-file cache
# ─────────────────────────────────────────────────────────────────────────────
_CASE_FILE_CACHE: dict | None = None


def _build_cache() -> dict:
    """Build {case_id -> absolute_path} for every *.json in DATA_DIR."""
    cache: dict = {}
    if os.path.exists(DATA_DIR):
        for fname in os.listdir(DATA_DIR):
            if fname.endswith(".json"):
                base = fname.rsplit(".", 1)[0]
                cid  = base.split("_")[-1]
                cache[cid] = os.path.join(DATA_DIR, fname)
    return cache


def find_case_file(case_entry: dict) -> str | None:
    """Return the absolute path to the raw JSON file for *case_entry*."""
    global _CASE_FILE_CACHE
    if _CASE_FILE_CACHE is None:
        _CASE_FILE_CACHE = _build_cache()
    case_id = case_entry.get("case_id")
    return _CASE_FILE_CACHE.get(case_id) if case_id else None


# ─────────────────────────────────────────────────────────────────────────────
# Data loading helpers
# ─────────────────────────────────────────────────────────────────────────────

def load_eligible_cases(max_cases: int | None = 200) -> list[dict]:
    """
    Load conclusions DB and return cases that have:
      • a ground-truth ``conclusion``
      • a ground-truth ``reasoning``
      • a resolvable raw JSON file in DATA_DIR

    Parameters
    ----------
    max_cases : int | None
        Cap the list at this many items.  Pass ``None`` for all cases.
    """
    with open(CONCLUSIONS_DB, "r", encoding="utf-8") as f:
        db = json.load(f)

    eligible: list[dict] = []
    for c in db.get("conclusions", []):
        if c.get("conclusion") and c.get("reasoning") and find_case_file(c):
            eligible.append(c)
            if max_cases is not None and len(eligible) >= max_cases:
                break
    return eligible


# ─────────────────────────────────────────────────────────────────────────────
# Section stripping
# ─────────────────────────────────────────────────────────────────────────────

def strip_sections(raw_data: dict) -> dict:
    """
    Return a deep-copy of *raw_data* with SECTIONS_TO_STRIP removed from
    ``elements_by_title`` and ``all_paragraphs`` so the pipeline cannot cheat.
    """
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


# ─────────────────────────────────────────────────────────────────────────────
# Pipeline runner
# ─────────────────────────────────────────────────────────────────────────────

def run_pipeline_on_case(case_file: str) -> dict | None:
    """
    Strip ground-truth sections, write to a temp file, and run main_pipeline.

    Returns the pipeline result dict, or ``None`` on any error.
    Prints a short status line to stdout.
    """
    from main_pipeline import run_pipeline  # lazy import — avoids loading models at import time

    try:
        with open(case_file, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
    except Exception as e:
        print(f"  ✗ JSON read error: {e}")
        return None

    sanitised = strip_sections(raw_data)

    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as tmp:
            json.dump(sanitised, tmp, ensure_ascii=False)
            tmp_path = tmp.name
    except Exception as e:
        print(f"  ✗ Temp file error: {e}")
        return None

    try:
        result = run_pipeline(tmp_path)
    except Exception as e:
        print(f"  ✗ Pipeline error: {e}")
        traceback.print_exc()
        result = None
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass

    return result


# ─────────────────────────────────────────────────────────────────────────────
# Reasoning extraction
# ─────────────────────────────────────────────────────────────────────────────

def extract_pipeline_reasoning(result: dict) -> str:
    """
    Pull the pipeline's generated explanation text in order of preference:
      1. explanation.summary_narrative  (full LLM-induced reasoning)
      2. explanation.logical_steps      (joined)
      3. judgment_probability.reasoning.legal_logic (joined)
    """
    explanation = result.get("explanation", {})

    narrative = explanation.get("summary_narrative", "")
    if narrative:
        return narrative

    steps = explanation.get("logical_steps", [])
    if steps:
        return " ".join(steps)

    jp = result.get("judgment_probability", {})
    legal_logic = jp.get("reasoning", {}).get("legal_logic", [])
    if legal_logic:
        return " ".join(legal_logic)

    return ""
