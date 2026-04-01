import pandas as pd
import numpy as np
import os
import json
import sys

# Ensure root is in path
sys.path.append(os.getcwd())

from con.feature_builder import LegalFeatureBuilder

def build_phi_matrix(results_dir="data/results/"):
    """
    Step 11: Dataset Assembly for Regression/Classification.
    Iterates over system intelligence reports and builds a Phi-Matrix.
    """
    if not os.path.exists(results_dir):
        print(f"⚠️ Results directory not found at {results_dir}. Run batch_process.py first.")
        return None

    files = [f for f in os.listdir(results_dir) if f.endswith(".json")]
    print(f"🚀 Processing {len(files)} Intelligence Reports into Phi Matrix...")

    builder = LegalFeatureBuilder()
    phi_records = []
    
    for filename in files:
        with open(os.path.join(results_dir, filename), 'r') as f:
            data = f.read()
            if not data: continue
            try:
                # We need to map the Intelligence Report -> Feature Vector
                # A Typical report from main_pipeline.py includes:
                # {con: ..., similar_cases: ..., missing_evidence: ..., contradictions: ...}
                report = json.loads(data)
                
                # Mock: we need to handle if results/ files are missing these subfields
                # (Fix: our last batch run had a simpler 'stats' schema, I'll adapt)
                con = report.get("con", {})
                if not con and "stats" in report:
                    # Map from the summary format if needed
                    con = {"case_type": report["case_type"], "claims": [], "evidence_present": []}
                    similar = [] # Fallback
                else:
                    similar = report.get("similar_cases", [])
                
                missing = report.get("missing_evidence", [])
                contradictions = report.get("contradictions", {})

                # Generate the 20-D Phi Vector
                vec, _ = builder.build(con, similar, missing, contradictions)
                
                # Attach ground truth from outcome in report
                outcome = report.get("judgment_probability", {}).get("prediction", "")
                if not outcome and "stats" in report:
                     outcome = report["stats"].get("judgment", "")
                
                label = 1 if "Allowed/Success" in str(outcome) else 0
                
                record = {name: val for name, val in zip(builder.feature_names, vec)}
                record["label"] = label
                record["case_id"] = filename.replace(".json", "")
                
                phi_records.append(record)
                
            except Exception as e:
                print(f"❌ Error in {filename}: {e}")
                continue

    # 3. SAVE Final Dataset for Training/Ablation Study
    if phi_records:
        df_phi = pd.DataFrame(phi_records)
        os.makedirs("data/dataset", exist_ok=True)
        df_phi.to_csv("data/dataset/final_phi_features.csv", index=False)
        
        print(f"✅ Phi-Matrix Ready: {len(df_phi)} samples with {len(builder.feature_names)} features.")
        print("Columns:", df_phi.columns.tolist())
        return df_phi
    else:
         print("⚠️ No valid records found.")
         return None

if __name__ == "__main__":
    build_phi_matrix()
