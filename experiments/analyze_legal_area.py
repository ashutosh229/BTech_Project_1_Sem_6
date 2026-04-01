import pandas as pd
import json
import os
from sklearn.ensemble import RandomForestClassifier

# --- Configuration ---
RESULTS_DIR = "/home/amaydixit11/Desktop/dev/Legal-Intelligence-System/results"
MATRIX_FILE = f"{RESULTS_DIR}/case_evidence_matrix.csv"
WEAK_INDEX = f"{RESULTS_DIR}/failed_cases_index.json"

# Human-readable cluster names
CLUSTER_NAMES = {
    'cluster_0': 'Medical/FSL Reports',
    'cluster_1': 'Witness Testimony (PW)',
    'cluster_2': 'Agreements & Contracts',
    'cluster_3': 'Other Procedural Docs',
    'cluster_4': 'FIR/Seizure/PM Reports',
    'cluster_5': 'Property Deeds'
}

def analyze_legal_areas():
    # 1. Load Data
    df = pd.read_csv(MATRIX_FILE)
    with open(WEAK_INDEX, 'r') as f:
        weak_data = json.load(f)
    failed_ids = [c["case_id"] for c in weak_data]
    df['is_success'] = ~df['case_id'].isin(failed_ids)
    
    # 2. Heuristic Categorization (Criminal vs Civil)
    # Based on the presence of typical evidence clusters
    df['is_criminal_nature'] = ((df['cluster_0'] == 1) | (df['cluster_4'] == 1)).astype(int)
    df['is_civil_nature'] = ((df['cluster_2'] == 1) | (df['cluster_5'] == 1)).astype(int)
    
    criminal_df = df[df['is_criminal_nature'] == 1]
    civil_df = df[df['is_civil_nature'] == 1]
    
    cluster_cols = [c for c in df.columns if c.startswith("cluster_")]

    def get_importance(subset_df):
        if len(subset_df) < 50: return None
        X = subset_df[cluster_cols]
        y = subset_df['is_success']
        rf = RandomForestClassifier(n_estimators=100, random_state=42)
        rf.fit(X, y)
        return rf.feature_importances_

    crim_importances = get_importance(criminal_df)
    civil_importances = get_importance(civil_df)

    # 3. Visualization Mapping
    print("\n" + "="*70)
    print("📈 STATUTE-SPECIFIC EVIDENCE IMPORTANCE (CRIMINAL vs CIVIL)")
    print("="*70)
    print(f"{'Evidence Cluster':<30} | {'Criminal (%)':<15} | {'Civil (%)'}")
    print("-" * 75)

    for i, col in enumerate(cluster_cols):
        name = CLUSTER_NAMES.get(col, col)
        crim_val = f"{crim_importances[i]*100:>10.1f}%" if crim_importances is not None else "N/A"
        civil_val = f"{civil_importances[i]*100:>10.1f}%" if civil_importances is not None else "N/A"
        print(f"{name:<30} | {crim_val:<15} | {civil_val}")

    # Save comparison data
    summary = {
        "criminal": dict(zip(cluster_cols, crim_importances.tolist() if crim_importances is not None else [])),
        "civil": dict(zip(cluster_cols, civil_importances.tolist() if civil_importances is not None else []))
    }
    with open(f"{RESULTS_DIR}/legal_area_comparison.json", 'w') as f:
        json.dump(summary, f, indent=2)

if __name__ == "__main__":
    analyze_legal_areas()
