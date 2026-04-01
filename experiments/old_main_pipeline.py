import os
import json
import numpy as np
import pandas as pd
import joblib
import faiss
from sentence_transformers import SentenceTransformer

# Internal Modules
try:
    from scrapers.knowledge_graph import LegalKnowledgeGraph
    from scrapers.contradiction_engine import ContradictionEngine
    from scrapers.evidence_extractor import extract_evidence
except ImportError:
    # If run directly from scrapers folder
    from knowledge_graph import LegalKnowledgeGraph
    from contradiction_engine import ContradictionEngine
    from evidence_extractor import extract_evidence

class LegalPipeline:
    """
    UNIFIED LEGAL INTELLIGENCE PIPELINE (STAGE 3 FUSION)
    Connects: KG (Legal Requirements) + RAG (Empirical Patterns) + NLI (Contradictions)
    """

    def __init__(self, model_path="/home/amaydixit11/Desktop/dev/Legal-Intelligence-System/results/outcome_predictor.joblib"):
        self.kg = LegalKnowledgeGraph()
        self.contradiction_engine = ContradictionEngine()
        
        # Load Predictor Model
        try:
            model_data = joblib.load(model_path)
            self.clf = model_data["model"]
            self.feature_names = model_data["feature_names"]
            self.cluster_names = model_data["cluster_mapping"]
            self.importances = dict(zip(self.feature_names, self.clf.feature_importances_))
        except:
            print("⚠️ Predictor model not found. Using zero-weights fallback.")
            self.clf = None
            self.feature_names = [f"cluster_{i}" for i in range(6)]
            self.importances = {f: 0 for f in self.feature_names}

        # Load FAISS Index for Retrieval
        self.embedder = SentenceTransformer('law-ai/InLegalBERT')
        self.index = faiss.read_index("/home/amaydixit11/Desktop/dev/Legal-Intelligence-System/results/legal_fact_index.faiss")
        
        with open("/home/amaydixit11/Desktop/dev/Legal-Intelligence-System/results/failed_cases_index.json", 'r') as f:
            self.weak_cases = json.load(f)

    def get_similar_cases(self, fact_text, k=5):
        """Retrieval Branch: Pure RAG / FAISS."""
        query_vector = self.embedder.encode([fact_text])[0].reshape(1, -1)
        distances, indices = self.index.search(query_vector.astype('float32'), k)
        
        # Mocking metadata retrieval (in production, use a SQLite/DuckDB index)
        similar_cases = []
        for i, idx in enumerate(indices[0]):
             # Simple identifier mock
             similar_cases.append({
                 "case_id": f"historical_case_{idx}",
                 "distance": float(distances[0][i]),
                 "outcome": "Dismissed" if idx % 3 == 0 else "Allowed"
             })
        return similar_cases

    def analyze_case(self, case_text, section="302"):
        """Main Hybrid Analysis Loop."""
        
        # 1. Extraction (CON generation placeholder)
        evidence_vector, raw_counts = extract_evidence(case_text)
        current_clusters = [f"cluster_{i}" for i, v in enumerate(evidence_vector) if v > 0]
        readable_evidence = [self.cluster_names.get(c, c) for c in current_clusters]

        # 2. Contradiction Branch (NLI/Symbolic)
        contradiction_results = self.contradiction_engine.analyze_contradictions(case_text)

        # 3. Missing Evidence Branch (KG + RAG Hybrid)
        # KG Check
        kg_missing = self.kg.verify_evidence(section, readable_evidence)
        
        # RAG Check (Similar cases patterns)
        similar_cases = self.get_similar_cases(case_text)
        
        # 4. Importance Logic (Gradient Boosting Weights)
        missing_ranked = []
        for item in kg_missing:
            # Map back to cluster for weight lookup
            target_cluster = "cluster_1" # Mock mapping
            score = self.importances.get(target_cluster, 0.1)
            missing_ranked.append({"type": item, "importance": score})
        
        # Sort missing evidence by model importance
        missing_ranked = sorted(missing_ranked, key=lambda x: x["importance"], reverse=True)

        # 5. Prediction Branch (Outcome Distribution)
        # Using the actual GBC model if loaded
        X_test = pd.DataFrame([evidence_vector], columns=self.feature_names)
        prob = self.clf.predict_proba(X_test)[0] if self.clf else [0.5, 0.5]
        
        # Calculate Completeness Score (Weighted presence)
        completeness = (np.dot(evidence_vector, list(self.importances.values())) / sum(self.importances.values())) * 100
        
        # Final Unified Output Contract
        return {
            "case_id": "QUERY_CASE_01",
            "statutory_section": section,
            
            "summary": {
                "completeness_score": f"{completeness:.1f}%",
                "contradiction_score": f"{contradiction_results['contradiction_score']:.2f}",
                "predicted_outcome": "Allowed" if prob[1] > 0.5 else "Dismissed",
                "prediction_confidence": f"{max(prob)*100:.1f}%"
            },
            
            "missing_evidence": missing_ranked,
            
            "contradictions": contradiction_results["found_contradictions"],
            
            "similar_cases": similar_cases,
            
            "importance_weights": self.importances
        }

if __name__ == "__main__":
    pipeline = LegalPipeline()
    sample_text = "Murder case (Section 302). Weapon recovery report exists but eyewitness PW1 statement inconsistent. Delayed FIR by 2 days."
    report = pipeline.analyze_case(sample_text, section="302")
    print(json.dumps(report, indent=2))
