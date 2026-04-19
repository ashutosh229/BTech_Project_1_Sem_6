"""
NYARAG Judgment Prediction Demo

Demonstrates the new RAG-enhanced judgment prediction architecture:
1. Load case data with shareable embeddings
2. Retrieve similar precedents using FAISS + InLegalBERT
3. Generate judgment prediction with causal reasoning chains
4. Compare RAG-only vs ML-only vs Ensemble reasoning
"""

import json
import argparse
import pandas as pd
import os
from pathlib import Path
from typing import Dict, List, Optional

# Local imports
from con_files.builder import LegalCaseBuilder
from models.judgment.rag_judgment_predictor import RAGJudgmentPredictor, predict_with_rag
from models.missing_evidence.diagnostics import missing_evidence_diagnostic
from models.contradiction.detect import detect_contradictions
from retrieval.search import extract_case_query_text


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class RAGJudgmentDemo:
    """Interactive demo of RAG-enhanced judgment prediction."""

    def __init__(self, k_neighbors: int = 10):
        """Initialize demo with RAG predictor."""
        self.predictor = RAGJudgmentPredictor(k_neighbors=k_neighbors)
        self.case_builder = LegalCaseBuilder()
        
    def load_case_from_json(self, json_path: str) -> Dict:
        """Load raw case JSON and convert to CON."""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
            
            # Convert to CON using the builder
            con_dict = self.case_builder.build(raw_data)
            return con_dict
        except Exception as e:
            print(f"❌ Failed to load case: {e}")
            return None

    def predict_case(self, case_path: str, analyze_gaps: bool = True, 
                    analyze_contradictions: bool = True, verbose: bool = True) -> Dict:
        """
        End-to-end prediction for a single case.
        
        Args:
            case_path: Path to raw case JSON
            analyze_gaps: Include missing evidence analysis
            analyze_contradictions: Include contradiction detection
            verbose: Print detailed reasoning
            
        Returns:
            Complete prediction with reasoning and evidence analysis
        """
        print("\n" + "="*70)
        print("🏛️  NYARAG JUDGMENT PREDICTION SYSTEM")
        print("="*70)

        # Step 1: Load case
        print(f"\n[1] Loading case from: {case_path}")
        con_dict = self.load_case_from_json(case_path)
        if not con_dict:
            return None

        case_id = con_dict.get("case_id", "Unknown")
        case_type = con_dict.get("case_type", "Unknown")
        print(f"    ✓ Loaded case: {case_id}")
        print(f"    ✓ Case type: {case_type}")
        print(f"    ✓ Claims: {len(con_dict.get('claims', []))}")
        print(f"    ✓ Issues: {len(con_dict.get('issues', []))}")

        # Step 2: Missing evidence analysis (optional)
        missing_evidence = []
        if analyze_gaps:
            print(f"\n[2] Analyzing missing evidence...")
            try:
                from models.missing_evidence.recommendation import recommend_missing_evidence
                query_text = extract_case_query_text(con_dict)
                missing_evidence = recommend_missing_evidence(con_dict, query_text)
                if missing_evidence:
                    print(f"    ✓ Found {len(missing_evidence)} critical gaps")
                    for gap in missing_evidence[:3]:
                        print(f"      - {gap.get('evidence_type', '?')}: {gap.get('confidence', '?')}")
                else:
                    print(f"    ✓ No critical gaps detected")
            except Exception as e:
                print(f"    ⚠ Gap analysis unavailable: {e}")
        else:
            print(f"\n[2] Skipping missing evidence analysis")

        # Step 3: Contradiction detection (optional)
        contradictions = {}
        if analyze_contradictions:
            print(f"\n[3] Detecting contradictions...")
            try:
                contradictions = detect_contradictions(con_dict)
                conflict_count = len(contradictions.get("found_contradictions", []))
                if conflict_count > 0:
                    print(f"    ✓ Found {conflict_count} contradictions")
                else:
                    print(f"    ✓ No major contradictions detected")
            except Exception as e:
                print(f"    ⚠ Contradiction detection unavailable: {e}")
                contradictions = {}
        else:
            print(f"\n[3] Skipping contradiction detection")

        # Step 4: RAG Judgment Prediction
        print(f"\n[4] Running RAG-Enhanced Judgment Prediction...")
        prediction = predict_with_rag(
            con_dict=con_dict,
            missing_evidence=missing_evidence,
            contradictions=contradictions,
            k_neighbors=self.predictor.k_neighbors
        )

        # Step 5: Display results
        print(f"\n" + "="*70)
        print(f"PREDICTION RESULT")
        print("="*70)
        print(f"\n🎯 Outcome: {prediction['prediction']}")
        print(f"   Confidence: {prediction['confidence']:.2%}")
        print(f"   Score: {prediction['score']:.4f}")
        print(f"\n📊 Reasoning Breakdown:")
        
        if "reasoning" in prediction:
            reasoning = prediction["reasoning"]
            
            # ML Component
            ml = reasoning.get("ml_prediction", {})
            print(f"\n   🤖 ML Predictor (weight: {reasoning['ensemble_weights']['ml']:.1%})")
            print(f"      Score: {ml.get('score', 'N/A')}")
            print(f"      Confidence: {ml.get('confidence', 'N/A')}")
            print(f"      Method: {ml.get('method', 'N/A')}")
            
            # RAG Component
            rag = reasoning.get("rag_consensus", {})
            print(f"\n   📚 RAG Precedent Consensus (weight: {reasoning['ensemble_weights']['rag']:.1%})")
            print(f"      Allowed Score: {rag.get('allowed_score', 'N/A'):.4f}")
            print(f"      Dismissed Score: {rag.get('dismissed_score', 'N/A'):.4f}")
            print(f"      Precedent Count: {rag.get('precedent_count', 0)}")
            print(f"      Confidence: {rag.get('confidence', 'N/A'):.4f}")
            
            # KG Component
            kg = reasoning.get("symbolic_alignment", {})
            print(f"\n   ⚖️  Knowledge Graph Alignment (weight: {reasoning['ensemble_weights']['kg']:.1%})")
            print(f"      Score: {kg.get('score', 'N/A'):.4f}")
            
            # Phi Vector Analysis
            phi = reasoning.get("phi_vector_summary", {})
            print(f"\n   📈 Case Feature Profile (Phi-Vector):")
            print(f"      Context Density: {phi.get('context_density', 0)}/3")
            print(f"      Evidence Density: {phi.get('evidence_density', 0):.2%}")
            print(f"      Gap Severity: {phi.get('gap_severity', 0):.2f}")
            print(f"      Conflict Severity: {phi.get('conflict_severity', 0):.2f}")

        print(f"\n" + "="*70)
        
        if verbose and "precedent_analysis" in prediction:
            precedent = prediction["precedent_analysis"]
            print(f"\n📋 PRECEDENT ANALYSIS")
            print("="*70)
            print(f"Retrieved Cases: {precedent.get('retrieved_count', 0)}")
            print(f"Dominant Outcome: {precedent.get('dominant_outcome', 'Unknown')}")
            
            if precedent.get("reasoning_chain"):
                chains = precedent["reasoning_chain"]
                print(f"\nSuccessful Case Patterns:")
                for pattern, count in chains.get("successful_patterns", {}).items():
                    if count > 0:
                        print(f"  • {pattern}: {count}")
                
                print(f"\nDismissal Case Patterns:")
                for pattern, count in chains.get("dismissal_patterns", {}).items():
                    if count > 0:
                        print(f"  • {pattern}: {count}")

        return prediction

    def batch_predict(self, case_dir: str, output_file: Optional[str] = None) -> pd.DataFrame:
        """
        Run predictions on multiple cases in a directory.
        
        Args:
            case_dir: Directory containing case JSON files
            output_file: Optional CSV file to save results
            
        Returns:
            DataFrame with predictions for all cases
        """
        case_files = list(Path(case_dir).glob("*.json"))
        results = []

        print(f"\n🔄 Batch Prediction Mode")
        print(f"📁 Processing {len(case_files)} cases from {case_dir}")
        print("="*70)

        for i, case_file in enumerate(case_files, 1):
            print(f"\n[{i}/{len(case_files)}] Processing: {case_file.name}")
            
            try:
                con_dict = self.load_case_from_json(str(case_file))
                if not con_dict:
                    continue
                
                prediction = predict_with_rag(
                    con_dict=con_dict,
                    k_neighbors=self.predictor.k_neighbors
                )
                
                # Extract summary data
                result = {
                    "case_id": con_dict.get("case_id", "Unknown"),
                    "case_type": con_dict.get("case_type", "Unknown"),
                    "prediction": prediction["prediction"],
                    "confidence": prediction["confidence"],
                    "score": prediction["score"],
                    "method": prediction["method"]
                }
                
                if "reasoning" in prediction:
                    result["ml_score"] = prediction["reasoning"]["ml_prediction"]["score"]
                    result["rag_score"] = prediction["reasoning"]["rag_consensus"]["allowed_score"]
                    result["precedent_count"] = prediction["reasoning"]["rag_consensus"]["precedent_count"]
                
                results.append(result)
                print(f"    ✓ {prediction['prediction']} (confidence: {prediction['confidence']:.2%})")
                
            except Exception as e:
                print(f"    ❌ Error: {e}")
                continue

        # Create results dataframe
        df_results = pd.DataFrame(results)
        
        if output_file:
            df_results.to_csv(output_file, index=False)
            print(f"\n✓ Results saved to: {output_file}")
        
        print(f"\n📊 Batch Prediction Summary")
        print("="*70)
        print(f"Total Cases: {len(df_results)}")
        print(f"Average Confidence: {df_results['confidence'].mean():.2%}")
        print(f"\nOutcome Distribution:")
        print(df_results['prediction'].value_counts())
        
        return df_results


