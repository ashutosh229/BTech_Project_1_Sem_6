import os
import json
import re
from pathlib import Path

# --- Specific markers that indicate an evidentiary weakness ---
WEAKNESS_MARKERS = [
    r'benefit\s?of\s?doubt',
    r'lack\sof\sevidence',
    r'insufficient\sevidence',
    r'failed\sto\sprove',
    r'not\sproven\sbeyond\sreasonable\sdoubt',
    r'absence\sof\smaterial\sevidence',
    r'prosecution\sfailed\sto\scorroborate',
    r'no\scorroborative\sevidence',
    r'failure\sto\sproduce\smaterial\switness',
    r'gap\sin\sthe\schain\sof\sevidence'
]

def find_weak_cases(data_dir, output_file):
    weak_cases = []
    total_processed = 0
    
    print(f"🕵️ Scanning 12,024 cases for evidentiary 'Weakness Markers'...")

    for json_path in Path(data_dir).glob('*.json'):
        # Skip cleaning script and meta files
        if json_path.name.startswith('_'): continue
        
        total_processed += 1
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except: continue
        
        case_id = json_path.stem
        elements = data.get("elements_by_title", {})
        
        # We focus primarily on the 'Conclusion' or 'Court's Reasoning'
        # These are where the court explicitly calls out evidentiary gaps
        search_text = []
        if "Conclusion" in elements:
            search_text.append(" ".join([i.get("text", "") for i in elements["Conclusion"]]))
        if "Court's Reasoning" in elements:
            search_text.append(" ".join([i.get("text", "") for i in elements["Court's Reasoning"]]))
        
        full_text = " ".join(search_text).lower()
        
        # Check for matches
        found_markers = [m for m in WEAKNESS_MARKERS if re.search(m, full_text)]
        
        if found_markers:
            weak_cases.append({
                "case_id": case_id,
                "court": data.get("court_name", "N/A"),
                "year": case_id.split('_')[1] if '_' in case_id else "N/A",
                "markers_found": found_markers
            })

    # Save to JSON index
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(weak_cases, f, indent=2)

    print(f"✅ Scanning complete. Processed {total_processed} cases.")
    print(f"📈 Found {len(weak_cases)} potential 'Weak Cases' (cases that died for lack of evidence).")

if __name__ == "__main__":
    BASE_DIR = "/home/amaydixit11/Desktop/dev/Legal-Intelligence-System"
    DATA_DIR = f"{BASE_DIR}/data"
    OUTPUT = f"{BASE_DIR}/results/failed_cases_index.json"
    
    find_weak_cases(DATA_DIR, OUTPUT)
