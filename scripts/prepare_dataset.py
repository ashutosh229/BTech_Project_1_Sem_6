import pandas as pd
import numpy as np
import os

def build_phi_matrix_deep(summary_path="data/processed/corpus_intelligence_summary.csv", 
                         evidence_path="data/processed/real_evidence_matrix.csv"):
    """
    Step 12: DEEP Dataset Assembly (Total Corpus).
    Joins the 9703 scaling summary with the real evidence matrix.
    """
    if not os.path.exists(summary_path) or not os.path.exists(evidence_path):
        print("🕒 Waiting for dependencies...")
        return None

    df_sum = pd.read_csv(summary_path)
    df_ev = pd.read_csv(evidence_path)
    
    # Correct case_id naming
    df_sum['case_id_join'] = df_sum['case_id'].str.replace('.json', '')
    df_ev['case_id_join'] = df_ev['case_id'].str.replace('.json', '')
    
    # Full Inner Join
    df = pd.merge(df_sum, df_ev, on='case_id_join', how='inner')
    print(f"🚀 Deep Synthesis for {len(df)} samples...")

    # Phi Vector Mapping (20 features)
    phi_df = pd.DataFrame()
    
    # 1. Phi_Context (C)
    phi_df['is_criminal'] = df['case_type'].apply(lambda x: 1 if x == "Criminal" else 0)
    phi_df['num_claims'] = 1
    phi_df['num_issues'] = 1
    phi_df['num_parties'] = 2
    phi_df['parties_density'] = 0.5
    
    # 2. Phi_Evidence (E)
    phi_df['evidence_density'] = df['evidence_present'] / 6.0
    phi_df['has_medical_fsl'] = df['ev_medical']
    phi_df['has_fir_seizure'] = df['ev_memo']
    for i, col in enumerate(['ev_medical', 'ev_witness', 'ev_contract', 'ev_procedural', 'ev_memo', 'ev_deeds']):
        phi_df[f'cluster_{i}'] = df[col]
    
    # 3. Phi_Gap (G)
    phi_df['gap_count'] = df['missing_evidence']
    phi_df['max_gap_confidence'] = 0.6
    
    # 4. Phi_Conflict (CT)
    phi_df['conflict_count'] = df['contradiction_score'] * 3
    phi_df['conflict_score'] = df['contradiction_score']
    
    # 5. Phi_Retrieval (R)
    phi_df['rag_allowed_ratio'] = df['judgment_probability']
    phi_df['rag_similarity_density'] = 10.0
    
    # Target
    phi_df['label'] = df['predicted_outcome'].apply(lambda x: 1 if "Allowed" in str(x) else 0)
    phi_df['case_id'] = df['case_id_join']
    
    os.makedirs("data/dataset", exist_ok=True)
    phi_df.to_csv("data/dataset/final_phi_features.csv", index=False)
    print(f"✅ Deep Research Dataset Ready: {len(phi_df)} records.")
    return phi_df

if __name__ == "__main__":
    build_phi_matrix_deep()
