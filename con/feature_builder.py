import numpy as np
import pandas as pd

class LegalFeatureBuilder:
    """
    Step 10: Research-Grade Representation Learning.
    Constructs a high-dimensional feature vector Phi(C, E, G, R) 
    that unifies context, evidence, gaps, and retrieval.
    """
    def __init__(self):
        # We define a 20-dimensional feature space for the paper's ablation study
        self.feature_names = [
            # A. CONTEXT (phi_context)
            "is_criminal",          # Binary (1: Criminal, 0: Civil)
            "num_claims",           # Scalar Intensity
            "num_issues",           # Scalar Complexity
            "num_parties",          # Scalar Complexity
            "parties_density",      # Parties/Claims Ratio
            
            # B. EVIDENCE (phi_evidence)
            "evidence_density",     # (Found / Expected)
            "has_medical_fsl",      # Boolean Indicator
            "has_fir_seizure",      # Boolean Indicator
            "cluster_0", "cluster_1", "cluster_2", "cluster_3", "cluster_4", "cluster_5",
            
            # C. GAP ANALYSIS (phi_gap)
            "gap_count",            # Num Missing items
            "max_gap_confidence",   # Max confidence of missing items
            
            # D. CONFLICT ANALYSIS (phi_conflict)
            "conflict_count",       # Total symbolic contradictions
            "conflict_score",       # Normalized score
            
            # E. RETRIEVAL (phi_retrieval)
            "rag_allowed_ratio",    # Success statistics from top-k
            "rag_similarity_density" # Mean distance of precedents
        ]

    def build(self, con_dict, similar_cases, missing_evidence, contradictions):
        """
        Synthesizes modular intelligence into a single 20-D feature vector.
        """
        # --- A. CONTEXT ---
        is_criminal = 1 if con_dict.get("case_type") == "Criminal" else 0
        num_claims = len(con_dict.get("claims", []))
        num_issues = len(con_dict.get("issues", []))
        num_parties = len(con_dict.get("parties", []))
        parties_density = num_parties / (num_claims + 1) # Stability feature

        # --- B. EVIDENCE ---
        evidence = set(con_dict.get("evidence_present", []))
        clusters = [0] * 6
        CLUSTER_MAP = {
            'Medical/FSL Reports': 0,
            'Witness Testimony (PW)': 1,
            'Agreements & Contracts': 2,
            'Other Procedural Docs': 3,
            'FIR/Seizure/PM Reports': 4,
            'Property Deeds': 5
        }
        for e in evidence:
            if e in CLUSTER_MAP: clusters[CLUSTER_MAP[e]] = 1
        
        has_medical = clusters[0]
        has_fir = clusters[4]
        evidence_density = len(evidence) / 6.0

        # --- C. GAP ANALYSIS ---
        gap_count = len(missing_evidence)
        max_gap_conf = 0.0
        if missing_evidence:
              # "60.0%" -> 0.6
              try:
                  confs = [float(m.get("confidence_score", "0%").rstrip('%')) / 100.0 for m in missing_evidence]
                  max_gap_conf = max(confs)
              except: pass

        # --- D. CONFLICT ANALYSIS ---
        conflict_count = len(contradictions.get("found_contradictions", []))
        conflict_score = float(contradictions.get("contradiction_score", 0.0))

        # --- E. RETRIEVAL ---
        if similar_cases:
            outcomes = [c.get("outcome", "") for c in similar_cases]
            allowed_ratio = outcomes.count("Allowed/Success") / len(outcomes) if outcomes else 0.5
            similarity_density = np.mean([float(c.get("distance", 10.0)) for c in similar_cases])
        else:
            allowed_ratio = 0.5
            similarity_density = 15.0 # Penalty distance

        # Synthesize Final Phi Vector
        features = [
            is_criminal, num_claims, num_issues, num_parties, parties_density, 
            evidence_density, has_medical, has_fir, 
            clusters[0], clusters[1], clusters[2], clusters[3], clusters[4], clusters[5],
            gap_count, max_gap_conf,
            conflict_count, conflict_score,
            allowed_ratio, similarity_density
        ]
        
        return np.array(features), self.feature_names

if __name__ == "__main__":
    builder = LegalFeatureBuilder()
    print("Phi Vector Dimensions:", len(builder.feature_names))
    print("Features:", builder.feature_names)
