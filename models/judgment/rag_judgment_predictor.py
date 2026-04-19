"""
RAG-Enhanced Judgment Prediction Module (NYARAG-inspired Architecture)

Implements retrieval-augmented reasoning for judicial outcome forecasting:
1. Embed query case using shareable legal vectors
2. Retrieve similar precedents (top-k neighbors from corpus)
3. Augment decision features with retrieved cases' attributes
4. Generate outcome prediction with causal reasoning chains
"""

import json
import joblib
import numpy as np
import pandas as pd
import os
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path

# Local imports
from con_files.feature_builder import LegalFeatureBuilder, outcome_to_binary
from retrieval.search import LegalSearcher, extract_case_outcome
from models.kg.knowledge_engine import KnowledgeEngine

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


class RAGJudgmentPredictor:
    """
    NYARAG-inspired Retrieval-Augmented Generation for Judgment Prediction.
    
    Architecture:
    - Level 1: Dense Legal Embeddings (InLegalBERT on shareable vectors)
    - Level 2: Precedent-Aware Feature Augmentation (Retrieved case features)
    - Level 3: Ensemble Reasoning (XGBoost + Symbolic KG + RAG consensus)
    """

    def __init__(self, 
                 model_path: Optional[str] = None,
                 embeddings_path: Optional[str] = None,
                 k_neighbors: int = 10,
                 use_embedding_augmentation: bool = True):
        """
        Initialize RAG-enhanced judgment predictor.
        
        Args:
            model_path: Path to trained XGBoost model
            embeddings_path: Path to shareable legal vectors (optional)
            k_neighbors: Number of similar precedents to retrieve
            use_embedding_augmentation: Whether to augment features with retrieval data
        """
        self.feature_builder = LegalFeatureBuilder()
        self.searcher = LegalSearcher()
        self.kg_engine = KnowledgeEngine()
        self.k_neighbors = k_neighbors
        self.use_embedding_augmentation = use_embedding_augmentation

        # Load trained XGBoost model
        paths = [
            model_path,
            os.path.join(BASE_DIR, 'data/processed/judgment_model.joblib'),
            os.path.join(BASE_DIR, 'outputs/models/judgment_model.joblib')
        ]
        
        self.model = None
        for p in paths:
            if p and os.path.exists(p):
                try:
                    artifact = joblib.load(p)
                    self.model = artifact if not isinstance(artifact, dict) else artifact.get("model")
                    if self.model:
                        print(f"✓ Loaded XGBoost model from {p}")
                        break
                except Exception as e:
                    print(f"⚠ Failed to load model from {p}: {e}")
                    continue

        if not self.model:
            print("⚠ No trained model found. Will use retrieval-based reasoning only.")

        # Load embedding augmentation data if available
        self.embedding_cache = {}
        if embeddings_path and os.path.exists(embeddings_path):
            self._load_embedding_cache(embeddings_path)

    def _load_embedding_cache(self, path: str):
        """Load shareable legal embeddings for augmentation."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Handle nested structure if present
                if isinstance(data, dict) and 'embeddings' in data:
                    self.embedding_cache = data['embeddings']
                else:
                    self.embedding_cache = data
            print(f"✓ Loaded {len(self.embedding_cache)} embedding vectors")
        except Exception as e:
            print(f"⚠ Could not load embeddings: {e}")

    def _retrieve_precedents(self, con_dict: Dict, query_text: Optional[str] = None) -> List[Dict]:
        """
        Retrieve top-k similar cases (precedents) from corpus.
        
        Args:
            con_dict: Case Object Notation dictionary
            query_text: Optional custom query text
            
        Returns:
            List of similar precedent cases with metadata
        """
        if not self.searcher.index:
            print("⚠ FAISS index not available. Skipping retrieval.")
            return []

        try:
            # Generate retrieval query from CON or use provided text
            from retrieval.search import extract_case_query_text
            query = query_text or extract_case_query_text(con_dict)
            
            # Retrieve similar cases
            results = self.searcher.search(query, top_k=self.k_neighbors)
            
            # Enrich results with outcome labels
            enriched_results = []
            for result in results:
                case_id = result.get("case_id")
                if case_id in self.searcher.case_outcomes:
                    result["outcome"] = self.searcher.case_outcomes[case_id]
                enriched_results.append(result)
            
            return enriched_results
        except Exception as e:
            print(f"⚠ Retrieval failed: {e}")
            return []

    def _calculate_rag_consensus(self, similar_cases: List[Dict]) -> Dict:
        """
        Calculate consensus prediction from retrieved precedents.
        Uses outcome distribution + similarity weighting.
        
        Returns:
            Dict with allowed_score, dismissed_score, confidence
        """
        if not similar_cases:
            return {
                "allowed_score": 0.5,
                "dismissed_score": 0.5,
                "confidence": 0.0,
                "precedent_count": 0
            }

        # Calculate similarity-weighted outcome distribution
        allowed_weight = 0.0
        dismissed_weight = 0.0
        total_weight = 0.0

        for case in similar_cases:
            distance = float(case.get("distance", 1.0) or 1.0)
            similarity = 1.0 / (distance + 1e-6)  # Inverse distance as similarity
            total_weight += similarity

            outcome = case.get("outcome", "Unknown")
            if "Allowed/Success" in str(outcome):
                allowed_weight += similarity
            elif "Dismissed/Weak" in str(outcome):
                dismissed_weight += similarity

        # Normalize to probabilities
        if total_weight > 0:
            allowed_score = allowed_weight / total_weight
            dismissed_score = dismissed_weight / total_weight
        else:
            allowed_score = dismissed_score = 0.5

        # Confidence is based on precedent agreement
        max_score = max(allowed_score, dismissed_score)
        confidence = abs(allowed_score - dismissed_score)

        return {
            "allowed_score": float(allowed_score),
            "dismissed_score": float(dismissed_score),
            "confidence": float(confidence),
            "precedent_count": len(similar_cases),
            "dominant_outcome": "Allowed/Success" if allowed_score > 0.5 else "Dismissed/Weak"
        }

    def _extract_rag_reasoning_chain(self, similar_cases: List[Dict]) -> Dict:
        """
        Extract symbolic reasoning chains from retrieved precedents.
        
        Returns:
            Dict with causal reasoning patterns from precedents
        """
        reasoning_chains = {
            "successful_patterns": {},
            "dismissal_patterns": {},
            "evidence_emphasis": {},
            "legal_principles": []
        }

        if not similar_cases:
            return reasoning_chains

        for case in similar_cases[:5]:  # Analyze top 5 for reasoning
            outcome = case.get("outcome", "Unknown")
            evidence = case.get("evidence_profile", {})
            
            if "Allowed/Success" in str(outcome):
                for ev_type, count in evidence.items():
                    reasoning_chains["successful_patterns"][ev_type] = \
                        reasoning_chains["successful_patterns"].get(ev_type, 0) + (count or 0)
            elif "Dismissed/Weak" in str(outcome):
                for ev_type, count in evidence.items():
                    reasoning_chains["dismissal_patterns"][ev_type] = \
                        reasoning_chains["dismissal_patterns"].get(ev_type, 0) + (count or 0)

        return reasoning_chains

    def _build_augmented_phi(self, con_dict: Dict, similar_cases: List[Dict], 
                            missing: List[Dict], contradictions: Dict) -> np.ndarray:
        """
        Build augmented Phi-vector incorporating RAG information.
        
        Strategy:
        1. Start with base Phi (Context, Evidence, Gap, Conflict)
        2. Add RAG consensus scores
        3. Weight by precedent similarity
        """
        # Get base Phi features
        phi_dict = self.feature_builder.build_phi_dict(
            con_dict, similar_cases, missing, contradictions
        )

        # Add RAG consensus features
        rag_consensus = self._calculate_rag_consensus(similar_cases)
        phi_dict.update({
            "rag_allowed_consensus": rag_consensus["allowed_score"],
            "rag_dismissed_consensus": rag_consensus["dismissed_score"],
            "rag_precedent_confidence": rag_consensus["confidence"],
            "rag_precedent_count": rag_consensus["precedent_count"] / max(self.k_neighbors, 1)
        })

        # Convert to array in canonical order
        phi_vec = np.array([
            phi_dict.get(name, 0.0) 
            for name in self.feature_builder.feature_names
        ])

        return phi_vec, phi_dict

    def predict(self, con_dict: Dict, 
                similar_cases: Optional[List[Dict]] = None,
                missing_evidence: Optional[List[Dict]] = None,
                contradictions: Optional[Dict] = None,
                return_breakdown: bool = True) -> Dict:
        """
        Predict judgment outcome using RAG-enhanced reasoning.
        
        Args:
            con_dict: Case Object Notation
            similar_cases: Pre-retrieved similar cases (if None, will retrieve via FAISS)
            missing_evidence: Missing evidence analysis
            contradictions: Contradiction detection results
            return_breakdown: Include detailed reasoning breakdown
            
        Returns:
            Prediction dict with:
            - prediction: "Allowed/Success" or "Dismissed/Weak"
            - confidence: Confidence score [0-1]
            - rag_contribution: RAG weight in final decision
            - reasoning: Detailed breakdown of reasoning
        """
        missing_evidence = missing_evidence or []
        contradictions = contradictions or {}

        # Retrieve precedents if not provided
        if similar_cases is None:
            similar_cases = self._retrieve_precedents(con_dict)
            if not similar_cases:
                print(f"⚠ No precedents retrieved. Using feature-based reasoning only.")

        # Build augmented Phi vector with RAG info
        phi_vec, phi_dict = self._build_augmented_phi(
            con_dict, similar_cases, missing_evidence, contradictions
        )

        # === LEVEL 1: ML-based Prediction ===
        ml_prediction = {"score": 0.5, "confidence": 0.0, "method": "No model"}
        if self.model:
            try:
                X = phi_vec.reshape(1, -1)
                probs = self.model.predict_proba(X)[0]
                ml_prediction = {
                    "score": float(probs[1]),  # P(Allowed)
                    "confidence": float(abs(probs[1] - probs[0])),
                    "method": "XGBoost Classifier"
                }
            except Exception as e:
                print(f"⚠ ML prediction failed: {e}")

        # === LEVEL 2: RAG Consensus Prediction ===
        rag_consensus = self._calculate_rag_consensus(similar_cases)
        rag_prediction = {
            "score": rag_consensus["allowed_score"],
            "confidence": rag_consensus["confidence"],
            "method": "RAG Precedent Consensus"
        }

        # === LEVEL 3: Symbolic Knowledge Graph ===
        symbolic_score = 0.5
        try:
            sym_res = self.kg_engine.calculate_symbolic_score(phi_dict)
            symbolic_score = float(sym_res.get("symbolic_score", 0.5))
        except Exception as e:
            print(f"⚠ KG prediction failed: {e}")

        # === FINAL SYNTHESIS: Weighted Ensemble ===
        # RAG consensus is heavily weighted when we have good precedents
        rag_weight = min(0.4, 0.04 * rag_consensus["precedent_count"])  # Up to 40%
        ml_weight = 0.4  # ML model is primary
        kg_weight = 0.2  # KG provides symbolic grounding

        final_score = (
            ml_prediction["score"] * ml_weight +
            rag_prediction["score"] * rag_weight +
            symbolic_score * kg_weight
        )

        # Normalize if we had to skip RAG
        if rag_weight < 0.1:
            final_score = (ml_prediction["score"] * 0.6 + symbolic_score * 0.4)

        predicted_outcome = "Allowed/Success" if final_score > 0.5 else "Dismissed/Weak"
        confidence = final_score if final_score > 0.5 else (1.0 - final_score)

        # === Build Response ===
        response = {
            "prediction": predicted_outcome,
            "confidence": round(confidence, 4),
            "score": round(final_score, 4),
            "method": "RAG-Enhanced Judgment Predictor (NYARAG-inspired)"
        }

        if return_breakdown:
            response.update({
                "reasoning": {
                    "ml_prediction": {
                        "score": round(ml_prediction["score"], 4),
                        "confidence": round(ml_prediction["confidence"], 4),
                        "method": ml_prediction["method"],
                        "weight": ml_weight
                    },
                    "rag_consensus": {
                        "allowed_score": round(rag_prediction["score"], 4),
                        "dismissed_score": round(1.0 - rag_prediction["score"], 4),
                        "confidence": round(rag_prediction["confidence"], 4),
                        "precedent_count": rag_consensus["precedent_count"],
                        "method": rag_prediction["method"],
                        "weight": rag_weight
                    },
                    "symbolic_alignment": {
                        "score": round(symbolic_score, 4),
                        "weight": kg_weight
                    },
                    "ensemble_weights": {
                        "ml": ml_weight,
                        "rag": rag_weight,
                        "kg": kg_weight
                    }
                },
                "precedent_analysis": {
                    "retrieved_count": len(similar_cases),
                    "dominant_outcome": rag_consensus.get("dominant_outcome", "Unknown"),
                    "reasoning_chain": self._extract_rag_reasoning_chain(similar_cases)
                },
                "phi_vector_summary": {
                    "context_density": sum([
                        phi_dict.get("is_criminal", 0),
                        phi_dict.get("is_service", 0),
                        phi_dict.get("is_property", 0),
                    ]),
                    "evidence_density": phi_dict.get("evidence_density", 0.0),
                    "gap_severity": phi_dict.get("gap_importance_sum", 0.0),
                    "conflict_severity": phi_dict.get("conflict_score", 0.0)
                }
            })

        return response


def predict_with_rag(con_dict: Dict, 
                     similar_cases: Optional[List[Dict]] = None,
                     missing_evidence: Optional[List[Dict]] = None,
                     contradictions: Optional[Dict] = None,
                     k_neighbors: int = 10) -> Dict:
    """
    Convenience function for RAG-enhanced judgment prediction.
    
    Usage:
        from models.judgment.rag_judgment_predictor import predict_with_rag
        
        result = predict_with_rag(
            con_dict=my_case,
            missing_evidence=gaps,
            contradictions=contradicts
        )
        print(result["prediction"])
        print(result["reasoning"]["rag_consensus"])
    """
    predictor = RAGJudgmentPredictor(k_neighbors=k_neighbors)
    return predictor.predict(
        con_dict=con_dict,
        similar_cases=similar_cases,
        missing_evidence=missing_evidence,
        contradictions=contradictions,
        return_breakdown=True
    )
