import re
import os
import json

# Internal Evidence Patterns extracted from vectorize_cases.py for consistency
EVIDENCE_PATTERNS = {
    "scientific_reports": r'\b(post\s?mortem|inquest|fsl|forensic|medical|chemical\sexaminer|autopsy|injury\sreport|postmortem\sreport)\b',
    "memos_panchnama": r'\b(recovery\smemo|seizure\smemo|mahazar|panchnama|inquest\spanchnama|spot\spanchnama)\b',
    "declarations_confessions": r'\b(dying\sdeclaration|confession)\b',
    "procedural_docs": r'\b(fir|first\sinformation\sreport|charge\ssheet|charge\sframed|exhibit|ex\.?|exhibit\sno\.)\b',
    "witness_testimony": r'\b(deposition|statement\sof\spw|testimony\sof\spw|deposed\sas\spw|deposed\sby\spw|witness\spw)\b',
    "legal_deeds": r'\b(sale\sdeed|mortgage\sdeed|gift\sdeed|rent\sagreement|last\swill\sand\stestament|mou|bond|agreement|receipt)\b'
}

def extract_evidence(text):
    """
    Scans text for evidence clusters and returns a binary vector 
    and the raw count of matches.
    """
    text = text.lower()
    vector = []
    found_counts = {}
    
    # We follow the 6 clusters defined in the project:
    # 0: Medical, 1: PW Testimony, 2: Agreements, 3: Other Procedural, 4: FIR/PM/Seizure, 5: Deeds
    # (Mapping based on vectorize_cases.py and cluster_evidence.py semantic output)
    categories = [
        "scientific_reports",      # Cluster 0
        "witness_testimony",      # Cluster 1
        "procedural_docs",         # Cluster 4
        "memos_panchnama",         # Cluster 4/3
        "declarations_confessions",# Cluster 3
        "legal_deeds"              # Cluster 2/5
    ]
    
    # Simpler approach: Create a 6-item binary vector for the GBC model
    # Order: [Medical/FSL, PW Testimony, Agreements, Procedural, FIR/PM/Seizure, Deeds]
    # We follow the index from CLUSTER_NAMES in main_pipeline
    
    final_vector = [0] * 6
    
    # Mapping our regex categories to our visual clusters
    # 0: Medical/FSL Reports -> 'scientific_reports'
    # 1: Witness Testimony (PW) -> 'witness_testimony'
    # 2: Agreements & Contracts -> 'legal_deeds'
    # 3: Other Procedural Docs -> 'procedural_docs'
    # 4: FIR/Seizure/PM Reports -> 'memos_panchnama'
    # 5: Property Deeds -> 'legal_deeds'
    
    if re.search(EVIDENCE_PATTERNS["scientific_reports"], text): final_vector[0] = 1
    if re.search(EVIDENCE_PATTERNS["witness_testimony"], text): final_vector[1] = 1
    if re.search(EVIDENCE_PATTERNS["legal_deeds"], text): final_vector[2] = 1
    if re.search(EVIDENCE_PATTERNS["procedural_docs"], text): final_vector[3] = 1
    if re.search(EVIDENCE_PATTERNS["memos_panchnama"], text): final_vector[4] = 1
    # For cluster 5, we reuse deeds or specific markers
    if re.search(r"sale deed|gift deed", text): final_vector[5] = 1
    
    return final_vector, {"matches": sum(final_vector)}

def extract_case_metadata(parsed_case):
    """Legacy wrapper for backward compatibility."""
    all_text = " ".join([str(v) for v in parsed_case.values() if isinstance(v, str)]).lower()
    vec, counts = extract_evidence(all_text)
    parsed_case["evidence_vector"] = vec
    return parsed_case

if __name__ == "__main__":
    test_text = "The postmortem report and the recovery memo were filed as PW witnesses deposed."
    print("Extracted Evidence Vector:", extract_evidence(test_text))