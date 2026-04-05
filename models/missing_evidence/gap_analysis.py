import pandas as pd
import json
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")

def run_causal_analysis(
    matrix_file=os.path.join(PROCESSED_DIR, "real_evidence_matrix.csv"),
    weak_file=os.path.join(PROCESSED_DIR, "weak_case_scores.json"),
):
    # 1. Load Data
    if not os.path.exists(matrix_file) or not os.path.exists(weak_file):
        print("Missing data files.")
        return

    matrix_df = pd.read_csv(matrix_file)
    with open(weak_file, "r") as f:
        weak_meta = json.load(f)

    # 2. Tag cases as Weak/Strong using probabilities where available.
    if isinstance(weak_meta, dict):
        matrix_df["weak_probability"] = matrix_df["case_id"].map(
            lambda cid: float(weak_meta.get(cid, {}).get("weak_probability", 0.0))
        )
        matrix_df["is_weak"] = matrix_df["weak_probability"] >= 0.60
    else:
        failed_ids = [c["case_id"] for c in weak_meta]
        matrix_df["is_weak"] = matrix_df["case_id"].isin(failed_ids)

    # 3. Aggregate Frequencies
    cluster_cols = [
        c for c in matrix_df.columns
        if (c.startswith("ev_") and c != "ev_total_matches") or c.startswith("fg_")
    ]
    stats = matrix_df.groupby("is_weak")[cluster_cols].mean().transpose()
    
    # After groupby, stats.columns might be [False, True] for is_weak
    stats.columns = ["Success_Prob", "Weak_Prob"]

    # 4. Calculate the "Differential Gap"
    stats["Differential_Gap"] = stats["Success_Prob"] - stats["Weak_Prob"]
    stats = stats.sort_values(by="Differential_Gap", ascending=False)

    # 5. Human-Readable Mapping (Based on InLegalBERT Clustering Results)
    cluster_names = {
        "ev_medical": "Medical/FSL Reports",
        "ev_witness": "Witness Testimony (PW)",
        "ev_contract": "Agreements & Contracts",
        "ev_memo": "FIR/Seizure/PM Reports",
        "ev_deeds": "Property Deeds",
        "ev_procedural": "Other Procedural Documents",
    }
    for col in cluster_cols:
        if col.startswith("fg_") and col not in cluster_names:
            cluster_names[col] = col.replace("fg_", "").replace("_", " ").title()

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
