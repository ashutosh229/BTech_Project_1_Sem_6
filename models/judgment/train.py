import pandas as pd
import numpy as np
import os
import joblib
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

def train_system_model(
    dataset_path="data/dataset/final_phi_features.csv",
    X_path="data/dataset/X_features.csv",
    y_path="data/dataset/y_labels.csv",
):
    """
    Step 9: Training Loop for the Judgment Inference Model.
    The primary 'AI' of the system that learns from historical evidentiary signals.
    """
    if os.path.exists(dataset_path):
        df = pd.read_csv(dataset_path)
        if "label" not in df.columns:
            print(f"⚠️ label column missing in {dataset_path}.")
            return
        drop_cols = [c for c in ["case_id", "true_outcome", "label"] if c in df.columns]
        X = df.drop(columns=drop_cols)
        y = df["label"]
    else:
        if not os.path.exists(X_path) or not os.path.exists(y_path):
            print(f"⚠️ Dataset not found. Run scripts/prepare_dataset.py first.")
            return

        # 1. Loading Training Data
        X = pd.read_csv(X_path)
        y = pd.read_csv(y_path).values.ravel()

    X_train, X_test, y_train, y_test = train_test_split(X, np.asarray(y).ravel(), test_size=0.2, random_state=42, stratify=np.asarray(y).ravel())
    
    print(f"🚀 Training Judgment Engine on {len(X_train)} samples...")

    # 2. Training Gradient Boosting Model
    model = XGBClassifier(
        n_estimators=250,
        learning_rate=0.05,
        max_depth=6,
        subsample=0.9,
        colsample_bytree=0.9,
        eval_metric="logloss",
        random_state=42,
    )
    model.fit(X_train, y_train)

    # 3. Model Evaluation
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"✅ Training Complete. Model Accuracy: {acc*100:.2f}%")
    print("\n📝 Classification Report:\n", classification_report(y_test, y_pred))

    # 4. Feature Importance (THE WOW FACTOR)
    os.makedirs("outputs/plots", exist_ok=True)
    plt.figure(figsize=(12, 10))
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1]
    sorted_features = [X.columns[i] for i in indices]
    
    sns.barplot(x=importances[indices], y=sorted_features, palette='magma')
    plt.title("🔥 Causal Driver Identification (XGBoost Feature Importance)")
    plt.xlabel("Predictive Power Score")
    plt.savefig("outputs/plots/feature_importance.png")
    plt.close()
    
    # 5. Saving Artifact
    model_path = "data/processed/judgment_model.joblib"
    joblib.dump({"model": model, "features": list(X.columns)}, model_path)
    print(f"💾 Trained Judgment Model saved to: {model_path}")

if __name__ == "__main__":
    train_system_model()
