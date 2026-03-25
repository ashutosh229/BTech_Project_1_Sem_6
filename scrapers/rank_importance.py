import pandas as pd
import json
import numpy as np
import os
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

# --- Configuration ---
RESULTS_DIR = "/home/amaydixit11/Desktop/dev/Legal-Intelligence-System/results"
MATRIX_FILE = f"{RESULTS_DIR}/case_evidence_matrix.csv"
WEAK_INDEX = f"{RESULTS_DIR}/failed_cases_index.json"

def rank_causal_importance():
    # 1. Load Data
    df = pd.read_csv(MATRIX_FILE)
    with open(WEAK_INDEX, 'r') as f:
        weak_data = json.load(f)
    
    failed_ids = [c["case_id"] for c in weak_data]
    df['is_success'] = ~df['case_id'].isin(failed_ids)
    
    cluster_cols = [c for c in df.columns if c.startswith("cluster_")]
    X = df[cluster_cols]
    y = df['is_success']
    
    # 2. Random Forest for Feature Importance
    # This identifies which evidence matters MOST for winning (being "Successful")
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X, y)
    
    importances = rf.feature_importances_
    
    # 3. Logistic Regression for Directional Impact (Coefficient)
    lr = LogisticRegression()
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
    print("🏆 GLOBAL CAUSAL RANKING (STATISTICAL SIGNIFICANCE)")
    print("="*60)
    print(f"{'Evidence Cluster':<35} | {'Importance (%)':<15} | {'Impact Type'}")
    print("-" * 75)
    
    for r in results:
        print(f"{r['Evidence Cluster']:<35} | {r['Importance Score (%)']:<15}% | {r['Impact Mode']}")

    # Save to JSON
    with open(f"{RESULTS_DIR}/causal_ranking.json", 'w') as f:
        json.dump(results, f, indent=2)
        
    print(f"\n✅ Final Ranking Saved to: {RESULTS_DIR}/causal_ranking.json")

if __name__ == "__main__":
    rank_causal_importance()
