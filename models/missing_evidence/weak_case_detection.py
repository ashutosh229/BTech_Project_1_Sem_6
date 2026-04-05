import json
import os
import re
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")

WEAK_INDEX_PATH = os.path.join(PROCESSED_DIR, "failed_cases_index.json")
WEAK_SCORES_PATH = os.path.join(PROCESSED_DIR, "weak_case_scores.json")
WEAK_SCORES_CSV_PATH = os.path.join(PROCESSED_DIR, "weak_case_scores.csv")
WEAK_MODEL_PATH = os.path.join(PROCESSED_DIR, "weak_case_model.joblib")

WEAKNESS_MARKERS = [
    r"benefit\s?of\s?doubt",
    r"lack\sof\sevidence",
    r"insufficient\sevidence",
    r"failed\sto\sprove",
    r"not\sproven\sbeyond\sreasonable\sdoubt",
    r"absence\sof\smaterial\sevidence",
    r"prosecution\sfailed\sto\scorroborate",
    r"no\scorroborative\sevidence",
    r"failure\sto\sproduce\smaterial\switness",
    r"gap\sin\sthe\schain\sof\sevidence",
    r"no\sevidence\sof",
    r"not\ssupported\sby\sany\sdocumentary\sevidence",
    r"no\tdocumentary\tevidence",
    r"unable\sto\stestablish",
    r"has\snot\sbeen\sproved",
    r"evidence\sfalls\sshort",
    r"material\somissions?\s+in\s+evidence",
]

SUCCESS_MARKERS = [
    r"proved\sbeyond\sreasonable\sdoubt",
    r"stands\sproved",
    r"case\sof\sthe\sprosecution\sproved",
    r"petition\sis\sallowed",
    r"appeal\sis\sallowed",
    r"suit\sis\sdecreed",
    r"conviction\sis\supheld",
    r"successfully\sestablished",
    r"duly\sproved",
    r"clearly\sestablished",
]


def _collect_case_texts(data_dir):
    rows = []
    for json_path in Path(data_dir).glob("*.json"):
        if json_path.name.startswith("_"):
            continue
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            continue

        elements = data.get("elements_by_title", {})
        fact_text = " ".join(item.get("text", "") for item in elements.get("Fact", []))
        reasoning_text = " ".join(item.get("text", "") for item in elements.get("Court's Reasoning", []))
        conclusion_text = " ".join(item.get("text", "") for item in elements.get("Conclusion", []))
        analysis_text = " ".join(item.get("text", "") for item in elements.get("Analysis of the law", []))
        merged_text = " ".join([fact_text, reasoning_text, conclusion_text, analysis_text]).lower()

        weak_matches = [m for m in WEAKNESS_MARKERS if re.search(m, merged_text)]
        success_matches = [m for m in SUCCESS_MARKERS if re.search(m, merged_text)]

        rows.append(
            {
                "case_id": json_path.stem,
                "court": data.get("court_name", ""),
                "year": json_path.stem.split("_")[1] if "_" in json_path.stem else "",
                "text": merged_text,
                "weak_seed": int(bool(weak_matches)),
                "success_seed": int(bool(success_matches)),
                "weak_matches": weak_matches,
                "success_matches": success_matches,
                "seed_strength": len(weak_matches) - 0.5 * len(success_matches),
            }
        )
    return pd.DataFrame(rows)


def _build_text_features(texts):
    doc_count = len(texts)
    word_min_df = 3 if doc_count >= 50 else 1
    char_min_df = 5 if doc_count >= 100 else 1
    word_vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=word_min_df,
        max_features=16000,
        stop_words="english",
        sublinear_tf=True,
    )
    char_vectorizer = TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=(3, 5),
        min_df=char_min_df,
        max_features=12000,
        sublinear_tf=True,
    )
    x_word = word_vectorizer.fit_transform(texts)
    x_char = char_vectorizer.fit_transform(texts)
    return word_vectorizer, char_vectorizer, sparse.hstack([x_word, x_char], format="csr")


