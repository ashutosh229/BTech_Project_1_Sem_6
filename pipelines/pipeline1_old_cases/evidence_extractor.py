import re
from collections import OrderedDict

# Coarse, backward-compatible evidence space used by the existing pipeline.
COARSE_CLUSTER_LABELS = OrderedDict({
    "medical_fsl": "Medical/FSL Reports",
    "witness_pw": "Witness Testimony (PW)",
    "contracts": "Agreements & Contracts",
    "procedural": "Other Procedural Docs",
    "fir_seizure_pm": "FIR/Seizure/PM Reports",
    "deeds": "Property Deeds",
})

# Fine-grained evidence space for the upgraded missing-evidence model.
# These patterns are intentionally mixed across criminal, civil, and quasi-civil
# matters so the model has more expressivity than the original 6-cluster setup.
FINE_GRAINED_EVIDENCE_PATTERNS = OrderedDict({
    "postmortem_report": r"\b(post\s?mortem|autopsy|pm report|postmortem report)\b",
    "inquest_report": r"\b(inquest report|inquest panchnama|inquest)\b",
    "medical_report": r"\b(medical report|mlc|medico legal|injury report|treatment record)\b",
    "forensic_report": r"\b(fsl|forensic report|chemical examiner|serology report|dna report)\b",
    "seizure_memo": r"\b(seizure memo|recovery memo|mahazar|spot panchnama|panchnama)\b",
    "site_plan": r"\b(site plan|rough sketch|spot map)\b",
    "fir": r"\b(fir|first information report)\b",
    "charge_sheet": r"\b(charge sheet|chargesheet|final report)\b",
    "complaint_petition": r"\b(complaint petition|written complaint|complaint case)\b",
    "legal_notice": r"\b(legal notice|demand notice|statutory notice|notice dated)\b",
    "banking_record": r"\b(bank statement|account statement|ledger account|passbook|cheque return memo|return memo)\b",
    "digital_record": r"\b(cdr|call detail record|mobile location|tower location|electronic record|email printout|whatsapp chat|cctv footage|video recording)\b",
    "witness_testimony_pw": r"\b(statement of pw|testimony of pw|deposed as pw|deposed by pw|witness pw|eyewitness)\b",
    "independent_witness": r"\b(independent witness|public witness|neighbour witness)\b",
    "dying_declaration": r"\b(dying declaration)\b",
    "confession": r"\b(confession|extra judicial confession)\b",
    "expert_opinion": r"\b(expert opinion|handwriting expert|fingerprint expert|valuation report|survey report)\b",
    "agreement_contract": r"\b(agreement|contract|mou|memorandum of understanding|lease deed|rent agreement)\b",
    "receipt_invoice": r"\b(receipt|invoice|bill|voucher|cash memo)\b",
    "sale_deed": r"\b(sale deed|registered sale deed)\b",
    "gift_deed": r"\b(gift deed|settlement deed)\b",
    "mortgage_deed": r"\b(mortgage deed|hypothecation deed)\b",
    "title_record": r"\b(khatauni|khasra|jamabandi|mutation|patta|revenue record|record of rights)\b",
    "will_probate": r"\b(will|last will and testament|probate|codicil)\b",
    "photographic_material": r"\b(photograph|photo exhibit|video clip|video recording|cctv footage)\b",
    "exhibit_reference": r"\b(exhibit|ex\.|exhibit no\.)\b",
})

FINE_TO_COARSE = {
    "postmortem_report": "medical_fsl",
    "inquest_report": "fir_seizure_pm",
    "medical_report": "medical_fsl",
    "forensic_report": "medical_fsl",
    "seizure_memo": "fir_seizure_pm",
    "site_plan": "procedural",
    "fir": "fir_seizure_pm",
    "charge_sheet": "procedural",
    "complaint_petition": "procedural",
    "legal_notice": "procedural",
    "banking_record": "contracts",
    "digital_record": "procedural",
    "witness_testimony_pw": "witness_pw",
    "independent_witness": "witness_pw",
    "dying_declaration": "witness_pw",
    "confession": "medical_fsl",
    "expert_opinion": "medical_fsl",
    "agreement_contract": "contracts",
    "receipt_invoice": "contracts",
    "sale_deed": "deeds",
    "gift_deed": "deeds",
    "mortgage_deed": "deeds",
    "title_record": "deeds",
    "will_probate": "deeds",
    "photographic_material": "procedural",
    "exhibit_reference": "procedural",
}

