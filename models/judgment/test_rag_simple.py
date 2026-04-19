"""
Simple RAG Judgment Prediction Test Using Shareable Embeddings

No external dependencies beyond numpy/json.
Demonstrates:
1. Loading shareable legal embeddings (dense vectors for all cases)
2. Building similarity index
3. Retrieving similar cases
4. RAG-enhanced judgment prediction
"""

import json
import numpy as np
import os
from typing import List, Dict, Tuple


class SimpleRAGTest:
    """Test RAG judgment prediction using shareable embeddings."""

    def __init__(self):
        self.BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        self.embeddings_path = os.path.join(self.BASE_DIR, "outputs", "shareable_legal_vectors.json")
        self.sample_analysis_path = os.path.join(self.BASE_DIR, "outputs", "system_final_allahabad_2015_3099880.json")

    def load_shareable_embeddings(self) -> Tuple[List[Dict], int]:
        """Load shareable embeddings and return list of case embeddings with metadata."""
        print("📦 Loading shareable legal embeddings...")
        print(f"   File: {self.embeddings_path}")
        
        try:
            with open(self.embeddings_path, 'r', encoding='utf-8') as f:
                embeddings_list = json.load(f)
            
            # embeddings_list is a list of dicts, each with metadata and embedding vector
            num_cases = len(embeddings_list)
            
            # Get embedding dimension from first item
            embedding_dim = 0
            if embeddings_list and isinstance(embeddings_list[0], dict):
                first_item = embeddings_list[0]
                # Find the embedding vector in the dict
                if 'embedding' in first_item:
                    embedding_dim = len(first_item['embedding'])
                elif 'vector' in first_item:
                    embedding_dim = len(first_item['vector'])
                else:
                    # Try to find a numeric list in the dict
                    for key, val in first_item.items():
                        if isinstance(val, list) and len(val) > 10:  # Embeddings are typically long vectors
                            embedding_dim = len(val)
                            break
            
            print(f"✓ Success! Loaded {num_cases:,} case embeddings")
            print(f"✓ Embedding dimension: {embedding_dim}")
            
            return embeddings_list, embedding_dim
            
        except Exception as e:
            print(f"❌ Failed to load embeddings: {e}")
            import traceback
            traceback.print_exc()
            return [], 0

    def build_similarity_index(self, embeddings_list: List[Dict]) -> Tuple[Tuple[np.ndarray, List[str]], np.ndarray, List[str]]:
        """Build numpy array for similarity search from list of embedding dicts."""
        print("\n🔨 Building similarity search index...")
        
        case_ids = []
        embedding_vectors = []
        
        for item in embeddings_list:
            # Extract case_id from metadata
            if isinstance(item, dict):
                if 'metadata' in item and 'case_id' in item['metadata']:
                    case_id = item['metadata']['case_id']
                elif 'case_id' in item:
                    case_id = item['case_id']
                else:
                    case_id = f"case_{len(case_ids)}"
                
                # Extract embedding vector
                if 'embedding' in item:
                    vector = item['embedding']
                elif 'vector' in item:
                    vector = item['vector']
                else:
                    # Skip items without clear embedding
                    continue
                
                case_ids.append(case_id)
                embedding_vectors.append(vector)
        
        if not embedding_vectors:
            print("❌ No valid embeddings found")
            return (np.array([]), []), np.array([]), []
        
        index_array = np.array(embedding_vectors, dtype=np.float32)
        
        print(f"✓ Index built successfully")
        print(f"✓ Shape: {index_array.shape} (cases × dimensions)")
        print(f"✓ Cases indexed: {len(case_ids)}")
        
        return index_array, case_ids

    def build_similarity_index_old(self, embeddings: Dict) -> Tuple[np.ndarray, List[str]]:
        """Build numpy array for similarity search."""
        print("\n🔨 Building similarity search index...")
        
        case_ids = list(embeddings.keys())
        embedding_vectors = []
        
        for cid in case_ids:
            vec = embeddings[cid]
            if isinstance(vec, list):
                embedding_vectors.append(vec)
            else:
                embedding_vectors.append(vec)
        
        index_array = np.array(embedding_vectors, dtype=np.float32)
        
        print(f"✓ Index built successfully")
        print(f"✓ Shape: {index_array.shape} (cases × dimensions)")
        print(f"✓ Cases indexed: {len(case_ids)}")
        
        return index_array, case_ids

    def find_similar_cases(self, 
                          query_embedding: np.ndarray,
                          index_vectors: np.ndarray,
                          case_ids: List[str],
                          k: int = 10) -> List[Tuple[str, float]]:
        """Find top-k similar cases using cosine similarity."""
        print(f"\n🔍 Finding {k} similar cases using cosine similarity...")
        
        try:
            # Normalize for cosine similarity
            query_norm = query_embedding / (np.linalg.norm(query_embedding) + 1e-8)
            index_norm = index_vectors / (np.linalg.norm(index_vectors, axis=1, keepdims=True) + 1e-8)
            
            # Cosine similarity
            similarities = np.dot(index_norm, query_norm)
            top_k_indices = np.argsort(similarities)[::-1][:k]
            
            results = []
            print(f"\n   Top {k} Similar Cases:")
            print(f"   {'Case ID':<40} {'Similarity':<12}")
            print("   " + "─" * 52)
            
            for rank, idx in enumerate(top_k_indices, 1):
                case_id = case_ids[idx]
                score = float(similarities[idx])
                results.append((case_id, score))
                print(f"   {rank:2d}. {case_id:<36} {score:.6f}")
            
            return results
        except Exception as e:
            print(f"❌ Similarity search failed: {e}")
            import traceback
            traceback.print_exc()
            return []

    def load_sample_case_analysis(self) -> Dict:
        """Load sample case analysis with predictions."""
        print("\n📄 Loading sample case analysis...")
        print(f"   File: {self.sample_analysis_path}")
        
        try:
            with open(self.sample_analysis_path, 'r', encoding='utf-8') as f:
                analysis = json.load(f)
            
            case_id = analysis.get('case_id', 'unknown')
            print(f"✓ Loaded case analysis: {case_id}")
            
            # Show some key fields
            if 'prediction' in analysis:
                pred = analysis['prediction']
                print(f"   ML Prediction Score: {pred.get('judgment_probability', 'N/A')}")
            
            return analysis
            
        except Exception as e:
            print(f"❌ Failed to load sample analysis: {e}")
            return {}

    def simulate_rag_prediction(self, 
                                similar_cases: List[Tuple[str, float]],
                                sample_analysis: Dict) -> Dict:
        """Simulate RAG-enhanced prediction from similar cases."""
        print(f"\n🧠 Generating RAG-enhanced prediction...")
        
        if not similar_cases:
            print("❌ No similar cases found for RAG reasoning")
            return {}
        
        # Simulate outcome distribution from similar cases
        # Weights based on similarity score
        allowed_weight = 0.0
        dismissed_weight = 0.0
        
        for case_id, similarity in similar_cases:
            # Simulate outcomes based on deterministic hash of case_id
            # In production, query actual case outcomes from database
            outcome_hash = hash(case_id) % 100
            
            if outcome_hash < 55:  # 55% allowed rate
                allowed_weight += similarity
            else:
                dismissed_weight += similarity
        
        total_weight = allowed_weight + dismissed_weight + 1e-8
        rag_allowed_prob = allowed_weight / total_weight
        rag_dismissed_prob = dismissed_weight / total_weight
        
        # Get original ML prediction if available
        original_pred = sample_analysis.get("prediction", {})
        original_score = float(original_pred.get("judgment_probability", 0.5))
        
        # Weighted ensemble: 0.4 ML + 0.6 RAG
        ensemble_score = 0.4 * original_score + 0.6 * rag_allowed_prob
        
        print(f"   RAG Allowed Score (from {len(similar_cases)} precedents): {rag_allowed_prob:.4f}")
        print(f"   RAG Dismissed Score: {rag_dismissed_prob:.4f}")
        print(f"   Original ML Score: {original_score:.4f}")
        print(f"   Ensemble Score (0.4×ML + 0.6×RAG): {ensemble_score:.4f}")
        
        return {
            "rag_allowed_score": rag_allowed_prob,
            "rag_dismissed_score": rag_dismissed_prob,
            "original_ml_score": original_score,
            "ensemble_score": ensemble_score,
            "similar_cases_count": len(similar_cases),
            "confidence": max(rag_allowed_prob, rag_dismissed_prob)
        }

    def run_test(self):
        """Run full RAG test pipeline."""
        print("\n" + "=" * 80)
        print("🧪 RAG JUDGMENT PREDICTION TEST (Using Shareable Embeddings)")
        print("=" * 80)
        
        # Step 1: Load embeddings
        embeddings_list, embedding_dim = self.load_shareable_embeddings()
        if not embeddings_list or embedding_dim == 0:
            print("\n❌ Cannot proceed without valid embeddings")
            return
        
        # Step 2: Build similarity index
        index_vectors, case_ids = self.build_similarity_index(embeddings_list)
        
        if len(case_ids) == 0:
            print("\n❌ No cases indexed")
            return
        
        # Step 3: Load sample case analysis
        sample_case = self.load_sample_case_analysis()
        if not sample_case:
            print("\n❌ Cannot proceed without sample case")
            return
        
        # Step 4: Extract or simulate query embedding for sample case
        sample_case_id = sample_case.get('case_id')
        query_found_in_index = False
        query_embedding = None
        
        # Try to find sample case in embeddings list
        for item in embeddings_list:
            item_case_id = None
            if isinstance(item, dict):
                if 'metadata' in item and 'case_id' in item['metadata']:
                    item_case_id = item['metadata']['case_id']
                elif 'case_id' in item:
                    item_case_id = item['case_id']
            
            if item_case_id == sample_case_id:
                if 'embedding' in item:
                    query_embedding = np.array(item['embedding'], dtype=np.float32)
                elif 'vector' in item:
                    query_embedding = np.array(item['vector'], dtype=np.float32)
                
                if query_embedding is not None:
                    query_found_in_index = True
                    print(f"\n✓ Using embedding for query case: {sample_case_id}")
                    break
        
        if not query_found_in_index:
            print(f"\n⚠ Sample case {sample_case_id} NOT in embedding index")
            print("  Generating random query embedding for demonstration")
            query_embedding = np.random.randn(embedding_dim).astype(np.float32)
        
        # Step 5: Find similar cases
        similar_cases = self.find_similar_cases(query_embedding, index_vectors, case_ids, k=10)
        
        if not similar_cases:
            print("\n❌ Failed to find similar cases")
            return
        
        # Step 6: Generate RAG prediction
        rag_result = self.simulate_rag_prediction(similar_cases, sample_case)
        
        # Step 7: Display results
        print("\n" + "=" * 80)
        print("📊 FINAL RESULTS")
        print("=" * 80)
        
        print(f"\nQuery Case ID: {sample_case_id}")
        print(f"Case in Index: {'YES' if query_found_in_index else 'NO (simulated for demo)'}")
        print(f"Similar Cases Retrieved: {len(similar_cases)}")
        
        print(f"\n📈 Prediction Scores:")
        print(f"   ML Only:     {rag_result.get('original_ml_score', 0):.4f}")
        print(f"   RAG Only:    {rag_result.get('rag_allowed_score', 0):.4f}")
        print(f"   ENSEMBLE:    {rag_result.get('ensemble_score', 0):.4f}")
        
        final_verdict = "ALLOWED ✓" if rag_result['ensemble_score'] > 0.5 else "DISMISSED ✗"
        confidence = rag_result.get('confidence', 0)
        
        print(f"\n🎯 FINAL VERDICT: {final_verdict}")
        print(f"   Confidence: {confidence:.4f}")
        
        # Save test results
        output_path = os.path.join(self.BASE_DIR, "outputs", "rag_test_results.json")
        results = {
            "test_status": "SUCCESS",
            "query_case": sample_case_id,
            "embeddings_loaded": len(embeddings_list),
            "embedding_dimension": embedding_dim,
            "similar_cases_found": len(similar_cases),
            "prediction_results": {
                "ml_score": rag_result.get('original_ml_score', 0),
                "rag_score": rag_result.get('rag_allowed_score', 0),
                "ensemble_score": rag_result.get('ensemble_score', 0),
                "confidence": confidence,
                "final_verdict": final_verdict.split()[0]  # Just 'ALLOWED' or 'DISMISSED'
            },
            "similar_cases": [
                {"rank": i+1, "case_id": cid, "similarity": float(score)} 
                for i, (cid, score) in enumerate(similar_cases[:5])
            ]
        }
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)
            print(f"\n💾 Test results saved to: {output_path}")
        except Exception as e:
            print(f"\n⚠ Could not save results: {e}")
        
        print("\n" + "=" * 80)
        print("✅ RAG TEST COMPLETED SUCCESSFULLY")
        print("=" * 80)


if __name__ == "__main__":
    test = SimpleRAGTest()
    test.run_test()
