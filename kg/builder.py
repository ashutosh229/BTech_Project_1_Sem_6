import os
import json

class LegalKnowledgeGraph:
    """
    Simulates a Legal Knowledge Graph based on IPC statutory requirements.
    This provides the 'Ground Truth' for what evidence SHOULD exist by law.
    """
    
    # Mapping of Sections to statutory requirements (Evidence Types needed)
    # Based on Indian Evidence Act + IPC Ingredients
    SECTION_REQUIREMENTS = {
        "302": [  # Murder
            "postmortem_report",
            "eyewitness_testimony",
            "recovery_panchnama",
            "motive_proof",
            "weapon_recovery_report"
        ],
        "307": [  # Attempt to Murder
            "medical_certificate_injury",
            "witness_pw1",
            "weapon_seizure_memo",
            "intent_proof"
        ],
        "498A": [ # Matrimonial Cruelty
            "marriage_certificate",
            "panchnama",
            "witness_neighbors",
            "demand_evidence",
            "medical_report"
        ],
        "376": [  # Sexual Offense
            "medical_exam_report",
            "fsl_report",
            "victim_statement_164",
            "dna_report"
        ],
        "default": [
            "fir_report",
            "witness_testimony",
            "seizure_memo"
        ]
    }

    def get_required_evidence(self, section_number):
        """Returns a list of evidence clusters required by law for this section."""
        # Normalize section
        section = str(section_number).strip().lstrip("0")
        if section in self.SECTION_REQUIREMENTS:
            return self.SECTION_REQUIREMENTS[section]
        return self.SECTION_REQUIREMENTS["default"]

    def verify_evidence(self, section_number, current_evidence_set):
        """
        Compares current evidence against KG requirements.
        Returns missing required evidence.
        """
        required = set(self.get_required_evidence(section_number))
        # Map current evidence set (which are clusters like 'cluster_0') to readable names if needed
        # For simplicity, we assume the pipeline passes readable evidence names or we map them here
        missing = required - set(current_evidence_set)
        return list(missing)

if __name__ == "__main__":
    kg = LegalKnowledgeGraph()
    print("⚖️ KG Requirements for Murder (302):", kg.get_required_evidence("302"))
