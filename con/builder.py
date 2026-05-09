import os
import sys

# Ensure root is in path
sys.path.append(os.getcwd())

from con.schema import CaseCON, CaseType, CaseOutcome, CanonicalEvidence, Claim, EvidenceProfile
from pipelines.pipeline1_old_cases.evidence_extractor import extract_evidence_features

def infer_case_type(text) -> CaseType:
    text = (text or "").lower()
    category_tokens = {
        CaseType.SERVICE: ["appointment", "posting", "promotion", "departmental", "disciplinary", "service matter", "selection list", "seniority"],
        CaseType.MATRIMONIAL: ["divorce", "matrimonial", "alimony", "maintenance", "custody", "marriage", "cruelty", "husband", "wife"],
        CaseType.PROPERTY: ["property", "land", "sale deed", "title", "coparcener", "partition", "tenancy", "lease", "mortgage", "huf"],
        CaseType.CRIMINAL: [" ipc ", " bns ", " fir", "charge sheet", "postmortem", "seizure", "prosecution", "accused", "complainant", "conviction"],
    }
    scores = {
        category: sum(1 for token in tokens if token in text)
        for category, tokens in category_tokens.items()
    }
    best_category = max(scores, key=scores.get)
    if scores[best_category] >= 2:
        return best_category
    return CaseType.CIVIL

def map_outcome(outcome_str: str) -> CaseOutcome:
    raw = str(outcome_str or "").lower()
    if "allowed" in raw or "success" in raw or "decreed" in raw:
        return CaseOutcome.ALLOWED
    if "dismissed" in raw or "rejected" in raw or "weak" in raw:
        return CaseOutcome.DISMISSED
    if "partial" in raw or "mixed" in raw:
        return CaseOutcome.PARTIAL
    return CaseOutcome.UNKNOWN

def build_con(parsed_case):
    """
    Standard Logic Mapping for Case Object Notation (CON v1).
    Strict, deterministic initialization mapping free text to safe numerical primitives.
    """
    case_id = parsed_case.get("case_id", "Unknown")
    
    # 1. Text Aggregation for Feature Extraction
    all_text = " ".join([str(v) for v in parsed_case.values() if isinstance(v, str)])
    
    # 2. Strong Evidence Matching
    evidence_features = extract_evidence_features(all_text)
    evidence_vec = evidence_features["coarse_vector"]
    
    CLUSTER_MAP = {
        0: CanonicalEvidence.MEDICAL,
        1: CanonicalEvidence.WITNESS,
        2: CanonicalEvidence.CONTRACTS,
        3: CanonicalEvidence.PROCEDURAL,
        4: CanonicalEvidence.MEMO,
        5: CanonicalEvidence.DEEDS
    }
    evidence_found = [CLUSTER_MAP[i] for i, v in enumerate(evidence_vec) if v > 0]
    
    # 3. Clean Feature Profiles
    ep = EvidenceProfile(
        coarse_binary=dict(evidence_features["coarse_binary"]),
        coarse_counts=dict(evidence_features["coarse_counts"]),
        fine_binary=dict(evidence_features["fine_binary"]),
        fine_counts=dict(evidence_features["fine_counts"]),
        fine_matches=dict(evidence_features["fine_matches"]),
        fine_labels=dict(evidence_features["fine_labels"]),
    )

    # 4. Enforce Strict Counts 
    parties = parsed_case.get("parties", [])
    if not parties and "appellant" in parsed_case:
        parties = [parsed_case.get("appellant"), parsed_case.get("respondent", "State")]
    
    issues = parsed_case.get("issues", [])
    actions = parsed_case.get("actions", [])

    # 5. Lock Down Claims Structure
    raw_claims = parsed_case.get("claims", [])
    mapped_claims = []
    if raw_claims:
        for idx, c in enumerate(raw_claims):
            if isinstance(c, dict) and "text" in c:
                mapped_claims.append(Claim(id=c.get("id", f"c{idx}"), text=c["text"]))
            else:
                mapped_claims.append(Claim(id=f"c{idx}", text=str(c)))
    elif "primary_facts" in parsed_case:
        mapped_claims.append(Claim(id="c0", text=str(parsed_case["primary_facts"])[:200]))

    # Combine into rigid CON representation
    con = CaseCON(
        case_id=case_id,
        case_type=infer_case_type(all_text),
        parties_count=len(parties),
        issues_count=len(issues),
        claims=mapped_claims,
        administrative_actions_count=len(actions),
        evidence_present=evidence_found,
        evidence_profile=ep,
        outcome=map_outcome(parsed_case.get("outcome", "Unknown"))
    )
    
    return con.to_dict()
