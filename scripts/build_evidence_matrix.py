import os
import json
import re
import pandas as pd
from tqdm import tqdm
import sys

# Ensure root is in path
sys.path.append(os.getcwd())
from pipelines.pipeline1_old_cases.evidence_extractor import extract_evidence

def build_total_evidence_matrix(data_dir="data/"):
    """
    Step 11: High-Speed Evidence Matrix Builder (Total Corpus).
    Parses all 9703 cases across all High Courts.
    """
    files = [f for f in os.listdir(data_dir) if f.endswith(".json")]
    print(f"🚀 High-Speed Extraction from TOTAL Corpus: {len(files)} judgments...")
    
    records = []
    
    for filename in tqdm(files):
        try:
            with open(os.path.join(data_dir, filename), 'r') as f:
                data = json.load(f)
                all_text = ""
                # Attempt to get full text
                if "elements_by_title" in data:
                    for section in data["elements_by_title"].values():
                        all_text += " ".join([elem.get("text", "") for elem in section if isinstance(elem, dict)])
                
                # Extract 6-D Vector
                vec, counts = extract_evidence(all_text)
                
                record = {
                    "case_id": filename.replace(".json", ""),
                    "ev_medical": vec[0],
                    "ev_witness": vec[1],
                    "ev_contract": vec[2],
                    "ev_procedural": vec[3],
                    "ev_memo": vec[4],
                    "ev_deeds": vec[5],
                    "ev_total_matches": counts.get("matches", 0)
                }
                records.append(record)
        except Exception as e:
            continue
            
    if records:
        df = pd.DataFrame(records)
        os.makedirs("data/processed", exist_ok=True)
        df.to_csv("data/processed/real_evidence_matrix.csv", index=False)
        print(f"✅ Real Evidence Matrix saved: {len(df)} samples.")
    else:
        print("⚠️ No cases processed.")

if __name__ == "__main__":
    build_total_evidence_matrix()
