import json
import os
import sys
import pandas as pd
import joblib

# Add current directory to path
sys.path.append(os.getcwd())

from pipelines.pipeline1_old_cases.parse_case_json import parse_real_case_json
from pipelines.pipeline1_old_cases.evidence_extractor import extract_evidence
from con.builder import build_con

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

        # 1. Map to Feature Space
        is_criminal = 1 if con_dict.get("case_type") == "Criminal" else 0
        conf_str = "50%" # Default
        
        # Pull stats from retrieval if available
        success_ratio = 0.5
        if similar_cases:
            outcomes = [c.get("outcome", "") for c in similar_cases]
            success_ratio = outcomes.count("Allowed/Success") / len(outcomes) if outcomes else 0.5

        # Feature Vector
        X_vals = pd.DataFrame([{
            "is_criminal": is_criminal,
            "evidence_present": len(con_dict.get("evidence_present", [])),
            "missing_evidence": len(missing),
            "contradiction_score": contradictions.get("contradiction_score", 0),
            "judgment_probability": success_ratio
        }])
        
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
    missing = find_missing_evidence(con, similar)
    contradictions = detect_contradictions(con)

    # 4. Final Inference Synthesis
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
