import pandas as pd
import json
import os

def run_causal_analysis():
    # 1. Load Data
    matrix_file = "/home/amaydixit11/Desktop/dev/Legal-Intelligence-System/results/case_evidence_matrix.csv"
    weak_file = "/home/amaydixit11/Desktop/dev/Legal-Intelligence-System/results/failed_cases_index.json"
    
    if not os.path.exists(matrix_file) or not os.path.exists(weak_file):
        print("Missing data files.")
        return

    matrix_df = pd.read_csv(matrix_file)
    with open(weak_file, "r") as f:
        failed_cases_meta = json.load(f)

    # 2. Tag cases as Failed/Success
    failed_ids = [c["case_id"] for c in failed_cases_meta]
    matrix_df["is_weak"] = matrix_df["case_id"].isin(failed_ids)

    # 3. Aggregate Frequencies
    cluster_cols = [c for c in matrix_df.columns if c.startswith("cluster_")]
    stats = matrix_df.groupby("is_weak")[cluster_cols].mean().transpose()
    
    # After groupby, stats.columns might be [False, True] for is_weak
    stats.columns = ["Success_Prob", "Weak_Prob"]

    # 4. Calculate the "Differential Gap"
    stats["Differential_Gap"] = stats["Success_Prob"] - stats["Weak_Prob"]
    stats = stats.sort_values(by="Differential_Gap", ascending=False)

    # 5. Human-Readable Mapping (Based on InLegalBERT Clustering Results)
    cluster_names = {
        "cluster_0": "Medical/Confession/Inquest Markers",
        "cluster_1": "Witness Testimony (PW Statements)",
        "cluster_2": "Agreements & Contracts",
        "cluster_4": "Criminal Reports (FIR/Seizure/PM)",
        "cluster_5": "Property Deeds (Sale/Gift/Mortgage)",
        "cluster_3": "Other Procedural Documents"
    }

    print("\n" + "="*50)
    print("🧠 CAUSAL IMPORTANCE: THE EVIDENTIARY GAP")
    print("="*50)
    print(f"{'Evidence Category':<35} | {'Success':<10} | {'Weak':<10} | {'Gap'}")
    print("-" * 75)

    for idx, row in stats.iterrows():
        name = cluster_names.get(idx, idx)
        s_pct = f"{row['Success_Prob']*100:.1f}%"
        w_pct = f"{row['Weak_Prob']*100:.1f}%"
        gap = f"{row['Differential_Gap']*100:+.1f}%"
        print(f"{name:<35} | {s_pct:<10} | {w_pct:<10} | {gap}")

if __name__ == "__main__":
    run_causal_analysis()
