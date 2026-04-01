import os
import sys

# Ensure root is in path
sys.path.append(os.getcwd())

from con.schema import CaseCON
from pipelines.pipeline1_old_cases.evidence_extractor import extract_evidence
from pipelines.pipeline1_old_cases.parse_case_json import parse_real_case_json

def build_con(parsed_case):
    """
    Standard Logic Mapping for Case Object Notation (CON).
    Strictly following user Step 1 & 2 instructions.
    """
    # 1. Basic ID and Type
    case_id = parsed_case.get("case_id", "Unknown")
    
    # 2. Extract evidence using our existing logic for consistency
    all_text = " ".join([str(v) for v in parsed_case.values() if isinstance(v, str)])
    evidence_vec, _ = extract_evidence(all_text)
    
    # Human readable mapping
    CLUSTER_NAMES = {
        0: 'Medical/FSL Reports',
        1: 'Witness Testimony (PW)',
        2: 'Agreements & Contracts',
        3: 'Other Procedural Docs',
        4: 'FIR/Seizure/PM Reports',
        5: 'Property Deeds'
    }
    evidence_found = [CLUSTER_NAMES[i] for i, v in enumerate(evidence_vec) if v > 0]

    # 3. Handle Parties (Placeholder if not in parsed_case)
    parties = parsed_case.get("parties", [])
    if not parties and "appellant" in parsed_case:
        parties = [parsed_case["appellant"], parsed_case.get("respondent", "State")]

    # 4. Handle Issues and Claims (Draft extraction)
    issues = parsed_case.get("issues", [])
    claims = parsed_case.get("claims", [])
    
    # Simple semantic fallback for claims if empty
    if not claims and "primary_facts" in parsed_case:
        claims = [{"id": "c1", "text": parsed_case["primary_facts"][:200]}]

    # Create the CON object
    con = CaseCON(
        case_id=case_id,
        case_type="Criminal" if "ipc" in all_text.lower() else "Civil",
        parties=parties,
        issues=issues,
        claims=claims,
        administrative_actions=parsed_case.get("actions", []),
        evidence_present=evidence_found,
        claim_outcomes=parsed_case.get("claim_outcomes", []),
        outcome=parsed_case.get("outcome", "Unknown")
    )
    
    return con.to_dict()
