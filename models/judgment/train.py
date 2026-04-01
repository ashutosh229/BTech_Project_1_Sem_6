import pandas as pd
import numpy as np
import os
import joblib
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

def train_system_model(X_path="data/dataset/X_features.csv", y_path="data/dataset/y_labels.csv"):
    """
    Step 9: Training Loop for the Judgment Inference Model.
    The primary 'AI' of the system that learns from historical evidentiary signals.
    """
    if not os.path.exists(X_path):
        print(f"⚠️ Dataset not found at {X_path}. Run scripts/prepare_dataset.py first.")
        return

    # 1. Loading Training Data
    X = pd.read_csv(X_path)
    y = pd.read_csv(y_path)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y.values.ravel(), test_size=0.2, random_state=42)
    
    print(f"🚀 Training Judgment Engine on {len(X_train)} samples...")

    # 2. Training Gradient Boosting Model
    model = XGBClassifier(n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42)
    model.fit(X_train, y_train)

    # 3. Model Evaluation
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"✅ Training Complete. Model Accuracy: {acc*100:.2f}%")
    print("\n📝 Classification Report:\n", classification_report(y_test, y_pred))

    # 4. Feature Importance (THE WOW FACTOR)
    plt.figure(figsize=(10, 6))
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
