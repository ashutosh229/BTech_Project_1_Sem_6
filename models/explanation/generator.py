import os
import json
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from models.judgment.predict import predict_judgment
from retrieval.search import LegalSearcher
from con.builder import build_con
from pipelines.pipeline1_old_cases.parse_case_json import parse_real_case_json
from models.kg.knowledge_engine import KnowledgeEngine

class GroundedExplanationGenerator:
    """
    Produces research-grade intelligence reports that synthesize:
    1. Base Prediction (ML)
    2. Structural Grounding (KG)
    3. Precedent Alignment (RAG)
    4. Counterfactual Lifts (Missing Evidence)
    """
    def __init__(self):
        self.kg_engine = KnowledgeEngine()
        self.searcher = LegalSearcher()

    def generate_report(self, result: Dict, con_dict: Dict, similar_cases: List[Dict]) -> str:
        # Extract core metrics
        prediction = result.get("prediction", "Unknown")
        confidence = result.get("confidence", 0.0)
        reasoning = result.get("reasoning", {})
        cf_analysis = result.get("counterfactuals", {})

        # 1. Header
        report = [
            "====================================================",
            "⚖️ JUDICIAL INTELLIGENCE REPORT (Grounded Reasoning)",
            "====================================================",
            f"FINAL PREDICTION: {prediction}",
            f"CONFIDENCE SCORE: {confidence*100:.1f}%",
            "----------------------------------------------------",
            "\n[1] LEGAL GROUNDING (Statutory Alignment)",
        ]

        # 2. KG Analysis
        detected_concepts = reasoning.get("detected_concepts", [])
        logic_path = reasoning.get("legal_logic", [])
        if detected_concepts:
            report.append(f"Detected Legal Concepts: {', '.join(detected_concepts)}")
            report.append("Statutory Logic Path:")
            for step in logic_path:
                report.append(f"  - {step}")
        else:
            report.append("No specific statutory concepts triggered.")

        # 3. Precedent Analysis
        report.append("\n[2] PRECEDENT ALIGNMENT (RAG)")
        prec_cons = reasoning.get("precedent_consistency", {})
        if prec_cons:
            report.append(f"Similarity to 'Winning' Precedents: {prec_cons.get('allowed', 0):.2f}")
            report.append(f"Similarity to 'Failed' Precedents: {prec_cons.get('dismissed', 0):.2f}")

            # Cite specific similar cases
            report.append("Key Analogous Cases:")
            for i, case in enumerate(similar_cases[:3]):
                outcome = case.get("outcome", "Unknown")
                dist = case.get("distance", 0.0)
                report.append(f"  {i+1}. {case['case_id']} | Outcome: {outcome} | Dist: {dist:.4f}")
        else:
            report.append("No precedent alignment data available.")

        # 4. Counterfactual Lift (The "What If" Analysis)
        report.append("\n[3] COUNTERFACTUAL IMPACT (Evidence Gaps)")
        if cf_analysis:
            # Find top 3 most impactful missing features
            sorted_cf = sorted(cf_analysis.items(), key=lambda x: x[1]["delta"], reverse=True)
            found_impact = False
            for feat, metrics in sorted_cf[:3]:
                if metrics["delta"] > 0.01:
                    found_impact = True
                    report.append(f"  - Adding {feat} would increase win probability by {metrics['lift_percent']}%")
            if not found_impact:
                report.append("  No single piece of missing evidence significantly flips the outcome.")
        else:
            report.append("Counterfactual analysis unavailable.")

        # 5. Synthesis
        report.append("\n[4] FINAL SYNTHESIS")
        if " la " in prediction.lower() or "Success" in prediction:
            report.append("The case is bolstered by strong statutory alignment and precedent consistency.")
        else:
            report.append("The case lacks critical evidentiary markers and aligns more closely with dismissed precedents.")

        report.append("====================================================")
        return "\n".join(report)

def generate_intelligence_report(con_dict, similar_cases, missing, contradictions):
    """API entry point for the report generator."""
    # Run the prediction first to get the data
    prediction_res = predict_judgment(con_dict, similar_cases, missing, contradictions)

    generator = GroundedExplanationGenerator()
    report = generator.generate_report(prediction_res, con_dict, similar_cases)

    return {
        "prediction_data": prediction_res,
        "text_report": report
    }
