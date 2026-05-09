import json
import os
import sys
import pandas as pd
import joblib

# Add current directory to path
sys.path.append(os.getcwd())

from pipelines.pipeline1_old_cases.parse_case_json import parse_real_case_json
from con_files.builder import build_con
from con_files.feature_builder import LegalFeatureBuilder

# Reasoning imports for Step 5, 6 & 7
from retrieval.search import retrieve_similar_cases
from models.missing_evidence.recommendation import find_missing_evidence
from models.contradiction.detect import detect_contradictions
from models.judgment.predict import DiscriminativeReasoningEngine

# Global predictor for LLM (singleton to avoid reloading embeddings)
_LLM_PREDICTOR = None

def get_llm_predictor():
    global _LLM_PREDICTOR
    if _LLM_PREDICTOR is None:
        from models.judgment.nyarag_groq_implementation import NyayaRAGPredictor, RAGContextBuilder, llm
        
        # Determine paths relative to project root
        base_dir = os.getcwd()
        emb_path = os.path.join(base_dir, "outputs", "shareable_legal_vectors.json")
        ana_path = os.path.join(base_dir, "outputs", "system_final_allahabad_2015_3099880.json")
        
        rag_builder = RAGContextBuilder(embeddings_path=emb_path, analysis_path=ana_path)
        _LLM_PREDICTOR = NyayaRAGPredictor(llm, rag_builder)
    return _LLM_PREDICTOR

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

    # 5. Final Inference Synthesis (XGBoost + Symbolic)
    engine = DiscriminativeReasoningEngine()
    ai_judgment = engine.run_inference(con, similar, missing, contradictions)

    # 6. Explanation Synthesis (Groq LLM-induced Reasoning)
    try:
        predictor = get_llm_predictor()
        
        # Extract meaningful facts for the LLM
        facts_text = con.get("facts", "")
        if not facts_text and con.get("claims"):
            facts_text = " ".join([c.get("text", "") for c in con.get("claims")])
        if not facts_text:
            facts_text = "Detailed facts not extracted into CON, refer to similar cases for context."

        llm_res = predictor.predict(
            case_facts=facts_text,
            similar_cases=similar,
            case_id=con.get("case_id", "unknown")
        )
        
        explanation = {
            "summary_narrative": llm_res.get("explanation", "Reasoning generation failed."),
            "logical_steps": [llm_res.get("explanation", "")],
            "fidelity_score": llm_res.get("confidence", 0.0),
            "prediction": llm_res.get("prediction", "UNKNOWN")
        }
    except Exception as e:
        print(f"⚠️ LLM Explanation failed: {e}")
        # Fallback to template if Groq fails
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
