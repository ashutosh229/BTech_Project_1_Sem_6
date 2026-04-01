import pandas as pd
import json
import numpy as np
import os
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier

# --- Configuration ---
RESULTS_DIR = "/home/amaydixit11/Desktop/dev/Legal-Intelligence-System/results"
MATRIX_FILE = f"{RESULTS_DIR}/case_evidence_matrix.csv"
WEAK_INDEX = f"{RESULTS_DIR}/failed_cases_index.json"
MODEL_FILE = f"{RESULTS_DIR}/outcome_predictor.joblib"

def rank_causal_importance():
    # 1. Load Data
    if not os.path.exists(MATRIX_FILE):
        print(f"❌ Matrix file {MATRIX_FILE} not found.")
        return

    df = pd.read_csv(MATRIX_FILE)
    if not os.path.exists(WEAK_INDEX):
        print(f"❌ Weak case index {WEAK_INDEX} not found.")
        return

    with open(WEAK_INDEX, 'r') as f:
        weak_data = json.load(f)
    
    failed_ids = [c["case_id"] for c in weak_data]
    df['is_success'] = ~df['case_id'].isin(failed_ids)
    
    cluster_cols = [c for c in df.columns if c.startswith("cluster_")]
    X = df[cluster_cols]
    y = df['is_success']
    
    # 2. Gradient Boosting for Robust Feature Importance
    # This identifies "Importance Score" for each evidence type
    gb = GradientBoostingClassifier(n_estimators=200, learning_rate=0.1, max_depth=3, random_state=42)
    gb.fit(X, y)
    
    importances = gb.feature_importances_
    
    # 3. Logistic Regression for Directional Impact (Coefficient)
    lr = LogisticRegression(max_iter=1000)
    lr.fit(X, y)
    coefficients = lr.coef_[0]

    # Human-readable mapping
    cluster_names = {
        'cluster_0': 'Medical/FSL Reports',
        'cluster_1': 'Witness Testimony (PW)',
        'cluster_2': 'Agreements & Contracts',
        'cluster_3': 'Other Procedural Docs',
        'cluster_4': 'FIR/Seizure/PM Reports',
        'cluster_5': 'Property Deeds'
    }

    # 4. Result Assembly
    results = []
    for i, col in enumerate(cluster_cols):
        results.append({
            "Evidence Cluster": cluster_names.get(col, col),
            "Importance Score (%)": round(importances[i]*100, 2),
            "Impact Mode": "Positive" if coefficients[i] > 0 else "Negative (Contested)"
        })
    
    results = sorted(results, key=lambda x: x["Importance Score (%)"], reverse=True)
    
    print("\n" + "="*60)
    print("🏆 GRADIENT BOOSTED IMPORTANCE (CAUSAL RANKING)")
    print("="*60)
    print(f"{'Evidence Cluster':<35} | {'Importance (%)':<15} | {'Impact Type'}")
    print("-" * 75)
    
    for r in results:
        print(f"{r['Evidence Cluster']:<35} | {r['Importance Score (%)']:<15}% | {r['Impact Mode']}")

    # 5. Save Model and Metadata
    model_data = {
        "model": gb, # Now using GradientBoosting
        "feature_names": cluster_cols,
        "cluster_mapping": cluster_names,
        "global_rankings": results,
        "importances_raw": importances.tolist()
    }
    joblib.dump(model_data, MODEL_FILE)
    print(f"\n✅ Gradient Boosted Model Saved to: {MODEL_FILE}")

    # Save to JSON for backward compat
    with open(f"{RESULTS_DIR}/causal_ranking.json", 'w') as f:
        json.dump(results, f, indent=2)
        
    print(f"✅ Final Ranking Saved to: {RESULTS_DIR}/causal_ranking.json")

if __name__ == "__main__":
    rank_causal_importance()