FINE_LABELS = {
    "postmortem_report": "Postmortem Report",
    "inquest_report": "Inquest Report",
    "medical_report": "Medical Report",
    "forensic_report": "Forensic/FSL Report",
    "seizure_memo": "Seizure / Recovery Memo",
    "site_plan": "Site Plan / Spot Map",
    "fir": "FIR",
    "charge_sheet": "Charge Sheet / Final Report",
    "complaint_petition": "Complaint Petition",
    "legal_notice": "Legal / Demand Notice",
    "banking_record": "Banking / Ledger Record",
    "digital_record": "Digital / Electronic Record",
    "witness_testimony_pw": "PW / Eyewitness Testimony",
    "independent_witness": "Independent Witness Testimony",
    "dying_declaration": "Dying Declaration",
    "confession": "Confession",
    "expert_opinion": "Expert Opinion / Technical Report",
    "agreement_contract": "Agreement / Contract",
    "receipt_invoice": "Receipt / Invoice / Bill",
    "sale_deed": "Sale Deed",
    "gift_deed": "Gift / Settlement Deed",
    "mortgage_deed": "Mortgage / Hypothecation Deed",
    "title_record": "Revenue / Title Record",
    "will_probate": "Will / Probate Record",
    "photographic_material": "Photographic / Video Material",
    "exhibit_reference": "Exhibit / Procedural Reference",
}


def _normalize_text(text):
    text = text or ""
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text


def extract_fine_grained_evidence(text):
    """
    Returns a rich evidence profile:
    - binary and count features over fine-grained evidence types
    - matched surface forms for auditing / future clustering
    """
    normalized = _normalize_text(text)
    binary = OrderedDict()
    counts = OrderedDict()
    matches = OrderedDict()

    for feature_name, pattern in FINE_GRAINED_EVIDENCE_PATTERNS.items():
        found = re.findall(pattern, normalized)
        flat = []
        for item in found:
            flat.append(item[0] if isinstance(item, tuple) else item)
        binary[feature_name] = 1 if flat else 0
        counts[feature_name] = len(flat)
        matches[feature_name] = sorted(set(flat))

    return {
        "binary": binary,
        "counts": counts,
        "matches": matches,
        "labels": {k: FINE_LABELS[k] for k in FINE_GRAINED_EVIDENCE_PATTERNS},
    }


def extract_evidence_features(text):
    """
    Returns both fine-grained and coarse evidence views for the same case.
    This is the preferred interface for new modules.
    """
    fine = extract_fine_grained_evidence(text)

    coarse_binary = OrderedDict((key, 0) for key in COARSE_CLUSTER_LABELS)
    coarse_counts = OrderedDict((key, 0) for key in COARSE_CLUSTER_LABELS)

    for fine_name, present in fine["binary"].items():
        coarse_key = FINE_TO_COARSE[fine_name]
        coarse_binary[coarse_key] = max(coarse_binary[coarse_key], present)
        coarse_counts[coarse_key] += fine["counts"][fine_name]

    coarse_vector = [coarse_binary[key] for key in COARSE_CLUSTER_LABELS]

    return {
        "coarse_vector": coarse_vector,
        "coarse_binary": coarse_binary,
        "coarse_counts": coarse_counts,
        "coarse_labels": dict(COARSE_CLUSTER_LABELS),
        "fine_binary": fine["binary"],
        "fine_counts": fine["counts"],
        "fine_matches": fine["matches"],
        "fine_labels": fine["labels"],
    }


def extract_evidence(text):
    """
    Backward-compatible wrapper.
    Returns the historical 6-D vector plus total matches.
    """
    features = extract_evidence_features(text)
    total_matches = int(sum(features["fine_counts"].values()))
    return features["coarse_vector"], {"matches": total_matches}


def extract_case_metadata(parsed_case):
    """Legacy wrapper for backward compatibility."""
    all_text = " ".join([str(v) for v in parsed_case.values() if isinstance(v, str)])
    features = extract_evidence_features(all_text)
    parsed_case["evidence_vector"] = features["coarse_vector"]
    parsed_case["evidence_profile"] = {
        "coarse_binary": dict(features["coarse_binary"]),
        "fine_binary": dict(features["fine_binary"]),
        "fine_matches": dict(features["fine_matches"]),
    }
    return parsed_case


if __name__ == "__main__":
    test_text = (
        "The postmortem report, seizure memo, CCTV footage and witness PW statements "
        "were filed along with the sale deed and legal notice."
    )
    print(extract_evidence_features(test_text))
