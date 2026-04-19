"""
Integration Example: Using RAG-Enhanced Judgment Prediction in main_pipeline.py

This script demonstrates how to integrate the new NYARAG judgment predictor
into your existing pipeline while maintaining backward compatibility.
"""

import json
import os
from typing import Dict, Optional

# Existing system imports
from con_files.builder import LegalCaseBuilder
from con_files.feature_builder import outcome_to_binary
from retrieval.search import LegalSearcher, extract_case_outcome, extract_case_query_text

# New RAG prediction imports
from models.judgment.rag_judgment_predictor import RAGJudgmentPredictor, predict_with_rag
from models.missing_evidence.diagnostics import missing_evidence_diagnostic
from models.contradiction.detect import detect_contradictions
from models.missing_evidence.recommendation import recommend_missing_evidence


class IntegratedJudgmentPipeline:
    """
    Drop-in replacement for single-case judgment prediction.
    Seamlessly uses RAG when available, falls back to traditional methods.
    """

    def __init__(self, use_rag: bool = True, k_neighbors: int = 10, verbose: bool = True):
        """
        Initialize integrated pipeline.
        
        Args:
            use_rag: Use RAG-enhanced prediction (requires FAISS index)
            k_neighbors: Number of precedents to retrieve
            verbose: Print reasoning steps
        """
        self.use_rag = use_rag
        self.k_neighbors = k_neighbors
        self.verbose = verbose
        
        # Initialize builders and searchers
        self.case_builder = LegalCaseBuilder()
        self.searcher = LegalSearcher()
        
        # Initialize RAG predictor if requested
        self.rag_predictor = None
        if use_rag:
            try:
                self.rag_predictor = RAGJudgmentPredictor(k_neighbors=k_neighbors)
                if verbose:
                    print("✓ RAG-Enhanced Judgment Predictor initialized")
            except Exception as e:
                print(f"⚠ RAG predictor unavailable: {e}")
                print("  Falling back to traditional prediction...")

    def run(self, case_json_path: str, 
            include_evidence_analysis: bool = True,
            include_contradiction_check: bool = True,
            return_reasoning: bool = True) -> Dict:
        """
        Main inference pipeline: Load → Analyze → Predict
        
        Args:
            case_json_path: Path to raw case JSON
            include_evidence_analysis: Analyze missing evidence gaps
            include_contradiction_check: Detect narrative contradictions
            return_reasoning: Include detailed reasoning breakdown
            
        Returns:
            Structured judgment prediction with reasoning
        """
        
        if self.verbose:
            print("\n" + "="*70)
            print("⚖️  INTEGRATED JUDGMENT PREDICTION PIPELINE")
            print("="*70)

        # Step 1: Load and parse case
        if self.verbose:
            print(f"\n[1] Loading case: {os.path.basename(case_json_path)}")
        
        try:
            with open(case_json_path, 'r', encoding='utf-8') as f:
                raw_case = json.load(f)
        except Exception as e:
            return {"error": f"Failed to load case: {e}"}

        # Convert to CON (Case Object Notation)
        con_dict = self.case_builder.build(raw_case)
        case_id = con_dict.get("case_id", "Unknown")
        
        if self.verbose:
            print(f"    ✓ Case ID: {case_id}")
            print(f"    ✓ Type: {con_dict.get('case_type', 'Unknown')}")
            print(f"    ✓ Claims: {len(con_dict.get('claims', []))}")

        # Step 2: Analysis modules (optional)
        missing_evidence = []
        contradictions = {}
        
        if include_evidence_analysis:
            if self.verbose:
                print(f"\n[2] Analyzing missing evidence...")
            try:
                query_text = extract_case_query_text(con_dict)
                missing_evidence = recommend_missing_evidence(con_dict, query_text)
                if self.verbose and missing_evidence:
                    print(f"    ✓ Found {len(missing_evidence)} critical gaps")
            except Exception as e:
                if self.verbose:
                    print(f"    ⚠ Gap analysis unavailable: {e}")

        if include_contradiction_check:
            if self.verbose:
                print(f"\n[3] Detecting contradictions...")
            try:
                contradictions = detect_contradictions(con_dict)
                if self.verbose:
                    conflict_count = len(contradictions.get("found_contradictions", []))
                    print(f"    ✓ Analysis complete ({conflict_count} contradictions)")
            except Exception as e:
                if self.verbose:
                    print(f"    ⚠ Contradiction detection unavailable: {e}")

        # Step 3: Judgment Prediction
        if self.verbose:
            if self.use_rag and self.rag_predictor:
                print(f"\n[4] Running RAG-Enhanced Judgment Prediction...")
            else:
                print(f"\n[4] Running Traditional Judgment Prediction...")

        result = self._predict(con_dict, missing_evidence, contradictions)
        
        # Step 4: Format output
        if return_reasoning:
            output = self._format_output(con_dict, result)
        else:
            output = {
                "case_id": case_id,
                "prediction": result.get("prediction"),
                "confidence": result.get("confidence"),
                "score": result.get("score")
            }

        if self.verbose:
            print(f"\n    ✓ {result['prediction']} (confidence: {result['confidence']:.2%})")
            print("="*70)

        return output

    def _predict(self, con_dict: Dict, missing_evidence: list, 
                 contradictions: Dict) -> Dict:
        """
        Core prediction logic with RAG fallback.
        """
        
        if self.use_rag and self.rag_predictor:
            # Use RAG-enhanced prediction
            return predict_with_rag(
                con_dict=con_dict,
                missing_evidence=missing_evidence,
                contradictions=contradictions,
                k_neighbors=self.k_neighbors
            )
        else:
            # Fallback: Traditional feature-based prediction
            from models.judgment.predict import predict_judgment
            return predict_judgment(
                con_dict=con_dict,
                similar_cases=[],  # Would need to retrieve these
                missing=missing_evidence,
                contradictions=contradictions
            )

    def _format_output(self, con_dict: Dict, prediction: Dict) -> Dict:
        """
        Format prediction into structured output.
        """
        output = {
            "case_id": con_dict.get("case_id"),
            "case_type": con_dict.get("case_type"),
            "prediction": prediction.get("prediction"),
            "confidence": prediction.get("confidence"),
            "score": prediction.get("score"),
            "method": prediction.get("method"),
        }

        # Include reasoning if available
        if "reasoning" in prediction:
            output["reasoning"] = {
                "ensemble_components": {
                    "ml": {
                        "score": prediction["reasoning"]["ml_prediction"]["score"],
                        "weight": prediction["reasoning"]["ensemble_weights"]["ml"]
                    },
                    "rag": {
                        "allowed_score": prediction["reasoning"]["rag_consensus"]["allowed_score"],
                        "precedent_count": prediction["reasoning"]["rag_consensus"]["precedent_count"],
                        "weight": prediction["reasoning"]["ensemble_weights"]["rag"]
                    },
                    "kg": {
                        "score": prediction["reasoning"]["symbolic_alignment"]["score"],
                        "weight": prediction["reasoning"]["ensemble_weights"]["kg"]
                    }
                },
                "phi_vector_profile": prediction["reasoning"].get("phi_vector_summary", {}),
                "precedent_analysis": prediction.get("precedent_analysis", {})
            }

        return output


