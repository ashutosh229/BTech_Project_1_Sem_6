import os
import json
import re
import pandas as pd
from pathlib import Path
from tqdm import tqdm

# --- Configuration ---
DATA_DIR = "/home/amaydixit11/Desktop/dev/Legal-Intelligence-System/data"
RESULTS_DIR = "/home/amaydixit11/Desktop/dev/Legal-Intelligence-System/results"
WEAK_INDEX = f"{RESULTS_DIR}/failed_cases_index.json"
MATRIX_FILE = f"{RESULTS_DIR}/case_evidence_matrix.csv"

# Diagnostic Patterns
FAILURE_MODES = {
    "Delay": [r'\bdelayed\b', r'\blaches\b', r'\bunexplained\sdelay\b', r'\binordinate\sdelay\b'],
    "Contradiction": [r'\bcontradicts\b', r'\binconsistent\b', r'\bdifferent\sversion\b', r'\bcontrary\sto\b', r'\bdiscrepancy\b'],
    "Non-Production": [r'\bnot\sproduced\b', r'\bwithheld\b', r'\bnot\sexamined\b', r'\bnot\scited\b', r'\bnon-examination\b'],
    "Benefit of Doubt / Credibility": [r'\binterested\switness\b', r'\bpartisan\b', r'\bnot\scredible\b', r'\bbenfit\sof\sdoubt\b', r'\btestimony\sis\sunreliable\b']
}

def diagnose_failures():
    # 1. Load Resources
    with open(WEAK_INDEX, 'r') as f:
        weak_data = json.load(f)
    matrix_df = pd.read_csv(MATRIX_FILE)
    
    diagnostic_report = []
    cluster_cols = [c for c in matrix_df.columns if c.startswith('cluster_')]

    print(f"🕵️ Analyzing {len(weak_data)} weak cases for Failure Modes...")

    for case_meta in tqdm(weak_data):
        case_id = case_meta['case_id']
        path = Path(DATA_DIR) / f"{case_id}.json"
        
        if not path.exists(): continue
        
        # Load Case Text (Reasoning section specifically)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            reasoning = " ".join([item.get("text", "") for item in data.get("elements_by_title", {}).get("Court's Reasoning", [])]).lower()
        except: continue
        
        # Get Evidence Presence
        row = matrix_df[matrix_df['case_id'] == case_id].iloc[0]
        
        modes_found = []
        for mode, patterns in FAILURE_MODES.items():
            for p in patterns:
                if re.search(p, reasoning):
                    modes_found.append(mode)
                    break
        
        diagnostic_report.append({
            "case_id": case_id,
            "failed_reason": case_meta.get("reason", "Unknown"),
            "failure_modes": list(set(modes_found)),
            "evidence_count": int(sum([row[c] for c in cluster_cols]))
        })

    # 2. Aggregation & Statistics
    df = pd.DataFrame(diagnostic_report)
    df.to_csv(f"{RESULTS_DIR}/failure_diagnostics.csv", index=False)
    
    # Explode failure_modes column to get frequency count
    exploded_df = df.explode('failure_modes')
    stats = exploded_df['failure_modes'].value_counts().reset_index()
    stats.columns = ['Failure Mode', 'Occurrence Count']

    print("\n" + "="*60)
    print("📈 FAILURE MODE CLASSIFICATION (DIAGNOSTIC SUMMARY)")
    print("="*60)
    print(stats)
    print(f"\n💾 Saved detailed report to: {RESULTS_DIR}/failure_diagnostics.csv")

if __name__ == "__main__":
    diagnose_failures()
