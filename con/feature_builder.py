import numpy as np
import pandas as pd

class LegalFeatureBuilder:
    """
    Step 10: Formal Research-Grade Representation Learning.
    Constructs a deterministic Phi(C, E, G, R) vector for ML training.
    Includes Option A: Retrieval-Weighted Outcome.
    """
    def __init__(self):
        self.feature_names = [
            # A. CONTEXT FEATURES
            "is_criminal",          # Binary (1: Criminal, 0: Civil)
            "num_claims",           # Complexity index
            "num_issues",           # Reasoning depth
            "num_parties",          # Case scale
            
            # B. EVIDENCE FEATURES (Multi-hot cluster)
            "ev_med_fsl", "ev_witness", "ev_contract", "ev_procedural", "ev_fir_seizure", "ev_deeds",
            "evidence_density",     # Ratio of clusters present
            
            # C. GAP ANALYSIS (Structural Weaknesses)
            "missing_count",        # Scalar count of recommended items
            "gap_importance_sum",  # Weighted importance of missing items
            
            # D. SYMBOLIC CONFLICT (Inconsistency)
            "conflict_count",       # Number of contradictions
            "conflict_score",       # Normalized symbolic penalty
            
            # E. LEARNED RETRIEVAL (The Deep Component)
            "rag_allowed_ratio",    # Mean success of top-k
            "rag_weighted_outcome", # Σ(sim_i * outcome_i) -> Attention over precedents
            "rag_similarity_mean"   # Average distance in vector space
        ]

    def build_phi(self, con_dict, similar_cases, missing_evidence, contradictions):
        """Synthesizes the 20-dimensional Phi vector."""
        
        # --- A. Context ---
        is_criminal = 1 if con_dict.get("case_type") == "Criminal" else 0
        num_claims = len(con_dict.get("claims", []))
        num_issues = len(con_dict.get("issues", []))
        num_parties = len(con_dict.get("parties", []))

        # --- B. Evidence ---
        evidence = set(con_dict.get("evidence_present", []))
        ev_v = [0] * 6
        EV_MAP = {'Medical/FSL Reports': 0, 'Witness Testimony (PW)': 1, 'Agreements & Contracts': 2, 
                  'Other Procedural Docs': 3, 'FIR/Seizure/PM Reports': 4, 'Property Deeds': 5}
        for e in evidence:
            if e in EV_MAP: ev_v[EV_MAP[e]] = 1
        ev_density = sum(ev_v) / 6.0

        # --- C. Gap ---
        missing_count = len(missing_evidence)
        gap_imp = 0.0
        try:
            gap_imp = sum([float(m.get("importance", "0").rstrip('%')) / 100.0 for m in missing_evidence])
        except: pass

        # --- D. Conflict ---
        conflict_count = len(contradictions.get("found_contradictions", []))
        conflict_score = float(contradictions.get("contradiction_score", 0.0))

        # --- E. Retrieval (Weighted Attention) ---
        if similar_cases:
            # rag_allowed_ratio
            outcomes = [1 if "Allowed" in str(c.get("outcome", "")) else 0 for c in similar_cases]
            allowed_ratio = sum(outcomes) / len(outcomes)
            
            # rag_weighted_outcome: Implementation of Option A
            # We use (1/distance) as the similarity weight
            similarities = [1.0 / (float(c.get("distance", 1.0)) + 1e-6) for c in similar_cases]
            total_sim = sum(similarities)
            weighted_outcome = sum([out * sim for out, sim in zip(outcomes, similarities)]) / total_sim
            
            sim_mean = np.mean([float(c.get("distance", 10.0)) for c in similar_cases])
        else:
            allowed_ratio = 0.5
            weighted_outcome = 0.5
            sim_mean = 15.0

        phi = [
            is_criminal, num_claims, num_issues, num_parties,
            *ev_v, ev_density,
            missing_count, gap_imp,
            conflict_count, conflict_score,
            allowed_ratio, weighted_outcome, sim_mean
        ]
        
        return np.array(phi), self.feature_names