def _fit_weak_ensemble(x, y_seed):
    word_char_model = LogisticRegression(max_iter=3000, class_weight="balanced", C=2.0)
    word_char_model.fit(x, y_seed)
    base_prob = word_char_model.predict_proba(x)[:, 1]

    # Pseudo-label expansion: use only high-confidence regions to refine.
    confident = (base_prob >= 0.85) | (base_prob <= 0.15)
    pseudo_y = (base_prob >= 0.5).astype(int)
    if confident.sum() < 2 or len(set(pseudo_y[confident])) < 2:
        return word_char_model, word_char_model, base_prob, base_prob
    refined_model = LogisticRegression(max_iter=3000, class_weight="balanced", C=1.0)
    refined_model.fit(x[confident], pseudo_y[confident])
    refined_prob = refined_model.predict_proba(x)[:, 1]

    return word_char_model, refined_model, base_prob, refined_prob


def build_probabilistic_weak_case_index(
    data_dir=DATA_DIR,
    weak_index_path=WEAK_INDEX_PATH,
    weak_scores_path=WEAK_SCORES_PATH,
    weak_scores_csv_path=WEAK_SCORES_CSV_PATH,
    weak_model_path=WEAK_MODEL_PATH,
):
    df = _collect_case_texts(data_dir)
    if df.empty:
        print("⚠️ No cases found for weak-case scoring.")
        return None

    # Weak supervision seeds.
    df["seed_label"] = ((df["weak_seed"] == 1) & (df["success_seed"] == 0)).astype(int)
    df["anti_seed"] = ((df["success_seed"] == 1) & (df["weak_seed"] == 0)).astype(int)

    word_vectorizer, char_vectorizer, x = _build_text_features(df["text"])
    base_model, refined_model, base_prob, refined_prob = _fit_weak_ensemble(x, df["seed_label"].to_numpy())

    seed_boost = df["weak_seed"] * 0.18 - df["success_seed"] * 0.12
    lexical_conflict_penalty = (df["weak_seed"] & df["success_seed"]).astype(float) * 0.08

    # Final probability is a blended ensemble, not a regex bucket.
    calibrated = 0.40 * base_prob + 0.45 * refined_prob + 0.15 * df["seed_label"].to_numpy()
    calibrated = np.clip(calibrated + seed_boost - lexical_conflict_penalty, 0.0, 1.0)

    df["weak_probability"] = calibrated
    df["hard_weak"] = ((df["seed_label"] == 1) | (df["weak_probability"] >= 0.62)).astype(int)

    os.makedirs(PROCESSED_DIR, exist_ok=True)

    weak_list = []
    scores_payload = {}
    for _, row in df.iterrows():
        payload = {
            "case_id": row["case_id"],
            "court": row["court"],
            "year": row["year"],
            "weak_probability": round(float(row["weak_probability"]), 6),
            "hard_weak": int(row["hard_weak"]),
            "seed_label": int(row["seed_label"]),
            "anti_seed": int(row["anti_seed"]),
            "weak_matches": row["weak_matches"],
            "success_matches": row["success_matches"],
        }
        scores_payload[row["case_id"]] = payload
        if row["hard_weak"] == 1:
            weak_list.append(
                {
                    "case_id": row["case_id"],
                    "court": row["court"],
                    "year": row["year"],
                    "markers_found": row["weak_matches"],
                    "weak_probability": round(float(row["weak_probability"]), 6),
                }
            )

    with open(weak_scores_path, "w", encoding="utf-8") as f:
        json.dump(scores_payload, f, indent=2)
    with open(weak_index_path, "w", encoding="utf-8") as f:
        json.dump(weak_list, f, indent=2)

    df.drop(columns=["text"]).to_csv(weak_scores_csv_path, index=False)
    joblib.dump(
        {
            "word_vectorizer": word_vectorizer,
            "char_vectorizer": char_vectorizer,
            "base_model": base_model,
            "refined_model": refined_model,
        },
        weak_model_path,
    )

    print(f"✅ Weak-case probability index created for {len(df)} cases.")
    print(f"📈 Hard weak cases: {len(weak_list)}")
    print(f"💾 Saved: {weak_scores_path}")
    return df


def find_weak_cases(data_dir, output_file):
    df = build_probabilistic_weak_case_index(data_dir=data_dir, weak_index_path=output_file)
    return df


if __name__ == "__main__":
    find_weak_cases(DATA_DIR, WEAK_INDEX_PATH)
