import re
import os
import json

class ContradictionEngine:
    """
    Step 6: Symbolic Contradiction Detection.
    Implements light-weight checks for temporal and evidentiary mismatches.
    """

    def check_temporal_contradiction(self, case_text):
        """Simple rule for FIR delays without explanation."""
        if "delayed fir" in case_text.lower():
            return {
                "type": "temporal_mismatch",
                "severity": 0.8,
                "detail": "Factual claim indicates a delayed FIR, which often weakens prosecution logic."
            }
        return None

    def check_evidence_claim_mismatch(self, case_text, evidence_list):
        """Checks for mismatches between claims and evidence present."""
        contradictions = []
        
        # 1. Recovery Mismatch
        if "recovery" in case_text.lower() and "FIR/Seizure/PM Reports" not in evidence_list:
            contradictions.append({
                "type": "evidentiary_conflict",
                "severity": 0.9,
                "detail": "Claim mentioned weapon/item recovery, but no Seizure Memo/Panchnama was identified."
            })
            
        # 2. Witness Mismatch
        if "eyewitness" in case_text.lower() and "Witness Testimony (PW)" not in evidence_list:
             contradictions.append({
                "type": "procedural_gap",
                "severity": 0.7,
                "detail": "Claim relies on eyewitnesses, but no formal Witness Testimony (PW) was submitted."
            })

        return contradictions

    def analyze(self, con_dict):
        """Analyzes a CON dictionary for contradictions."""
        # Join all claims text for analysis
        case_text = " ".join([c.get("text", "") for c in con_dict.get("claims", [])])
        evidence_present = con_dict.get("evidence_present", [])
        
        results = []
        
        # Check Rules
        temporal = self.check_temporal_contradiction(case_text)
        if temporal: results.append(temporal)
        
        mismatches = self.check_evidence_claim_mismatch(case_text, evidence_present)
        results.extend(mismatches)
        
        # Calculate overall contradiction score
        score = sum([c["severity"] for c in results]) / 2.0 if results else 0
        
        return {
            "contradiction_score": min(score, 1.0),
            "found_contradictions": results
        }

def detect_contradictions(con_dict):
    engine = ContradictionEngine()
    return engine.analyze(con_dict)
