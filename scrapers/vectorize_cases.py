import os
import json
import re
import pandas as pd
from pathlib import Path
from collections import Counter

# --- Configuration ---
RESULTS_DIR = "/home/amaydixit11/Desktop/dev/Legal-Intelligence-System/results"
DATA_DIR = "/home/amaydixit11/Desktop/dev/Legal-Intelligence-System/data"
MAP_FILE = f"{RESULTS_DIR}/evidence_normalization_map.json"
OUTPUT_VECTOR_FILE = f"{RESULTS_DIR}/case_evidence_matrix.csv"

# Re-importing evidence patterns from pilot_extraction to keep consistency
EVIDENCE_PATTERNS = {
    "scientific_reports": r'\b(post\s?mortem|inquest|fsl|forensic|medical|chemical\sexaminer|autopsy|injury\sreport|postmortem\sreport)\b',
    "memos_panchnama": r'\b(recovery\smemo|seizure\smemo|mahazar|panchnama|inquest\spanchnama|spot\spanchnama)\b',
    "declarations_confessions": r'\b(dying\sdeclaration|confession)\b',
    "procedural_docs": r'\b(fir|first\sinformation\sreport|charge\ssheet|charge\sframed|exhibit|ex\.?|exhibit\sno\.)\b',
    "witness_testimony": r'\b(deposition|statement\sof\spw|testimony\sof\spw|deposed\sas\spw|deposed\sby\spw|witness\spw)\b',
    "legal_deeds": r'\b(sale\sdeed|mortgage\sdeed|gift\sdeed|rent\sagreement|last\swill\sand\stestament|mou|bond|agreement|receipt)\b'
}

def vectorize_corpus():
    # 1. Load Normalization Map
    with open(MAP_FILE, 'r') as f:
        norm_map = json.load(f)
    
    # Identify unique clusters (ignore -1 noise if present)
    clusters = sorted(list(set(norm_map.values())))
    if -1 in clusters: clusters.remove(-1)
    
    print(f"🧬 Loaded normalization map with {len(clusters)} valid semantic clusters.")

    # 2. Process all cases
    case_vectors = []
    json_files = list(Path(DATA_DIR).glob('*.json'))
    
    print(f"🛰️ Vectorizing {len(json_files)} cases...")

    for i, json_path in enumerate(json_files):
        if i % 500 == 0: print(f"   Processed {i} cases...")
        
        case_id = json_path.stem
        vector = {f"cluster_{cid}": 0 for cid in clusters}
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except: continue
        
        elements = data.get("elements_by_title", {})
        target_sections = ["Court's Reasoning", "Analysis of the law", "Conclusion"]
        
        # Extract matches from targeted sections
        for section in target_sections:
            if section in elements:
                section_text = " ".join([item.get("text", "") for item in elements[section]]).lower()
                
                # Check for each pattern
                for cat, pattern in EVIDENCE_PATTERNS.items():
                    matches = re.findall(pattern, section_text)
                    for m in matches:
                        # If the match was structured as a group (list) by re.findall
                        match_str = m[0] if isinstance(m, tuple) else m
                        
                        # Map match to cluster ID
                        if match_str in norm_map:
                            cid = norm_map[match_str]
                            if cid != -1:
                                vector[f"cluster_{cid}"] = 1
        
        case_data = {"case_id": case_id}
        case_data.update(vector)
        case_vectors.append(case_data)

    # 3. Save to Matrix CSV
    df = pd.DataFrame(case_vectors)
    df.to_csv(OUTPUT_VECTOR_FILE, index=False)
    
    print(f"✅ Full-scale vectorization complete.")
    print(f"💾 Case Evidence Matrix saved to: {OUTPUT_VECTOR_FILE}")
    print(f"📊 Matrix Shape: {df.shape}")

if __name__ == "__main__":
    vectorize_corpus()
