import os
import sys

# Ensure root is in path
sys.path.append(os.getcwd())

from con.schema import CaseCON
from pipelines.pipeline1_old_cases.evidence_extractor import extract_evidence_features


def infer_case_type(text):
    text = (text or "").lower()
    category_tokens = {
        "Service": ["appointment", "posting", "promotion", "departmental", "disciplinary", "service matter", "selection list", "seniority"],
        "Matrimonial": ["divorce", "matrimonial", "alimony", "maintenance", "custody", "marriage", "cruelty", "husband", "wife"],
        "Property": ["property", "land", "sale deed", "title", "coparcener", "partition", "tenancy", "lease", "mortgage", "huf"],
        "Criminal": [" ipc ", " bns ", " fir", "charge sheet", "postmortem", "seizure", "prosecution", "accused", "complainant", "conviction"],
    }
    scores = {
        category: sum(1 for token in tokens if token in text)
        for category, tokens in category_tokens.items()
    }
    best_category = max(scores, key=scores.get)
    if scores[best_category] >= 2:
        return best_category
    return "Civil"


def build_con(parsed_case):
    """
    Standard Logic Mapping for Case Object Notation (CON).
    Strictly following user Step 1 & 2 instructions.
    """
    # 1. Basic ID and Type
    case_id = parsed_case.get("case_id", "Unknown")
    
    # 2. Extract evidence using our existing logic for consistency
    all_text = " ".join([str(v) for v in parsed_case.values() if isinstance(v, str)])
    evidence_features = extract_evidence_features(all_text)
    evidence_vec = evidence_features["coarse_vector"]
    
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
        case_type=infer_case_type(all_text),
        parties=parties,
        issues=issues,
        claims=claims,
        administrative_actions=parsed_case.get("actions", []),
        evidence_present=evidence_found,
        evidence_profile={
            "coarse_binary": dict(evidence_features["coarse_binary"]),
            "coarse_counts": dict(evidence_features["coarse_counts"]),
            "fine_binary": dict(evidence_features["fine_binary"]),
            "fine_counts": dict(evidence_features["fine_counts"]),
            "fine_matches": dict(evidence_features["fine_matches"]),
            "fine_labels": dict(evidence_features["fine_labels"]),
        },
        claim_outcomes=parsed_case.get("claim_outcomes", []),
        outcome=parsed_case.get("outcome", "Unknown")
    )
    
    return con.to_dict()
