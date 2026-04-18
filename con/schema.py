from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum

class CaseType(str, Enum):
    CRIMINAL = "Criminal"
    CIVIL = "Civil"
    SERVICE = "Service"
    MATRIMONIAL = "Matrimonial"
    PROPERTY = "Property"
    UNKNOWN = "Unknown"

class CaseOutcome(str, Enum):
    ALLOWED = "Allowed/Success"
    DISMISSED = "Dismissed/Weak"
    PARTIAL = "Partial/Mixed"
    UNKNOWN = "Unknown"

class CanonicalEvidence(str, Enum):
    MEDICAL = "Medical/FSL Reports"
    WITNESS = "Witness Testimony (PW)"
    CONTRACTS = "Agreements & Contracts"
    PROCEDURAL = "Other Procedural Docs"
    MEMO = "FIR/Seizure/PM Reports"
    DEEDS = "Property Deeds"

@dataclass
class Claim:
    id: str
    text: str

@dataclass
class EvidenceProfile:
    coarse_binary: Dict[str, float] = field(default_factory=dict)
    coarse_counts: Dict[str, float] = field(default_factory=dict)
    fine_binary: Dict[str, float] = field(default_factory=dict)
    fine_counts: Dict[str, float] = field(default_factory=dict)
    fine_matches: Dict[str, List[str]] = field(default_factory=dict)
    fine_labels: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self):
        return {
            "coarse_binary": self.coarse_binary,
            "coarse_counts": self.coarse_counts,
            "fine_binary": self.fine_binary,
            "fine_counts": self.fine_counts,
            "fine_matches": self.fine_matches,
            "fine_labels": self.fine_labels,
        }

@dataclass
class CaseCON:
    """
    Standard Case Object Notation (CON) for the Legal Intelligence System.
    v1: Strict, enumerative, deterministic schema without ambiguity.
    Removes raw text lists (like parties/issues) in favor of clean signal primitives.
    """
    case_id: str
    case_type: CaseType = CaseType.UNKNOWN
    parties_count: int = 0
    issues_count: int = 0
    claims: List[Claim] = field(default_factory=list)
    administrative_actions_count: int = 0
    evidence_present: List[CanonicalEvidence] = field(default_factory=list)
    evidence_profile: EvidenceProfile = field(default_factory=EvidenceProfile)
    outcome: CaseOutcome = CaseOutcome.UNKNOWN

    def to_dict(self):
        return {
            "case_id": self.case_id,
            "case_type": self.case_type.value if isinstance(self.case_type, Enum) else self.case_type,
            "parties_count": self.parties_count,
            "issues_count": self.issues_count,
            "claims": [{"id": c.id if hasattr(c, "id") else idx, "text": c.text if hasattr(c, "text") else str(c)} for idx, c in enumerate(self.claims)],
            "administrative_actions_count": self.administrative_actions_count,
            "evidence_present": [e.value if isinstance(e, Enum) else e for e in self.evidence_present],
            "evidence_profile": self.evidence_profile.to_dict() if hasattr(self.evidence_profile, "to_dict") else self.evidence_profile,
            "outcome": self.outcome.value if isinstance(self.outcome, Enum) else self.outcome
        }
