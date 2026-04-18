import json
import joblib
import numpy as np
import pandas as pd
import os
from typing import List, Dict, Any, Tuple, Optional
from con.feature_builder import LegalFeatureBuilder
from models.kg.knowledge_engine import KnowledgeEngine

class DiscriminativeReasoningEngine:
    """
    Implements a multi-stage discriminative reasoning process inspired by ADAPT and VERDICT.
    Shift from 'Label Prediction' to 'Consistency Evaluation'.
    """
    def __init__(self, model_path=None):
        self.feature_builder = LegalFeatureBuilder()
        self.kg_engine = KnowledgeEngine()

        # Load the XGBoost model for the 'Probability' base
        paths = [
            model_path,
            'data/processed/judgment_model.joblib',
            'outputs/models/judgment_model.joblib'
        ]
        
        self.model = None
        for p in paths:
            if p and os.path.exists(p):
                try:
                    artifact = joblib.load(p)
                    self.model = artifact if not isinstance(artifact, dict) else artifact.get("model")
                    if self.model: break
                except Exception:
                    continue

    def _decompose_facts(self, con_dict: Dict) -> Dict:
        """
        Stage 1: Ask (Fact Decomposition).
        Breaks down the CON into structural legal elements.
        """
        return {
            "subject": {
                "is_professional": con_dict.get("case_type") in ["Service", "Property"],
                "type": con_dict.get("case_type", "Civil")
            },
            "behavior": {
                "evidence_density": len(con_dict.get("evidence_present", [])),
                "has_mandatory_evidence": False, # Calculated in alignment
            },
            "intent": {
                "conflict_score": 0.0 # To be filled by contradiction module
            }
        }

    def _calculate_consistency(self, phi_vec: np.ndarray, candidate_outcome: str, similar_cases: List[Dict]) -> float:
        """
        Stage 2: Discriminate (Consistency Evaluation).
        Measures how well the current case's Φ aligns with the 'winning' patterns of similar cases.
        """
        if not similar_cases:
            return 0.5

        # Filter cases that match the candidate outcome
        target_cases = [c for c in similar_cases if candidate_outcome.lower() in c.get("outcome", "").lower()]
        if not target_cases:
            return 0.1 # Very low consistency if no similar cases have this outcome

        # Fallback: use distance as a proxy for consistency if full vectors aren't passed
        avg_dist = np.mean([float(c.get("distance", 1.0)) for c in target_cases])
        consistency = 1.0 / (1.0 + avg_dist)
        return float(consistency)

    def run_inference(self, con_dict: Dict, similar_cases: List[Dict], missing: List[Dict], contradictions: Dict) -> Dict:
        """
        Final multi-stage pipeline:
        1. Base Prob (XGBoost)
        2. Structural Alignment (KG)
        3. Discriminative Consistency (Precedents)
        4. Final Synthesis
        """
        # --- 1. Base ML Probability ---
        phi_dict = self.feature_builder.build_phi_dict(con_dict, similar_cases, missing, contradictions)
        phi_vec = np.array([phi_dict.get(name, 0.0) for name in self.feature_builder.feature_names])

        p_win = 0.5
        method = "Heuristic"
        if self.model:
            X = phi_vec.reshape(1, -1)
            probs = self.model.predict_proba(X)[0]
            p_win = float(probs[1])
            method = "XGBoost + Discriminative Layer"

        # --- 2. KG / Symbolic Grounding ---
        symbolic_res = self.kg_engine.calculate_symbolic_score(phi_dict)
        sym_score = symbolic_res["symbolic_score"]

        # --- 3. Discriminative Consistency Check ---
        cons_allowed = self._calculate_consistency(phi_vec, "Allowed/Success", similar_cases)
        cons_dismissed = self._calculate_consistency(phi_vec, "Dismissed/Weak", similar_cases)

        # --- 4. Final Synthesis (Weighted Voting) ---
        # Probability is the anchor, KG and Consistency are the 'Judicial Review'
        final_score = (p_win * 0.5) + (sym_score * 0.2) + (cons_allowed * 0.3)

        prediction = "Allowed / Success Likely" if final_score > 0.5 else "Dismissed / High Risk"
        confidence = final_score if final_score > 0.5 else (1.0 - final_score)

        # --- 5. Counterfactual Integration ---
        cf_analysis = {}
        try:
            from models.missing_evidence.counterfactual import CounterfactualImportance
            cf_engine = CounterfactualImportance()
            if cf_engine.available:
                cf_analysis = cf_engine.compute(phi_dict)
        except Exception as e:
            cf_analysis = {"error": str(e)}

        return {
            "prediction": prediction,
            "confidence": round(confidence, 4),
            "p_win": round(p_win, 4),
            "final_score": round(final_score, 4),
            "method": method,
            "reasoning": {
                "base_probability": p_win,
                "symbolic_alignment": sym_score,
                "precedent_consistency": {
                    "allowed": cons_allowed,
                    "dismissed": cons_dismissed
                },
                "detected_concepts": symbolic_res["detected_concepts"],
                "legal_logic": symbolic_res["reasoning_path"]
            },
            "counterfactuals": cf_analysis,
            "phi_vector": phi_vec.tolist()
        }

def predict_judgment(con_dict, similar_cases, missing=None, contradictions=None):
    """Standard API entry point."""
    engine = DiscriminativeReasoningEngine()
    return engine.run_inference(con_dict, similar_cases, missing or [], contradictions or {})