# Example usage patterns
def example_1_simple_prediction():
    """Simple single case prediction."""
    print("\n" + "="*70)
    print("Example 1: Simple Single-Case Prediction")
    print("="*70)
    
    pipeline = IntegratedJudgmentPipeline(use_rag=True, verbose=True)
    result = pipeline.run(
        case_json_path="data/sample_cases/case_123.json",
        include_evidence_analysis=True,
        include_contradiction_check=True
    )
    
    print("\n📋 Result:")
    print(json.dumps(result, indent=2))


def example_2_batch_processing():
    """Process multiple cases in a directory."""
    print("\n" + "="*70)
    print("Example 2: Batch Processing")
    print("="*70)
    
    import glob
    from pathlib import Path
    import pandas as pd
    
    pipeline = IntegratedJudgmentPipeline(use_rag=True, verbose=False)
    
    # Find all case files
    case_dir = "data/sample_cases"
    case_files = glob.glob(os.path.join(case_dir, "*.json"))
    
    results = []
    for i, case_file in enumerate(case_files, 1):
        print(f"[{i}/{len(case_files)}] Processing {os.path.basename(case_file)}...", end=" ")
        
        result = pipeline.run(
            case_json_path=case_file,
            include_evidence_analysis=False,  # Skip for speed
            return_reasoning=False
        )
        
        if "error" not in result:
            results.append(result)
            print(f"✓ {result['prediction']}")
        else:
            print(f"❌ {result['error']}")
    
    # Create summary dataframe
    df = pd.DataFrame(results)
    print(f"\n📊 Summary:")
    print(f"  Total: {len(df)}")
    print(f"  Allowed: {(df['prediction'] == 'Allowed/Success').sum()}")
    print(f"  Dismissed: {(df['prediction'] == 'Dismissed/Weak').sum()}")
    print(f"  Avg Confidence: {df['confidence'].mean():.2%}")
    
    return df


