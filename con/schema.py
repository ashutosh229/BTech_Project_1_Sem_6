from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class CaseCON:
    """
    Standard Case Object Notation (CON) for the Legal Intelligence System.
    Strictly following the schema requested for Step 1.
    """
    case_id: str
    case_type: Optional[str] = "Criminal/Civil"
    parties: List[str] = field(default_factory=list)
    issues: List[str] = field(default_factory=list)
    claims: List[dict] = field(default_factory=list)
    administrative_actions: List[str] = field(default_factory=list)
    evidence_present: List[str] = field(default_factory=list)
    claim_outcomes: List[str] = field(default_factory=list)
    outcome: Optional[str] = "Unknown"

    def to_dict(self):
        return {
            "case_id": self.case_id,
            "case_type": self.case_type,
            "parties": self.parties,
            "issues": self.issues,
            "claims": self.claims,
            "administrative_actions": self.administrative_actions,
            "evidence_present": self.evidence_present,
            "claim_outcomes": self.claim_outcomes,
            "outcome": self.outcome
        }
