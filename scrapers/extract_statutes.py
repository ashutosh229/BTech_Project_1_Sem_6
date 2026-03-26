import os
import json
import re
import pandas as pd
from pathlib import Path
from collections import Counter
from tqdm import tqdm

DATA_DIR = "/home/amaydixit11/Desktop/dev/Legal-Intelligence-System/data"
RESULTS_DIR = "/home/amaydixit11/Desktop/dev/Legal-Intelligence-System/results"
OUTPUT_FILE = f"{RESULTS_DIR}/case_statutes.csv"

# Broad patterns for Indian Statutes
STATUTE_PATTERNS = [
    r'section\s+(\d+[A-Za-z]?)\b', # General Section matching
    r'article\s+(\d+[A-Za-z]?)\b', # Constitutional Articles
    r'(ipc|crpc|ni\sact|cpc|evidence\sact|constitution)', # Main Acts
]

def extract_statutes():
    json_files = list(Path(DATA_DIR).glob('*.json'))
    results = []
    
    print(f"⚖️ Extracting Legal Statutes from {len(json_files)} cases...")
    
    for path in tqdm(json_files):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract from Title and first part of Reasoning
            text = (data.get("page_title", "") + " " + 
                    " ".join([item.get("text", "") for item in data.get("elements_by_title", {}).get("Analysis of the law", [])[:2]])).lower()
            
            # Find IPC/CrPC specifically
            ipc_match = re.search(r'section\s+(\d+[A-Za-z]?)\s+of\s+the\s+(?:ipc|indian\spenal\scode)', text)
            section = ipc_match.group(1) if ipc_match else "Unknown"
            
            # If not found, try general section
            if section == "Unknown":
                gen_match = re.search(r'section\s+(\d+[A-Za-z]?)\b', text)
                section = gen_match.group(1) if gen_match else "Other"

            results.append({
                "case_id": path.stem,
                "primary_section": section,
                "is_ipc": 1 if "ipc" in text or "penal code" in text else 0
            })
        except: continue

    df = pd.DataFrame(results)
    df.to_csv(OUTPUT_FILE, index=False)
    
    # Show Top 10 Sections found
    print("\n--- Top 10 Legal Sections Found ---")
    print(df['primary_section'].value_counts().head(10))
    print(f"\n💾 Saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    extract_statutes()