def main():
    parser = argparse.ArgumentParser(
        description="RAG-Enhanced Judgment Prediction (NYARAG Architecture)"
    )
    parser.add_argument(
        "--case",
        type=str,
        help="Path to single case JSON file for prediction"
    )
    parser.add_argument(
        "--batch",
        type=str,
        help="Directory containing multiple case JSON files"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output CSV file for batch results"
    )
    parser.add_argument(
        "--k-neighbors",
        type=int,
        default=10,
        help="Number of similar precedents to retrieve (default: 10)"
    )
    parser.add_argument(
        "--no-gaps",
        action="store_true",
        help="Skip missing evidence analysis"
    )
    parser.add_argument(
        "--no-contradictions",
        action="store_true",
        help="Skip contradiction detection"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Minimal output"
    )

    args = parser.parse_args()

    demo = RAGJudgmentDemo(k_neighbors=args.k_neighbors)

    if args.case:
        # Single case prediction
        if not os.path.exists(args.case):
            print(f"❌ Case file not found: {args.case}")
            return
        
        demo.predict_case(
            args.case,
            analyze_gaps=not args.no_gaps,
            analyze_contradictions=not args.no_contradictions,
            verbose=not args.quiet
        )

    elif args.batch:
        # Batch prediction
        if not os.path.isdir(args.batch):
            print(f"❌ Directory not found: {args.batch}")
            return
        
        demo.batch_predict(args.batch, output_file=args.output)

    else:
        # Interactive mode
        print("\n" + "="*70)
        print("🏛️  NYARAG JUDGMENT PREDICTION - Interactive Mode")
        print("="*70)
        print("\nUsage:")
        print("  python -m models.judgment.rag_judgment_demo --case <path>")
        print("  python -m models.judgment.rag_judgment_demo --batch <dir>")
        print("\nExample:")
        print("  python -m models.judgment.rag_judgment_demo --case case_123.json")
        print("\nRun with --help for more options.")


if __name__ == "__main__":
    main()
