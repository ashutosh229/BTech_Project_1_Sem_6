import os
import json

class EvidenceRecommender:
    """
    Step 5: Hybrid Missing Evidence Analysis (RAG Branch).
    Compares query case against 'Success Siblings' retrieved by RAG.
    """
    def __init__(self, con_data_dir="data/con/"):
        self.con_data_dir = con_data_dir

    def recommend(self, con_dict, similar_cases):
        """Identifies gaps between current CON and success patterns."""
        if not similar_cases: return []

        current_evidence = set(con_dict.get("evidence_present", []))
        
        # 1. Gather all evidence from successful siblings
        success_patterns = []
        for case in similar_cases:
            # Only learn from success patterns
            if "Success" in case.get("outcome", ""):
                 # Check if we have the CON for this historical case
                 # (Mock: using a set of common winners to simulate)
                 winners_patterns = [
                     ["Medical/FSL Reports", "Witness Testimony (PW)", "FIR/Seizure/PM Reports"],
                     ["Agreements & Contracts", "Property Deeds"],
                     ["Witness Testimony (PW)", "Other Procedural Docs"]
                 ]
                 import random
                 success_patterns.append(random.choice(winners_patterns))
        
        if not success_patterns:
            return []

        # 2. Heuristic Gap Analysis: What do multiple winners have that I don't?
        # Flatten and count frequencies
        all_success_evidence = [item for sublist in success_patterns for item in sublist]
        from collections import Counter
        counts = Counter(all_success_evidence)
        
        missing = []
        for evidence_type, frequency in counts.most_common():
            if evidence_type not in current_evidence:
                # Priority is how frequently this was found in successful similar cases
                priority = frequency / len(success_patterns)
                missing.append({
                    "type": evidence_type,
                    "confidence_score": f"{priority*100:.1f}%",
                    "reason": "Commonly present in successful precedents of this case type."
                })
        
        return missing

def find_missing_evidence(con_dict, similar_cases):
    recommender = EvidenceRecommender()
    return recommender.recommend(con_dict, similar_cases)
