import json
import numpy as np
from con.feature_builder import LegalFeatureBuilder
from models.judgment.predict import UnifiedInferenceEngine

def run_demo():
    # 1. Load the case (Shyamsingh v. State of MP)
    case_path = 'data/madhyapradesh_2021_62734450.json'
    with open(case_path, 'r') as f:
        case_data = json.load(f)

    # 2. Mock outputs from Level 2/3 modules (these would normally come from FAISS/Gap modules)
    mock_similar = [
        {'id': 'allahabad_2015_3099880', 'distance': 0.15, 'outcome': 'Allowed/Success'},
        {'id': 'allahabad_2015_2847201', 'distance': 0.22, 'outcome': 'Dismissed/Weak'}
    ]
    mock_missing = [{'type': 'Statement under 164', 'importance': 0.8}]
    mock_contradictions = {
        'found_contradictions': [{'type': 'Time gap in reporting', 'score': 0.4}],
        'contradiction_score': 0.4
    }

    # 3. Build the Φ-Vector (The "Legal Fingerprint")
    builder = LegalFeatureBuilder()
    phi_dict = builder.build_phi_dict(
        case_data, 
        similar_cases=mock_similar, 
        missing_evidence=mock_missing, 
        contradictions=mock_contradictions
    )

    # 4. Display Results
    print('\n' + '='*40)
    print('   JUDGMENT PIPELINE DEMO   ')
    print('='*40)
    print(f'Case: {case_data.get("case_title", "Unknown")}')
    print('\n[+] PHI-VECTOR (TOP 10 NUMERIC SIGNALS)')
    print('This matrix is what the XGBoost model consumes.')
    
    # Sort signals by absolute weight for display
    sorted_phi = sorted(phi_dict.items(), key=lambda x: abs(x[1]), reverse=True)
    for k, v in sorted_phi:
        if isinstance(v, (int, float)) and v != 0:
            print(f'  {k:.<25} {v:.4f}')

    # 5. Run Inference Engine
    print('\n[+] AI PREDICTION ENGINE')
    engine = UnifiedInferenceEngine(model_path='outputs/models/judgment_model.joblib')
    
    try:
        # This will fail if train.py hasn't run yet, which is expected
        result = engine.run_inference(case_data, mock_similar, mock_missing, mock_contradictions)
        print(f'    Final Prediction: {result["prediction"]}')
        print(f'    Reasoning Confidence: {result["confidence"] * 100:.1f}%')
    except Exception:
        print('    [!] Status: Model not yet trained (no .joblib file found).')
        print('    [!] Internal Projection (RAG-based):')
        
        # Manually calculate a RAG-weighted projection for the demo
        rag_win_prob = phi_dict.get('rag_weighted_outcome', 0.5)
        outcome = "Allowed / Success Likely" if rag_win_prob > 0.5 else "Dismissed / High Risk"
        
        print(f'        Weighted Neighborhood Outcome: {outcome}')
        print(f'        Projected Success Prob: {rag_win_prob * 100:.1f}%')
        print('\n    [RUN train.py to activate full XGBoost inference]')

if __name__ == "__main__":
    run_demo()
