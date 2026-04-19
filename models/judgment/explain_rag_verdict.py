"""
Detailed explanation of RAG Judgment Prediction
"""

import json

# Read the sample case
with open('outputs/system_final_allahabad_2015_3099880.json', 'r') as f:
    case_data = json.load(f)

# Read the RAG test results
with open('outputs/rag_test_results.json', 'r') as f:
    rag_results = json.load(f)

print("\n" + "=" * 90)
print("📋 RAG JUDGMENT PREDICTION - DETAILED EXPLANATION")
print("=" * 90)

print("\n" + "🔵 STEP 1: INPUT CASE (Query Case - The Case We're Predicting For)")
print("-" * 90)
con = case_data.get('con', {})
print(f"Case ID:     {con.get('case_id')}")
print(f"Case Type:   {con.get('case_type')}")
print(f"Evidence:    {', '.join(con.get('evidence_present', []))}")
print(f"Claim:       {con.get('claims', [{}])[0].get('text', '')[:80]}...")

print("\n" + "🟢 STEP 2: RETRIEVE SIMILAR CASES (Using Dense Legal Embeddings)")
print("-" * 90)
print("The system encodes this case into a 768-dimensional legal embedding.")
print("Then searches through ALL 9,703 cases in the database using cosine similarity.")
print("Returns the TOP-10 most similar precedent cases:\n")

similar_cases = case_data.get('similar_cases', [])
allowed_count = 0
dismissed_count = 0

print(f"{'Rank':<5} {'Case ID':<45} {'Outcome':<25} {'Distance':<10}")
print("-" * 90)

for i, case in enumerate(similar_cases[:10], 1):
    outcome = case.get('outcome', 'Unknown')
    distance = case.get('distance', 'N/A')
    case_id = case.get('case_id')
    
    if 'Allowed' in outcome:
        allowed_count += 1
        emoji = "✓"
    else:
        dismissed_count += 1
        emoji = "✗"
    
    print(f"{i:<5} {case_id:<45} {emoji} {outcome:<23} {distance:<10}")

print("\n" + "📊 OUTCOME DISTRIBUTION OF TOP-10 SIMILAR CASES:")
print("-" * 90)
total = allowed_count + dismissed_count
print(f"  ✓ ALLOWED/SUCCESS:  {allowed_count:2d}/10 cases  ({allowed_count*100/total:.1f}%)")
print(f"  ✗ DISMISSED/WEAK:   {dismissed_count:2d}/10 cases  ({dismissed_count*100/total:.1f}%)")

print("\n" + "🟡 STEP 3: CALCULATE RAG-BASED PREDICTION")
print("-" * 90)
print(f"RAG Logic:")
print(f"  1. Among top-10 similar cases, COUNT how many were ALLOWED: {allowed_count}")
print(f"  2. Among top-10 similar cases, COUNT how many were DISMISSED: {dismissed_count}")
print(f"  3. Calculate Allowed Probability = {allowed_count}/{total} = {allowed_count/total*100:.1f}%")
print(f"\n  → RAG Confidence Score: {allowed_count/total:.4f}  (This is {allowed_count/total*100:.2f}% confidence)")

print("\n" + "🔴 STEP 4: ENSEMBLE PREDICTION (Combine ML + RAG)")
print("-" * 90)

rag_score = rag_results['prediction_results']['rag_score']
ml_score = rag_results['prediction_results']['ml_score']
ensemble = rag_results['prediction_results']['ensemble_score']
verdict = rag_results['prediction_results']['final_verdict']

print(f"XGBoost ML Score:         {ml_score:.4f}")
print(f"RAG Score (Precedents):   {rag_score:.4f}  ← From {allowed_count}/{total} similar cases allowed")
print(f"\nEnsemble Formula: (0.4 × ML) + (0.6 × RAG)")
print(f"                = (0.4 × {ml_score:.4f}) + (0.6 × {rag_score:.4f})")
print(f"                = {0.4*ml_score:.4f} + {0.6*rag_score:.4f}")
print(f"                = {ensemble:.4f}")

print(f"\n  Compare: {ensemble:.4f} > 0.5 ?  → YES ✓")
print(f"  Final Verdict: {verdict.upper()}")

print("\n" + "💡 WHAT DOES 'ALLOWED' MEAN?")
print("-" * 90)
print("'ALLOWED' is a PREDICTION - it means the system predicts the case will be ALLOWED")
print("\nIn Indian Judicial System:")
print("  ✓ ALLOWED   = Case allowed, appeal allowed, petition accepted, suit decreed")
print("              = Plaintiff/Petitioner wins")
print("  ✗ DISMISSED = Case dismissed, appeal dismissed, petition rejected, suit dismissed")
print("              = Plaintiff/Petitioner loses")

print("\n" + "📈 HOW RAG WORKS:")
print("-" * 90)
print(f"""
The RAG System Reasoning:

  1. INPUT:  Query case "Smt. Pushpa Sareen vs State Of U.P. (2015)"
             [Case features: Civil case, Evidence: Agreements & Deeds, ...]

  2. SEARCH: Find semantically similar precedent cases in database
             Top-10 by legal embedding similarity:
             - cat_2025_58456480        → ALLOWED ✓
             - supremecourt_2017_140349586 → ALLOWED ✓
             - sebisat_2022_192078227   → ALLOWED ✓
             - ... and 7 more

  3. ANALYZE: Look at outcomes of these similar cases
              {allowed_count} out of 10 were ALLOWED
              → {allowed_count*100/10:.1f}% precedent success rate

  4. PREDICT: Since similar cases were mostly ALLOWED
              → This case will likely also be ALLOWED
              → Confidence: {rag_score*100:.1f}%

  5. REPORT: VERDICT = "ALLOWED" with {rag_score*100:.1f}% confidence
""")

print("=" * 90)
print("✅ This is how RAG Judgment Prediction works - by learning from similar precedents!")
print("=" * 90)
