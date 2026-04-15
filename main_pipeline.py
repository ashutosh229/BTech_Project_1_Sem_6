import json
import os
import sys
import pandas as pd
import joblib

# Add current directory to path
sys.path.append(os.getcwd())

from pipelines.pipeline1_old_cases.parse_case_json import parse_real_case_json
from con.builder import build_con
from con.feature_builder import LegalFeatureBuilder

# Reasoning imports for Step 5, 6 & 7
from retrieval.search import retrieve_similar_cases
from models.missing_evidence.recommendation import find_missing_evidence
from models.contradiction.detect import detect_contradictions

class UnifiedInferenceEngine:
    """
    Step 9: Unified Inference Engine.
    Uses the trained XGBoost model to provide evidentiary-aware outcome forecasting.
    """
    def __init__(self, model_path="data/processed/judgment_model.joblib"):
        self.feature_builder = LegalFeatureBuilder()
        if os.path.exists(model_path):
            artifact = joblib.load(model_path)
            self.model = artifact["model"]
            self.features = artifact["features"]
            print(f"🧠 Unified Inference Engine Warm. Model loaded from {model_path}")
        else:
            self.model = None
            print("⚠️ No trained judgment model found. Predictive depth will be limited.")

    def run_inference(self, con_dict, similar_cases, missing, contradictions):
        """Predicts outcome probabilities based on synthesized features."""
        if not self.model:
             # Fallback to pure retrieval logic if no model trained
             from models.judgment.predict import predict_judgment
             return predict_judgment(con_dict, similar_cases)

        phi_dict = self.feature_builder.build_phi_dict(
            con_dict=con_dict,
            similar_cases=similar_cases,
            missing_evidence=missing,
            contradictions=contradictions,
        )
        
        # Enforce exact column order as training
        X_vals = pd.DataFrame([phi_dict])[self.features]
        
        # 2. Model Prediction
        probs = self.model.predict_proba(X_vals)[0]
        outcome = "Allowed/Success likely" if probs[1] > 0.5 else "Dismissed/Weak likely"
        confidence = probs[1] if probs[1] > 0.5 else probs[0]
        
        return {
            "prediction": outcome,
            "confidence": f"{confidence*100:.1f}%",
            "probabilities": {"allowed": float(probs[1]), "dismissed": float(probs[0])}
        }

def run_pipeline(file_path):
    """
    FINAL END-TO-END UNIFIED PIPELINE (STEP 9)
    RAW CASE → CON → RAG → MISSING EVIDENCE → CONTRADICTIONS → AI JUDGMENT.
    """
    # 1. Parse -> CON
    parsed = parse_real_case_json(file_path)
    con = build_con(parsed)

    # 2. Retrieval Intelligence
    from retrieval.search import retrieve_similar_cases
    similar = retrieve_similar_cases(con)

    # 3. Reasoning Intelligence
    contradictions = detect_contradictions(con)

    # 4. Build Φ-vector (needed for counterfactual importance in step 3b)
    feature_builder = LegalFeatureBuilder()
    phi_dict = feature_builder.build_phi_dict(con, similar, [], contradictions)

    # 3b. Missing Evidence (with Φ-vector for Level 3 counterfactual)
    missing = find_missing_evidence(con, similar, phi_dict=phi_dict)

    # 5. Final Inference Synthesis
    engine = UnifiedInferenceEngine()
    ai_judgment = engine.run_inference(con, similar, missing, contradictions)

    return {
        "con": con,
        "similar_cases": similar,
        "missing_evidence": missing,
        "contradictions": contradictions,
        "judgment_probability": ai_judgment
    }

if __name__ == "__main__":
    # Demo Run
    DATA_PATH = "data/allahabad_2015_3099880.json"
    if os.path.exists(DATA_PATH):
        result = run_pipeline(DATA_PATH)
        print("\n🔥 RESEARCH-GRADE UNIFIED OUTPUT 🏆")
        print("====================================")
        print(json.dumps(result, indent=2))
