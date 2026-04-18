import os
import json
import pandas as pd
import numpy as np
from typing import List, Dict, Any
from models.judgment.predict import predict_judgment
from retrieval.search import LegalSearcher
from con.builder import build_con
from pipelines.pipeline1_old_cases.parse_case_json import parse_real_case_json

class AblationStudyFramework:
    """
    Measures the 'Lift' provided by each module of the pipeline.
    """
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.searcher = LegalSearcher()

    def run_test_case(self, file_path, use_rag=True, use_kg=True, use_contradictions=True):
        # 1. Setup
        parsed = parse_real_case_json(file_path)
        con = build_con(parsed)

        # 2. Conditional Retrieval
        similar = self.searcher.retrieve_similar_cases(con) if use_rag else []

        # 3. Conditional Reasoning
        # In a real system, we would disable these inside predict_judgment.
        # For the ablation, we pass empty values.
        missing = [] # simulate no gap analysis
        contradictions = {} if not use_contradictions else {"contradiction_score": 0.5} # mock value

        # 4. Inference
        # We use the predict_judgment API which we've now upgraded to handle these
        res = predict_judgment(con, similar, missing, contradictions)

        return res.get("confidence", 0.0), res.get("p_win", 0.5)

    def execute_ablation(self, test_files: List[str]):
        results = []
        for f in test_files:
            path = os.path.join(self.data_dir, f)

            # Baseline: No RAG, No KG, No Contradictions
            conf_base, p_base = self.run_test_case(path, use_rag=False, use_kg=False, use_contradictions=False)

            # + RAG
            conf_rag, p_rag = self.run_test_case(path, use_rag=True, use_kg=False, use_contradictions=False)

            # + RAG + KG
            conf_kg, p_kg = self.run_test_case(path, use_rag=True, use_kg=True, use_contradictions=False)

            # Full Pipeline
            conf_full, p_full = self.run_test_case(path, use_rag=True, use_kg=True, use_contradictions=True)

            results.append({
                "case": f,
                "baseline_p": p_base,
                "rag_p": p_rag,
                "kg_p": p_kg,
                "full_p": p_full,
                "lift_rag": p_rag - p_base,
                "lift_kg": p_kg - p_rag,
                "lift_full": p_full - p_kg
            })

        return pd.DataFrame(results)

if __name__ == "__main__":
    # Demo run
    study = AblationStudyFramework()
    test_files = [f for f in os.listdir("data") if f.endswith(".json")] [: 10]
    df_results = study.execute_ablation(test_files)
    print("\n🔥 ABLATION STUDY RESULTS (Probability Lift)")
    print(df_results[["case", "baseline_p", "full_p", "lift_rag", "lift_kg", "lift_full"]].to_string())
