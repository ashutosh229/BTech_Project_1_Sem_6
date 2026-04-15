import pandas as pd
import numpy as np
import os
import json
import joblib
from xgboost import XGBClassifier
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATASET_PATH = os.path.join(BASE_DIR, "data", "dataset", "final_phi_features.csv")
X_PATH = os.path.join(BASE_DIR, "data", "dataset", "X_features.csv")
Y_PATH = os.path.join(BASE_DIR, "data", "dataset", "y_labels.csv")
MODEL_PATH = os.path.join(BASE_DIR, "data", "processed", "judgment_model.joblib")
PLOTS_DIR = os.path.join(BASE_DIR, "outputs", "plots")
METRICS_PATH = os.path.join(BASE_DIR, "outputs", "training_metrics.json")


def _load_dataset():
    """Load from canonical Phi dataset or fallback to X/y split files."""
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


def train_system_model():
    """
    Research-grade training loop with:
    - Stratified 80/20 hold-out split
    - 5-fold cross-validation on training set
    - Full metric suite (Accuracy, F1, Precision, Recall, AUC)
    - Confusion matrix visualization
    - Feature importance plot
    - Saved metrics JSON for paper reporting
    """
    X, y = _load_dataset()
    print(f"📊 Dataset loaded: {len(y)} samples, {int(y.sum())} positive, {len(y) - int(y.sum())} negative")
    print(f"📐 Feature dimensionality: {X.shape[1]} features")

    # ── 1. Stratified Hold-Out Split ──
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"\n🔀 Split: {len(y_train)} train / {len(y_test)} test")

    # ── 2. Cross-Validation on Training Set ──
    print("\n🔄 Running 5-Fold Stratified Cross-Validation...")
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = {"accuracy": [], "f1": [], "precision": [], "recall": [], "auc": []}

    for fold, (train_idx, val_idx) in enumerate(skf.split(X_train, y_train), 1):
        X_fold_train = X_train.iloc[train_idx]
        y_fold_train = y_train[train_idx]
        X_fold_val = X_train.iloc[val_idx]
        y_fold_val = y_train[val_idx]

        fold_model = XGBClassifier(
            n_estimators=250, learning_rate=0.05, max_depth=6,
            subsample=0.9, colsample_bytree=0.9,
            eval_metric="logloss", random_state=42, verbosity=0,
        )
        fold_model.fit(X_fold_train, y_fold_train)
        y_fold_pred = fold_model.predict(X_fold_val)
        y_fold_proba = fold_model.predict_proba(X_fold_val)[:, 1]

        cv_scores["accuracy"].append(accuracy_score(y_fold_val, y_fold_pred))
        cv_scores["f1"].append(f1_score(y_fold_val, y_fold_pred, zero_division=0))
        cv_scores["precision"].append(precision_score(y_fold_val, y_fold_pred, zero_division=0))
        cv_scores["recall"].append(recall_score(y_fold_val, y_fold_pred, zero_division=0))
        try:
            cv_scores["auc"].append(roc_auc_score(y_fold_val, y_fold_proba))
        except ValueError:
            cv_scores["auc"].append(0.0)

        print(f"  Fold {fold}: Acc={cv_scores['accuracy'][-1]:.4f}  F1={cv_scores['f1'][-1]:.4f}  AUC={cv_scores['auc'][-1]:.4f}")

    print("\n📈 Cross-Validation Summary:")
    for metric, values in cv_scores.items():
        print(f"  {metric.upper():>10}: {np.mean(values):.4f} ± {np.std(values):.4f}")

    # ── 3. Train Final Model on Full Training Set ──
    print("\n🚀 Training final model on full training set...")
    model = XGBClassifier(
        n_estimators=250, learning_rate=0.05, max_depth=6,
        subsample=0.9, colsample_bytree=0.9,
        eval_metric="logloss", random_state=42, verbosity=0,
    )
    model.fit(X_train, y_train)

    # ── 4. Evaluate on Hold-Out Test Set ──
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    test_acc = accuracy_score(y_test, y_pred)
    test_f1 = f1_score(y_test, y_pred, zero_division=0)
    test_precision = precision_score(y_test, y_pred, zero_division=0)
    test_recall = recall_score(y_test, y_pred, zero_division=0)
    try:
        test_auc = roc_auc_score(y_test, y_proba)
    except ValueError:
        test_auc = 0.0

    print("\n" + "=" * 60)
    print("🏆 HOLD-OUT TEST SET RESULTS")
    print("=" * 60)
    print(f"  Accuracy:  {test_acc:.4f}")
    print(f"  F1 Score:  {test_f1:.4f}")
    print(f"  Precision: {test_precision:.4f}")
    print(f"  Recall:    {test_recall:.4f}")
    print(f"  AUC-ROC:   {test_auc:.4f}")
    print("\n📝 Classification Report:")
    print(classification_report(y_test, y_pred, target_names=["Dismissed/Weak", "Allowed/Success"]))

    # ── 5. Save Metrics JSON ──
    os.makedirs(os.path.dirname(METRICS_PATH), exist_ok=True)
    metrics = {
        "dataset_size": int(len(y)),
        "train_size": int(len(y_train)),
        "test_size": int(len(y_test)),
        "feature_count": int(X.shape[1]),
        "class_balance": {"positive": int(y.sum()), "negative": int(len(y) - y.sum())},
        "cross_validation": {k: {"mean": float(np.mean(v)), "std": float(np.std(v))} for k, v in cv_scores.items()},
        "holdout_test": {
            "accuracy": float(test_acc),
            "f1": float(test_f1),
            "precision": float(test_precision),
            "recall": float(test_recall),
            "auc_roc": float(test_auc),
        },
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
    }
    with open(METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print(f"\n💾 Metrics saved to: {METRICS_PATH}")

    # ── 6. Confusion Matrix Plot ──
    os.makedirs(PLOTS_DIR, exist_ok=True)
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(
        cm, annot=True, fmt="d", cmap="Blues",
        xticklabels=["Dismissed/Weak", "Allowed/Success"],
        yticklabels=["Dismissed/Weak", "Allowed/Success"],
    )
    plt.title("Confusion Matrix (Hold-Out Test Set)")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "confusion_matrix.png"), dpi=150)
    plt.close()
    print(f"📊 Confusion matrix saved to: {os.path.join(PLOTS_DIR, 'confusion_matrix.png')}")

    # ── 7. Feature Importance Plot ──
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1]
    sorted_features = [X.columns[i] for i in indices]
    sorted_importances = importances[indices]

    top_n = min(25, len(sorted_features))
    plt.figure(figsize=(12, 10))
    sns.barplot(x=sorted_importances[:top_n], y=sorted_features[:top_n], palette="magma")
    plt.title("🔥 XGBoost Feature Importance (Top 25)")
    plt.xlabel("Importance Score")
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "feature_importance.png"), dpi=150)
    plt.close()
    print(f"📊 Feature importance saved to: {os.path.join(PLOTS_DIR, 'feature_importance.png')}")

    # ── 8. Save Model Artifact ──
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump({"model": model, "features": list(X.columns)}, MODEL_PATH)
    print(f"💾 Trained model saved to: {MODEL_PATH}")

    return metrics


if __name__ == "__main__":
    train_system_model()
