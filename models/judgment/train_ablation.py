import pandas as pd
import numpy as np
import os
import json
import joblib
from xgboost import XGBClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATASET_PATH = os.path.join(BASE_DIR, "data", "dataset", "final_phi_features.csv")
X_PATH = os.path.join(BASE_DIR, "data", "dataset", "X_features.csv")
Y_PATH = os.path.join(BASE_DIR, "data", "dataset", "y_labels.csv")
PLOTS_DIR = os.path.join(BASE_DIR, "outputs", "plots")
ABLATION_METRICS_PATH = os.path.join(BASE_DIR, "outputs", "ablation_results.json")
MODEL_PATH = os.path.join(BASE_DIR, "data", "processed", "judgment_model.joblib")

# ── Φ-Vector Feature Block Definitions ──
# These correspond exactly to the 4 intelligence blocks in the Phi representation.

CONTEXT_FEATURES = [
    "is_criminal", "is_service", "is_property", "is_matrimonial",
    "num_claims", "num_issues", "num_parties", "num_actions",
]

EVIDENCE_FEATURES_PREFIX = ["ev_", "fg_", "evidence_density", "evidence_match_count"]

GAP_FEATURES = [
    "missing_count", "gap_importance_sum", "gap_confidence_max", "gap_confidence_mean",
]

CONFLICT_FEATURES = [
    "conflict_count", "conflict_score",
]

RAG_FEATURES = [
    "rag_allowed_ratio", "rag_dismissed_ratio", "rag_partial_ratio",
    "rag_unknown_ratio", "rag_weighted_outcome",
    "rag_similarity_mean", "rag_similarity_min",
]


def _match_columns(all_cols, prefixes_or_names):
    """Match column names by exact match or prefix."""
    matched = []
    for col in all_cols:
        for pattern in prefixes_or_names:
            if col == pattern or col.startswith(pattern):
                matched.append(col)
                break
    return matched


def _load_dataset():
    if os.path.exists(DATASET_PATH):
        df = pd.read_csv(DATASET_PATH)
        if "label" not in df.columns:
            raise ValueError(f"'label' column missing in {DATASET_PATH}")
        drop_cols = [c for c in ["case_id", "true_outcome", "label"] if c in df.columns]
        X = df.drop(columns=drop_cols)
        y = df["label"].values
        return X, y

    if os.path.exists(X_PATH) and os.path.exists(Y_PATH):
        X = pd.read_csv(X_PATH)
        y = pd.read_csv(Y_PATH).values.ravel()
        return X, y

    raise FileNotFoundError(
        f"No dataset found. Run:\n"
        f"  1) python batch_process.py\n"
        f"  2) python scripts/prepare_dataset.py\n"
    )


