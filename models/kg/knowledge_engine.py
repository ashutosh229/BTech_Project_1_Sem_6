from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set

class EvidenceRequirement(Enum):
    MANDATORY = "Mandatory"
    RECOMMENDED = "Recommended"
    SUPPORTING = "Supporting"

@dataclass
class LegalConcept:
    name: str
    description: str
    related_statutes: List[str] = field(default_factory=list)
    impact_weight: float = 1.0

class KnowledgeEngine:
    """
    Step 4: Legal Knowledge (KG) Layer.
    Provides symbolic legal reasoning by mapping cases to high-level legal concepts
    and statutory requirements.
    """
    
    def __init__(self):
        # A real KG would use a graph DB (Neo4j). We simulate with conceptual maps.
        self.concepts = {
            "Cruelty": LegalConcept(
                "Cruelty", 
                "Wilful conduct likely to drive the woman to suicide or cause grave injury.",
                ["498A IPC", "306 IPC"],
                1.5
            ),
            "Dowry Demand": LegalConcept(
                "Dowry Demand",
                "Demand for property or valuable security in connection with marriage.",
                ["304B IPC", "DP Act Sec 3"],
                2.0
            ),
            "Bail Eligibility": LegalConcept(
                "Bail Eligibility",
                "The right to temporary release pending trial based on the gravity of offense.",
                ["437 CrPC", "438 CrPC", "439 CrPC"],
                1.2
            ),
            "Natural Justice": LegalConcept(
                "Natural Justice",
                "Fair play in action; Audi alteram partem (hear the other side).",
                ["Constitution Art 14", "Constitution Art 21"],
                1.0
            )
        }
        
        # Statutory Impact Map (Historical success correlation for symbols)
        self.statute_impacts = {
            "304B IPC": {"type": "Burden of Proof", "shift": -0.2, "logic": "Reverse onus of proof on accused."},
            "498A IPC": {"type": "Substantive", "shift": -0.1, "logic": "Subjective interpretation of cruelty."},
            "439 CrPC": {"type": "Discretionary", "shift": 0.1, "logic": "High Court's wide powers for relief."},
            "Constitution Art 21": {"type": "Fundamental", "shift": 0.3, "logic": "Protection of life and personal liberty."}
        }

    def infer_concepts(self, phi_dict: Dict) -> List[Dict]:
        """
        Maps the technical Φ-vector back to high-level legal concepts.
        """
        detected = []
        # is_matrimonial implies Cruelty/Dowry concepts
        if phi_dict.get("is_matrimonial", 0) > 0.5:
            detected.append(self.concepts["Cruelty"])
            detected.append(self.concepts["Dowry Demand"])
            
        # is_criminal implies Bail concepts
        if phi_dict.get("is_criminal", 0) > 0.5:
            detected.append(self.concepts["Bail Eligibility"])
            
        # ev_procedural mentions likely trigger Natural Justice
        if phi_dict.get("ev_procedural", 0) > 0.5:
            detected.append(self.concepts["Natural Justice"])
            
        return [{"name": c.name, "weight": c.impact_weight, "statutes": c.related_statutes} for c in detected]

    def get_statutory_requirements(self, case_type: str) -> List[Dict]:
        """
        Returns the mandatory evidence requirements for a given case type.
        """
        # Research-grade domain modeling for Evidence Requirements
        if case_type == "Criminal":
            return [
                {"name": "Medical Report", "type": EvidenceRequirement.MANDATORY.value, "desc": "Antemortem injury verification"},
                {"name": "FIR copy", "type": EvidenceRequirement.MANDATORY.value, "desc": "Formal registration of crime"},
                {"name": "Independent Witness", "type": EvidenceRequirement.RECOMMENDED.value, "desc": "Non-relative corroboration"}
            ]
        elif case_type == "Property":
            return [
                {"name": "Sale Deed / Title", "type": EvidenceRequirement.MANDATORY.value, "desc": "Ownership proof"},
                {"name": "Site Plan", "type": EvidenceRequirement.RECOMMENDED.value, "desc": "Boundary clarity"},
                {"name": "Possession Record", "type": EvidenceRequirement.SUPPORTING.value, "desc": "Usage proof"}
            ]
        return []

    def calculate_symbolic_score(self, phi_dict: Dict) -> Dict:
        """
        Returns a symbolic 'Legal Soundness' score based on KG alignment.
        """
        detected_concepts = self.infer_concepts(phi_dict)
        score = 0.5
        logic_steps = []
        
        for item in detected_concepts:
            # Aggregate statutory shifts
            for stat in item["statutes"]:
                part = stat.split()[0] # e.g. '304B'
                for k, v in self.statute_impacts.items():
                    if k.startswith(part):
                        score += v["shift"]
                        logic_steps.append(v["logic"])
                        
        score = max(0.1, min(0.95, score))
        
        return {
            "symbolic_score": round(score, 4),
            "detected_concepts": [c["name"] for c in detected_concepts],
            "reasoning_path": list(set(logic_steps))
        }
