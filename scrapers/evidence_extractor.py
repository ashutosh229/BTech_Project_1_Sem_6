import re
from parse_case_json import parse_real_case_json
def extract_case_metadata(parsed_case):
    """
    Takes the cleaned case dictionary and extracts Outcome and Evidence.
    """
    # 1. OUTCOME EXTRACTION
    # We primarily look at the 'conclusion' or 'courts_reasoning'
    conclusion_text = parsed_case.get("conclusion", "").lower()
    
    # Simple regex patterns for Indian court outcomes
    if re.search(r'\b(allowed|acquitted|granted)\b', conclusion_text):
        parsed_case["outcome"] = "allowed/acquitted"
    elif re.search(r'\b(dismissed|convicted|rejected)\b', conclusion_text):
        parsed_case["outcome"] = "dismissed/convicted"
    else:
        parsed_case["outcome"] = "ambiguous"

    # 2. EVIDENCE EXTRACTION
    # We scan the entire case for mentions of standard legal evidence
    # We combine all text into one big string for the evidence scan
    all_text = " ".join([str(v) for v in parsed_case.values() if isinstance(v, str)]).lower()
    
    # List of common evidence types to look for (you will expand this list later!)
    evidence_patterns = {
        "postmortem_report": r'post\s?mortem\s?report',
        "fir": r'\bfir\b|first information report',
        "charge_sheet": r'charge\s?sheet',
        "witness_testimony": r'witness|testimony|deposed',
        "medical_certificate": r'medical (report|certificate)',
        "recovery_memo": r'recovery memo',
        "dying_declaration": r'dying declaration'
    }

    found_evidence = set() # Use a set to avoid duplicates
    
    for evidence_name, pattern in evidence_patterns.items():
        if re.search(pattern, all_text):
            found_evidence.add(evidence_name)
            
    parsed_case["evidence_list"] = list(found_evidence)
    
    return parsed_case

# --- Test it out! ---
# combined_case = extract_case_metadata(my_parsed_case_from_step_1)
# print("Outcome:", combined_case["outcome"])
# print("Evidence Found:", combined_case["evidence_list"])