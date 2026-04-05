import json
import os
import sys
import pandas as pd
from tqdm import tqdm

# Ensure root is in path
sys.path.append(os.getcwd())

from pipelines.pipeline1_old_cases.parse_case_json import parse_real_case_json
from con.builder import build_con
from con.feature_builder import LegalFeatureBuilder
from retrieval.search import LegalSearcher
from models.missing_evidence.recommendation import find_missing_evidence
from models.contradiction.detect import detect_contradictions
from models.judgment.predict import predict_judgment

class FullSystemOrchestrator:
    """
    Step 9: Scalability & Performance Dashboard.
    Runs the entire system on 9,703 cases and generates a corpus summary.
    """
    def __init__(self, 
                 raw_dir="data", 
                 out_dir="data/results",
                 summary_path="data/processed/corpus_intelligence_summary.csv"):
        
        self.raw_dir = raw_dir
        self.out_dir = out_dir
        self.summary_path = summary_path
        os.makedirs(self.out_dir, exist_ok=True)
        
        # Load models once
        print("🚀 [1/3] Preparing Intelligence Engines...")
        self.searcher = LegalSearcher()
        self.feature_builder = LegalFeatureBuilder()
        print("✅ Models Warm.")

    def run_all(self, limit=None):
        """Processes all 9,703 cases."""
        files = [f for f in os.listdir(self.raw_dir) if f.endswith(".json")]
        files.sort()
        if limit is not None:
            files = files[:limit]
        
        print(f"🚀 [2/3] Processing {len(files)} cases with Unified Pipeline...")
        
        batch_results = []
        
        # Using tqdm for visual progress in terminal
        for filename in tqdm(files):
            path = os.path.join(self.raw_dir, filename)
            try:
                # 1. Pipeline Execution
                parsed = parse_real_case_json(path)
                con = build_con(parsed)
                similar = self.searcher.retrieve_similar_cases(con)
                missing = find_missing_evidence(con, similar)
                contradictions = detect_contradictions(con)
                judgment = predict_judgment(con, similar)
                phi_dict = self.feature_builder.build_phi_dict(con, similar, missing, contradictions)

                # 2. Extract Key Metrics for CSV
                record = {
                    "case_id": filename.replace(".json", ""),
                    "case_type": con["case_type"],
                    "true_outcome": con.get("outcome", "Unknown"),
                    "evidence_present": len(con["evidence_present"]),
                    "missing_evidence": len(missing),
                    "contradiction_score": contradictions["contradiction_score"],
                    "judgment_probability": float(judgment["confidence"].replace("%", "")) / 100.0,
                    "predicted_outcome": judgment["prediction"],
                }
                record.update(phi_dict)
                
                batch_results.append(record)
                
                # Checkpoint: Save summary CSV every 100 cases for real-time analytics
                if len(batch_results) % 100 == 0:
                    pd.DataFrame(batch_results).to_csv(self.summary_path, index=False)
                    # print(f"📍 Checkpoint: Saved {len(batch_results)} results to summary.")
                
            except Exception:
                continue

        # 3. Final Save
        print(f"🚀 [3/3] Generating Final Corpus Summary...")
        df = pd.DataFrame(batch_results)
        df.to_csv(self.summary_path, index=False)
        print(f"✅ CORPUS SUCCESS: {len(df)} cases analyzed.")
        print(f"💾 Summary saved to: {self.summary_path}")
        return df

if __name__ == "__main__":
    orchestrator = FullSystemOrchestrator()
    limit = os.environ.get("BATCH_LIMIT")
    orchestrator.run_all(limit=int(limit) if limit else None)