def example_3_comparison_rag_vs_traditional():
    """Compare RAG-enhanced vs traditional prediction."""
    print("\n" + "="*70)
    print("Example 3: RAG vs Traditional Prediction Comparison")
    print("="*70)
    
    case_path = "data/sample_cases/case_123.json"

    # Prediction with RAG
    print("\n🔍 RAG-Enhanced Prediction (with NYARAG):")
    pipeline_rag = IntegratedJudgmentPipeline(use_rag=True, verbose=True)
    result_rag = pipeline_rag.run(case_path, return_reasoning=True)

    # Prediction without RAG
    print("\n\n🔍 Traditional Prediction (ML+KG only):")
    pipeline_traditional = IntegratedJudgmentPipeline(use_rag=False, verbose=True)
    result_traditional = pipeline_traditional.run(case_path, return_reasoning=False)

    # Comparison
    print("\n" + "="*70)
    print("📊 COMPARISON RESULTS")
    print("="*70)
    print(f"\nRAG Prediction:")
    print(f"  → {result_rag['prediction']}")
    print(f"  → Confidence: {result_rag['confidence']:.2%}")
    
    print(f"\nTraditional Prediction:")
    print(f"  → {result_traditional['prediction']}")
    print(f"  → Confidence: {result_traditional['confidence']:.2%}")
    
    if result_rag['reasoning']:
        rag_info = result_rag['reasoning']['ensemble_components']['rag']
        print(f"\nRAG Component Details:")
        print(f"  → Precedents Retrieved: {rag_info['precedent_count']}")
        print(f"  → Allowed Precedent Ratio: {rag_info['allowed_score']:.2%}")
        print(f"  → RAG Weight in Ensemble: {rag_info['weight']:.1%}")


def example_4_production_deployment():
    """Production-ready inference with caching and error handling."""
    print("\n" + "="*70)
    print("Example 4: Production Deployment Pattern")
    print("="*70)
    
    from functools import lru_cache
    import time
    
    # Cache predictions to avoid re-computing
    @lru_cache(maxsize=1000)
    def cached_predict(case_path: str) -> Dict:
        pipeline = IntegratedJudgmentPipeline(use_rag=True, verbose=False)
        return pipeline.run(case_path, include_evidence_analysis=False)
    
    # Simulate API request handler
    def handle_prediction_request(case_path: str, timeout_ms: int = 1000) -> Dict:
        """Production request handler with timeout."""
        try:
            start = time.time()
            result = cached_predict(case_path)
            latency_ms = (time.time() - start) * 1000
            
            if latency_ms > timeout_ms:
                print(f"⚠ Slow query ({latency_ms:.0f}ms > {timeout_ms}ms)")
            
            return {
                "status": "success",
                "data": result,
                "latency_ms": latency_ms
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "fallback_available": True
            }
    
    # Test request
    case_path = "data/sample_cases/case_123.json"
    response = handle_prediction_request(case_path)
    print(json.dumps(response, indent=2, default=str))


if __name__ == "__main__":
    import sys
    
    examples = {
        "1": ("Simple Prediction", example_1_simple_prediction),
        "2": ("Batch Processing", example_2_batch_processing),
        "3": ("RAG vs Traditional", example_3_comparison_rag_vs_traditional),
        "4": ("Production Deployment", example_4_production_deployment),
    }
    
    if len(sys.argv) > 1 and sys.argv[1] in examples:
        _, func = examples[sys.argv[1]]
        func()
    else:
        print("RAG Judgment Prediction Integration Examples")
        print("=" * 70)
        print("\nUsage: python models/judgment/rag_integration_example.py <example_id>")
        print("\nAvailable examples:")
        for id, (name, _) in examples.items():
            print(f"  {id}: {name}")
        print("\nExample: python models/judgment/rag_integration_example.py 1")
