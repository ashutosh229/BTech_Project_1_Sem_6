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

from models.judgment.predict import DiscriminativeReasoningEngine

def run_pipeline(file_path):
    """
    FINAL END-TO-END UNIFIED PIPELINE (STEP 9)
    RAW CASE → CON → RAG → MISSING EVIDENCE → CONTRADICTIONS → AI JUDGMENT.
    """
    # 1. Parse -> CON
    parsed = parse_real_case_json(file_path)
    con = build_con(parsed)

    # 2. Retrieval Intelligence (Phase 1: Fact-Similar Diversification)
    from retrieval.search import retrieve_similar_cases
    similar = retrieve_similar_cases(con, strategy="fact-similar")

    # 3. Reasoning Intelligence
    contradictions = detect_contradictions(con)

    # 4. Build Φ-vector (needed for counterfactual importance in step 3b)
    feature_builder = LegalFeatureBuilder()
    phi_dict = feature_builder.build_phi_dict(con, similar, [], contradictions)

    # 3b. Missing Evidence (with Φ-vector for Level 3 counterfactual)
    missing = find_missing_evidence(con, similar, phi_dict=phi_dict)

    # 5. Final Inference Synthesis
    engine = DiscriminativeReasoningEngine()
    ai_judgment = engine.run_inference(con, similar, missing, contradictions)

    # 6. Explanation Synthesis (Level 3 Research Task)
    from models.judgment.explanation import JudgmentExplainer
    explainer = JudgmentExplainer()
    explanation = explainer.generate({"judgment_probability": ai_judgment})

    return {
        "con": con,
        "similar_cases": similar,
        "missing_evidence": missing,
        "contradictions": contradictions,
        "judgment_probability": ai_judgment,
        "explanation": explanation
    }

if __name__ == "__main__":
    # Demo Run
    DATA_PATH = "data/allahabad_2015_3099880.json"
    if os.path.exists(DATA_PATH):
        result = run_pipeline(DATA_PATH)
        print("\n🔥 RESEARCH-GRADE UNIFIED OUTPUT 🏆")
        print("====================================")
        
        # Display Summary
        jp = result["judgment_probability"]
        print(f"Prediction: {jp['prediction']}")
        print(f"Confidence: {jp['confidence']:.2f}")
        print(f"Method: {jp['method']}")
        
        if "reasoning" in jp:
            re = jp["reasoning"]
            dict_cons = re["precedent_consistency"]
            print(f"Precedent Consistency (Allowed): {dict_cons['allowed']:.4f}")
            print(f"Symbolic Alignment (KG): {re['symbolic_alignment']:.4f}")
            print(f"Detected Concepts: {', '.join(re['detected_concepts'])}")
            
        if "counterfactuals" in jp and jp["counterfactuals"]:
            cf = jp["counterfactuals"]
            # Find the best lift
            valid_cf = {k: v for k, v in cf.items() if isinstance(v, dict) and "delta" in v}
            if valid_cf:
                best_f = max(valid_cf.items(), key=lambda x: x[1]["delta"])
                print(f"Primary Evidentiary Pivot: {best_f[0]} (Lift: +{best_f[1].get('lift_percent', 0)}%)")
            
        print("\nFull Result Artifact saved to memory.")
