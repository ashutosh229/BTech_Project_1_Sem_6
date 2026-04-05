import json
import os

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.feature_selection import mutual_info_classif
from sklearn.linear_model import LogisticRegression

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")

MATRIX_FILE = os.path.join(PROCESSED_DIR, "real_evidence_matrix.csv")
WEAK_INDEX = os.path.join(PROCESSED_DIR, "failed_cases_index.json")
WEAK_SCORES = os.path.join(PROCESSED_DIR, "weak_case_scores.json")
MODEL_FILE = os.path.join(PROCESSED_DIR, "outcome_predictor.joblib")


def _safe_normalize(values):
    arr = np.asarray(values, dtype=float)
    if arr.max() <= arr.min():
        return np.zeros_like(arr)
    return (arr - arr.min()) / (arr.max() - arr.min())


def rank_causal_importance():
    if not os.path.exists(MATRIX_FILE):
        print(f"❌ Matrix file {MATRIX_FILE} not found.")
        return

    df = pd.read_csv(MATRIX_FILE)
    if not os.path.exists(WEAK_INDEX):
        print(f"❌ Weak case index {WEAK_INDEX} not found.")
        return

    weak_scores = None
    if os.path.exists(WEAK_SCORES):
        with open(WEAK_SCORES, "r", encoding="utf-8") as f:
            weak_scores = json.load(f)
        df["weak_probability"] = df["case_id"].map(
            lambda cid: float(weak_scores.get(cid, {}).get("weak_probability", 0.0))
        )
        df["is_success"] = (df["weak_probability"] < 0.5).astype(int)
        sample_weight = (df["weak_probability"] - 0.5).abs() * 2.0
        sample_weight = sample_weight.clip(lower=0.20)
    else:
        with open(WEAK_INDEX, "r", encoding="utf-8") as f:
            weak_data = json.load(f)
        failed_ids = [c["case_id"] for c in weak_data]
        df["is_success"] = (~df["case_id"].isin(failed_ids)).astype(int)
        df["weak_probability"] = 1.0 - df["is_success"]
        sample_weight = np.ones(len(df))

    feature_cols = [
        c
        for c in df.columns
        if (c.startswith("ev_") and c != "ev_total_matches")
        or c.startswith("fg_")
        or c.startswith("fgcnt_")
    ]
    x = df[feature_cols].fillna(0.0)
    y = df["is_success"].astype(int)

    gb = GradientBoostingClassifier(n_estimators=250, learning_rate=0.05, max_depth=3, random_state=42)
    gb.fit(x, y, sample_weight=sample_weight)

    rf = RandomForestClassifier(
        n_estimators=250,
        max_depth=10,
        min_samples_leaf=5,
        class_weight="balanced_subsample",
        n_jobs=-1,
        random_state=42,
    )
    rf.fit(x, y, sample_weight=sample_weight)

    lr = LogisticRegression(max_iter=2000, class_weight="balanced")
    lr.fit(x, y, sample_weight=sample_weight)

    mi = mutual_info_classif(x, y, discrete_features=[c.startswith("ev_") or c.startswith("fg_") for c in feature_cols], random_state=42)

    success_mask = y == 1
    weak_mask = y == 0
    success_means = x[success_mask].mean(axis=0)
    weak_means = x[weak_mask].mean(axis=0)
    mean_uplift = success_means - weak_means

    # Binary support uplift for features that have count columns.
    prevalence_uplift = []
    for col in feature_cols:
        if col.startswith("fgcnt_"):
            binary = (x[col] > 0).astype(int)
        else:
            binary = (x[col] > 0).astype(int)
        prevalence_uplift.append(binary[success_mask].mean() - binary[weak_mask].mean())
    prevalence_uplift = np.asarray(prevalence_uplift)

    gb_norm = _safe_normalize(gb.feature_importances_)
    rf_norm = _safe_normalize(rf.feature_importances_)
    mi_norm = _safe_normalize(mi)
    coef_norm = _safe_normalize(np.maximum(lr.coef_[0], 0.0))
    uplift_norm = _safe_normalize(np.maximum(mean_uplift, 0.0))
    prevalence_norm = _safe_normalize(np.maximum(prevalence_uplift, 0.0))

    global_score = (
        0.25 * gb_norm
        + 0.20 * rf_norm
        + 0.15 * mi_norm
        + 0.15 * coef_norm
        + 0.15 * uplift_norm
        + 0.10 * prevalence_norm
    )

    cluster_names = {
        "ev_medical": "Medical/FSL Reports",
        "ev_witness": "Witness Testimony (PW)",
        "ev_contract": "Agreements & Contracts",
        "ev_procedural": "Other Procedural Docs",
        "ev_memo": "FIR/Seizure/PM Reports",
        "ev_deeds": "Property Deeds",
    }
    for col in feature_cols:
        if col not in cluster_names:
            pretty = col.replace("fgcnt_", "").replace("fg_", "").replace("_", " ").title()
            cluster_names[col] = pretty

    results = []
    for i, col in enumerate(feature_cols):
        results.append(
            {
                "feature_key": col,
                "Evidence Cluster": cluster_names.get(col, col),
                "Importance Score (%)": round(float(global_score[i]) * 100, 2),
                "Impact Mode": "Positive" if lr.coef_[0][i] > 0 else "Negative/Contested",
                "GB Importance": round(float(gb_norm[i]), 6),
                "RF Importance": round(float(rf_norm[i]), 6),
                "Mutual Information": round(float(mi_norm[i]), 6),
                "Positive Coefficient": round(float(max(lr.coef_[0][i], 0.0)), 6),
                "Mean Uplift": round(float(mean_uplift[i]), 6),
                "Prevalence Uplift": round(float(prevalence_uplift[i]), 6),
            }
        )

    results = sorted(results, key=lambda row: row["Importance Score (%)"], reverse=True)

    print("\n" + "=" * 80)
    print("🏆 ENSEMBLE EVIDENCE IMPORTANCE RANKING")
    print("=" * 80)
    print(f"{'Evidence':<35} | {'Score':<8} | {'Mean Uplift':<12} | {'Prev Uplift'}")
    print("-" * 80)
    for row in results[:25]:
        print(
            f"{row['Evidence Cluster']:<35} | {row['Importance Score (%)']:<8}% | "
            f"{row['Mean Uplift']:<12} | {row['Prevalence Uplift']}"
        )

    model_data = {
        "gradient_boosting": gb,
        "random_forest": rf,
        "logistic_regression": lr,
        "feature_names": feature_cols,
        "cluster_mapping": cluster_names,
        "global_rankings": results,
        "global_scores_raw": global_score.tolist(),
    }
    joblib.dump(model_data, MODEL_FILE)

    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    with open(os.path.join(OUTPUTS_DIR, "causal_ranking.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\n✅ Ensemble importance model saved to: {MODEL_FILE}")
    print(f"✅ Final ranking saved to: {os.path.join(OUTPUTS_DIR, 'causal_ranking.json')}")


if __name__ == "__main__":
    rank_causal_importance()
