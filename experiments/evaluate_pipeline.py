import json
from scrapers.main_pipeline import LegalPipeline
from tqdm import tqdm

def evaluate_on_weak_cases():
    pipeline = LegalPipeline()
    
    with open("/home/amaydixit11/Desktop/dev/Legal-Intelligence-System/results/failed_cases_index.json", 'r') as f:
        weak_cases = json.load(f)
    
    print(f"🧐 Evaluating on {len(weak_cases)} weak cases...")
    
    correct_failures = 0
    total = min(len(weak_cases), 50) # Evaluate on a subset for speed
    
    for i in range(total):
        case_id = weak_cases[i]["case_id"]
        result = pipeline.analyze_case(case_id=case_id)
        
        if result.get("prediction", {}).get("likely_outcome") == "FAILURE/WEAK":
            correct_failures += 1
            
    accuracy = (correct_failures / total) * 100 if total > 0 else 0
    print(f"\n📊 EVALUATION COMPLETE")
    print(f"Total Weak Cases Evaluated: {total}")
    print(f"Correctly Predicted as 'Weak': {correct_failures}")
    print(f"Precision on Weak Cases: {accuracy:.1f}%")

if __name__ == "__main__":
    evaluate_on_weak_cases()
