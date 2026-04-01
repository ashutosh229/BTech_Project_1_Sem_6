import os
import json
import re
import csv
from pathlib import Path
from collections import Counter

# --- Master Evidence Patterns (Tailored for Indian Law & Your Dataset) ---
EVIDENCE_PATTERNS = {
    "scientific_reports": r'\b(post\s?mortem|inquest|fsl|forensic|medical|chemical\sexaminer|autopsy|injury\sreport|postmortem\sreport)\b',
    "memos_panchnama": r'\b(recovery\smemo|seizure\smemo|mahazar|panchnama|inquest\spanchnama|spot\spanchnama)\b',
    "declarations_confessions": r'\b(dying\sdeclaration|confession)\b',
    "procedural_docs": r'\b(fir|first\sinformation\sreport|charge\ssheet|charge\sframed|exhibit|ex\.?|exhibit\sno\.)\b',
    "witness_testimony": r'\b(deposition|statement\sof\spw|testimony\sof\spw|deposed\sas\spw|deposed\sby\spw|witness\spw)\b',
    "legal_deeds": r'\b(sale\sdeed|mortgage\sdeed|gift\sdeed|rent\sagreement|last\swill\sand\stestament|mou|bond|agreement|receipt)\b'
}

def extract_evidence(data_dir, output_csv, case_stats_csv, sample_size=500):
    all_findings = []
    case_summary = []
    json_files = list(Path(data_dir).glob('*.json'))[:sample_size]
    
    print(f"🚀 Starting Pilot Extraction on {len(json_files)} files...")

    for json_path in json_files:
        case_id = json_path.stem
        evidence_counts = Counter()
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"⚠️ Error reading {json_path}: {e}")
            continue
            
        elements = data.get("elements_by_title", {})
        # Target Reasoning and Analysis sections for evidentiary reliability
        target_sections = ["Court's Reasoning", "Analysis of the law", "Conclusion"]
        
        findings_in_case = []
        for section in target_sections:
            if section in elements:
                section_text = " ".join([item.get("text", "") for item in elements[section]]).lower()
                
                for category, pattern in EVIDENCE_PATTERNS.items():
                    matches = re.finditer(pattern, section_text)
                    for match in matches:
                        evidence_counts[category] += 1
                        
                        # Extract 40 chars context
                        start, end = match.start(), match.end()
                        context = section_text[max(0, start-40):min(len(section_text), end+40)].strip()
                        
                        findings_in_case.append({
                            "case_id": case_id,
                            "category": category,
                            "matched_text": match.group(),
                            "context": context
                        })
        
        all_findings.extend(findings_in_case)
        case_summary.append({
            "case_id": case_id,
            "total_evidence_mentions": sum(evidence_counts.values()),
            **dict(evidence_counts)
        })

    # Save detailed findings
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["case_id", "category", "matched_text", "context"])
        writer.writeheader()
        writer.writerows(all_findings)
        
    # Save case-level summary (Density analysis)
    with open(case_stats_csv, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ["case_id", "total_evidence_mentions"] + list(EVIDENCE_PATTERNS.keys())
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(case_summary)
    
    print(f"✅ Pilot complete.")
    print(f"📊 Detailed Findings: {output_csv}")
    print(f"📈 Case Summary Stats: {case_stats_csv}")

if __name__ == "__main__":
    BASE_DIR = "/home/amaydixit11/Desktop/dev/Legal-Intelligence-System"
    RESULTS_DIR = f"{BASE_DIR}/results"
    OUTPUT_FILE = f"{RESULTS_DIR}/pilot_evidence_results.csv"
    STATS_FILE = f"{RESULTS_DIR}/pilot_case_stats.csv"
    
    extract_evidence(DATA_DIR, OUTPUT_FILE, STATS_FILE)
