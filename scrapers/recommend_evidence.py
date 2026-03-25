import json
import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

# --- Configuration ---
RESULTS_DIR = "/home/amaydixit11/Desktop/dev/Legal-Intelligence-System/results"
INDEX_FILE = f"{RESULTS_DIR}/legal_fact_index.faiss"
ID_MAP_FILE = f"{RESULTS_DIR}/case_indices.json"
MATRIX_FILE = f"{RESULTS_DIR}/case_evidence_matrix.csv"
WEAK_INDEX_FILE = f"{RESULTS_DIR}/failed_cases_index.json"
MODEL_NAME = 'law-ai/InLegalBERT'

# Human-readable cluster names
CLUSTER_NAMES = {
    "cluster_0": "Medical/FSL Reports",
    "cluster_1": "PW Testimony (Star Witness)",
    "cluster_2": "Agreements/Contracts",
    "cluster_3": "Other Procedural/Memo",
    "cluster_4": "FIR/Seizure/PM Reports",
    "cluster_5": "Property Deeds"
}

def get_recommendations(query_case_id):
    # 1. Load Resources
    index = faiss.read_index(INDEX_FILE)
    with open(ID_MAP_FILE, 'r') as f:
        case_ids = json.load(f)
    
    matrix_df = pd.read_csv(MATRIX_FILE)
    with open(WEAK_INDEX_FILE, 'r') as f:
        weak_data = json.load(f)
    
    failed_ids = [c["case_id"] for c in weak_data]
    model = SentenceTransformer(MODEL_NAME)

    # 2. Get Query Vector
    if query_case_id not in case_ids:
        print(f"❌ Case ID {query_case_id} not found in the semantic index.")
        return
    
    query_idx = case_ids.index(query_case_id)
    # We need to re-extract the vector... actually FAISS index.reconstruct(query_idx) works
    query_vector = index.reconstruct(query_idx).reshape(1, -1)

    # 3. Find 10 nearest neighbors
    D, I = index.search(query_vector, 20) # Search 20 to find enough successful ones
    
    # Filter for SUCCESSFUL cases
    similar_success_ids = []
    for idx_in_index in I[0]:
        cid = case_ids[idx_in_index]
        if cid != query_case_id and cid not in failed_ids:
            similar_success_ids.append(cid)
        if len(similar_success_ids) >= 5: break

    print(f"\n🔍 Query Case: {query_case_id} (WEAK)")
    print(f"✅ Found {len(similar_success_ids)} similar successful cases for comparison.")

    # 4. Compare Evidence Vectors
    query_evidence = matrix_df[matrix_df['case_id'] == query_case_id].iloc[0]
    success_evidence = matrix_df[matrix_df['case_id'].isin(similar_success_ids)]

    cluster_cols = [c for c in matrix_df.columns if c.startswith("cluster_")]
    
    print("\n" + "="*60)
    print(f"{'Evidence Cluster':<30} | {'Query':<7} | {'Success Avg':<12} | {'Recommendation'}")
    print("-" * 75)

    recommendations = []
    for col in cluster_cols:
        q_val = query_evidence[col]
        s_avg = success_evidence[col].mean()
        
        rel_diff = s_avg - q_val
        status = "PRESENT" if q_val == 1 else "MISSING"
        advise = "⚠️ CRITICAL MISSING" if rel_diff > 0.5 else "OPTIMAL" if q_val == 1 else "NOT REQUIRED"
        
        name = CLUSTER_NAMES.get(col, col)
        print(f"{name:<30} | {status:<7} | {s_avg*100:>10.1f}% | {advise}")
        
        if advise == "⚠️ CRITICAL MISSING":
            recommendations.append(name)

    print("="*60)
    if recommendations:
        print(f"\n💡 STRATEGY: To strengthen this case, focus on obtaining: {', '.join(recommendations)}.")
    else:
        print("\n💡 STRATEGY: Case evidence structure aligns well with successful precedents.")

if __name__ == "__main__":
    # Test with a known weak case from our index
    with open(WEAK_INDEX_FILE, 'r') as f:
        weak_samples = json.load(f)
    
    if weak_samples:
        test_case = weak_samples[0]["case_id"]
        get_recommendations(test_case)
    else:
        print("No weak cases found to test.")