def run_ablation_study():
    """
    Research-Grade Ablation Study:
    Tests the incremental "Lift" of each Φ-Vector block.

    Ablation Steps:
      A: Φ_Context only           (case type, parties, claims, issues)
      B: A + Φ_Evidence           (+ 6 coarse + N fine-grained evidence features)
      C: B + Φ_Gap                (+ missing evidence gap signals)
      D: C + Φ_Conflict           (+ contradiction score/count)
      E: Full Pipeline (Φ_all)    (+ RAG retrieval statistics)

    Each step is evaluated with 5-fold stratified CV, reporting:
      - Accuracy, F1, AUC-ROC
      - Incremental lift over previous step
    """
    X, y = _load_dataset()
    all_cols = list(X.columns)

    # Build cumulative feature blocks
    ctx_cols = _match_columns(all_cols, CONTEXT_FEATURES)
    ev_cols = _match_columns(all_cols, EVIDENCE_FEATURES_PREFIX)
    gap_cols = _match_columns(all_cols, GAP_FEATURES)
    conflict_cols = _match_columns(all_cols, CONFLICT_FEATURES)
    rag_cols = _match_columns(all_cols, RAG_FEATURES)

    ablation_steps = {
        "A: Φ_Context": ctx_cols,
        "B: + Φ_Evidence": ctx_cols + ev_cols,
        "C: + Φ_Gap": ctx_cols + ev_cols + gap_cols,
        "D: + Φ_Conflict": ctx_cols + ev_cols + gap_cols + conflict_cols,
        "E: Full Φ Pipeline": all_cols,
    }

    print("=" * 70)
    print("🧪 ABLATION STUDY: Incremental Feature Block Impact")
    print("=" * 70)
    print(f"Dataset: {len(y)} samples | Features: {len(all_cols)}")
    print(f"Class balance: {int(y.sum())} positive / {int(len(y) - y.sum())} negative")
    print()

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    results = []

    for step_name, feature_cols in ablation_steps.items():
        # Ensure columns exist
        valid_cols = [c for c in feature_cols if c in X.columns]
        if not valid_cols:
            print(f"  ⚠️ {step_name}: No valid features found, skipping.")
            continue

        X_sub = X[valid_cols]
        fold_accs, fold_f1s, fold_aucs = [], [], []

        for train_idx, val_idx in skf.split(X_sub, y):
            X_tr, X_val = X_sub.iloc[train_idx], X_sub.iloc[val_idx]
            y_tr, y_val = y[train_idx], y[val_idx]

            model = XGBClassifier(
                n_estimators=250, learning_rate=0.05, max_depth=6,
                subsample=0.9, colsample_bytree=0.9,
                eval_metric="logloss", random_state=42, verbosity=0,
            )
            model.fit(X_tr, y_tr)
            y_pred = model.predict(X_val)
            y_proba = model.predict_proba(X_val)[:, 1]

            fold_accs.append(accuracy_score(y_val, y_pred))
            fold_f1s.append(f1_score(y_val, y_pred, zero_division=0))
            try:
                fold_aucs.append(roc_auc_score(y_val, y_proba))
            except ValueError:
                fold_aucs.append(0.0)

        mean_acc = np.mean(fold_accs)
        mean_f1 = np.mean(fold_f1s)
        mean_auc = np.mean(fold_aucs)

        # Calculate lift from previous step
        if results:
            prev = results[-1]
            lift_acc = mean_acc - prev["accuracy"]
            lift_f1 = mean_f1 - prev["f1"]
            lift_str = f"  Δ Acc={lift_acc:+.4f}  Δ F1={lift_f1:+.4f}"
        else:
            lift_str = "  (baseline)"

        results.append({
            "step": step_name,
            "features_used": len(valid_cols),
            "accuracy": float(mean_acc),
            "accuracy_std": float(np.std(fold_accs)),
            "f1": float(mean_f1),
            "f1_std": float(np.std(fold_f1s)),
            "auc": float(mean_auc),
            "auc_std": float(np.std(fold_aucs)),
        })

        print(f"  ✅ {step_name:30s} | Acc={mean_acc:.4f} ± {np.std(fold_accs):.4f} | "
              f"F1={mean_f1:.4f} ± {np.std(fold_f1s):.4f} | "
              f"AUC={mean_auc:.4f}{lift_str}")

    # ── Save Ablation Results JSON ──
    os.makedirs(os.path.dirname(ABLATION_METRICS_PATH), exist_ok=True)
    with open(ABLATION_METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\n💾 Ablation results saved to: {ABLATION_METRICS_PATH}")

    # ── Ablation Bar Chart ──
    os.makedirs(PLOTS_DIR, exist_ok=True)
    df_results = pd.DataFrame(results)

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    sns.set_theme(style="whitegrid", palette="magma")

    for ax, metric, label in zip(
        axes,
        ["accuracy", "f1", "auc"],
        ["Accuracy", "F1 Score", "AUC-ROC"],
    ):
        bars = ax.bar(
            range(len(df_results)),
            df_results[metric],
            yerr=df_results[f"{metric}_std"],
            capsize=4,
            color=sns.color_palette("magma", len(df_results)),
            edgecolor="black",
            linewidth=0.5,
        )
        ax.set_xticks(range(len(df_results)))
        ax.set_xticklabels(
            [r["step"].split(":")[0] for r in results],
            rotation=0, fontsize=10,
        )
        ax.set_ylabel(label)
        ax.set_title(f"{label} by Feature Block")
        ax.set_ylim(0, 1.05)

        for bar, val in zip(bars, df_results[metric]):
            ax.annotate(
                f"{val:.3f}",
                xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                ha="center", va="bottom", fontsize=9,
            )

    plt.suptitle("🏆 Ablation Study: Impact of Reasoning Modules on Prediction", fontsize=14, y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "ablation_study.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"📊 Ablation chart saved to: {os.path.join(PLOTS_DIR, 'ablation_study.png')}")

    # ── Train & Save Full Model ──
    print("\n🚀 Training final full-pipeline model for inference...")
    full_model = XGBClassifier(
        n_estimators=250, learning_rate=0.05, max_depth=6,
        subsample=0.9, colsample_bytree=0.9,
        eval_metric="logloss", random_state=42, verbosity=0,
    )
    full_model.fit(X, y)
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump({"model": full_model, "features": all_cols}, MODEL_PATH)
    print(f"💾 Full inference model saved to: {MODEL_PATH}")

    return results


if __name__ == "__main__":
    run_ablation_study()
