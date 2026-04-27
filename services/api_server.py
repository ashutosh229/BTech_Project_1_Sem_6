from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import sys
import json
import numpy as np
from pathlib import Path

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import prediction logic
from models.judgment.nyarag_groq_implementation import NyayaRAGPredictor, RAGContextBuilder, llm
from models.judgment.rag_judgment_predictor import RAGJudgmentPredictor

app = FastAPI(title="Legal Intelligence API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

EVIDENCE_OPTIONS = [
    "medical", "witness", "fir", "contracts", "deeds", "procedural"
]

class CaseAnalysisRequest(BaseModel):
    case_type: str
    parties: Optional[str] = ""
    facts: str
    evidence: List[str] = []
    reliefs: Optional[str] = ""

# Global predictors
rag_builder = None
llm_predictor = None
ensemble_predictor = None

@app.on_event("startup")
async def init_predictors():
    global rag_builder, llm_predictor, ensemble_predictor
    print("🚀 Initializing Legal Intelligence Engines...")
    
    # Initialize RAG Builder (Vector Search)
    rag_builder = RAGContextBuilder(
        embeddings_path="outputs/shareable_legal_vectors.json",
        analysis_path="outputs/system_final_allahabad_2015_3099880.json"
    )
    
    # Initialize NyayaRAG (Groq LLM)
    llm_predictor = NyayaRAGPredictor(llm, rag_builder)
    
    # Initialize Ensemble Predictor (Corpus Analytics)
    ensemble_predictor = RAGJudgmentPredictor()
    print("✅ All engines ready.")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "engines": ["faiss", "groq", "xgboost"]}

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def extract_statutes_from_text(text: str) -> List[Dict]:
    import re
    matches = re.findall(r'\b(\d+[A-Z]?)\s*(?:of\s*)?(IPC|BNS)\b', text, re.IGNORECASE)
    
    statutes = []
    seen = set()
    for sec, code in matches:
        code = code.upper()
        sec = sec.upper()
        
        match_letter = re.match(r'^(\d+)([A-Z])$', sec)
        if match_letter:
            file_sec = f"{match_letter.group(1)} {match_letter.group(2)}"
        else:
            file_sec = sec
            
        key = f"{file_sec}_{code}"
        if key in seen:
            continue
        seen.add(key)
        
        dir_name = "ipc_sections" if code == "IPC" else "bns_sections"
        path = os.path.join(BASE_DIR, "data", dir_name, f"{file_sec}_{code}.json")
        
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                    impact = "High" if "Non-Bailable" in str(data.get("bail", "")) else "Medium"
                    if "death" in str(data.get("punishment", "")).lower() or "life" in str(data.get("punishment", "")).lower():
                        impact = "Critical"
                        
                    statutes.append({
                        "section": f"Sec {sec} {code}",
                        "title": data.get("title", "Statutory Provision"),
                        "desc": data.get("description", "")[:150] + ("..." if len(data.get("description", "")) > 150 else ""),
                        "impact": impact
                    })
            except Exception as e:
                print(f"Error loading {path}: {e}")
                pass
                
    if not statutes:
        statutes = [
            {"section": "Stamp Act Sec 47-A", "title": "Undervalued Instruments", "desc": "Procedure for dealing with undervalued instruments.", "impact": "Direct"},
            {"section": "Stamp Act Sec 27", "title": "Duty Considerations", "desc": "Facts affecting duty must be set forth.", "impact": "Substantive"}
        ]
        
    return statutes

@app.post("/analyze")
async def analyze_case(req: CaseAnalysisRequest):
    if not ensemble_predictor or not llm_predictor:
        raise HTTPException(status_code=503, detail="Engines not initialized")
    
    try:
        # Dynamically extract statutes from facts
        dynamic_statutes = extract_statutes_from_text(req.facts + " " + req.case_type)
        
        # Map UI evidence to coarse ML names
        UI_TO_COARSE_MAP = {
            "medical": "Medical/FSL Reports",
            "witness": "Witness Testimony (PW)",
            "fir": "FIR/Seizure/PM Reports",
            "contracts": "Agreements & Contracts",
            "deeds": "Property Deeds",
            "procedural": "Other Procedural Docs"
        }
        ml_evidence = [UI_TO_COARSE_MAP[e] for e in req.evidence if e in UI_TO_COARSE_MAP]

        # 1. Convert request to internal CON format
        con_dict = {
            "case_id": "current_live_analysis",
            "case_type": req.case_type,
            "facts": req.facts,
            "evidence_present": ml_evidence,
            "reliefs": [req.reliefs] if req.reliefs else []
        }

        # 2. Retrieve Precedents FIRST (needed for both LLM and Ensemble)
        print(f"🔍 Retrieving precedents for case type: {req.case_type}")
        retrieved = ensemble_predictor._retrieve_precedents(con_dict)

        # 3. Run Ensemble Prediction (Pattern Matching + Precedent RAG)
        # We pass retrieved cases to avoid double retrieval
        re = ensemble_predictor.predict(con_dict, similar_cases=retrieved)
        
        # 4. Run LLM Synthetic Reasoning (NyayaRAG)
        # We pass the retrieved precedents from our vector search
        llm_res = llm_predictor.predict(req.facts, retrieved)

        # 5. Synthesize Factor Impacts
        factors = []
        if "reasoning" in re:
            res_reasoning = re["reasoning"]
            
            # Neural Pattern Match
            if "ml_prediction" in res_reasoning:
                ml_p = res_reasoning["ml_prediction"]
                factors.append({
                    "label": "Neural Pattern Match",
                    "impact": round(ml_p["score"] * 100 - 50),
                    "type": "positive" if ml_p["score"] > 0.5 else "negative",
                    "desc": "Alignment with successful Civil clusters in corpus."
                })
            
            # Precedent Consensus
            if "rag_consensus" in res_reasoning:
                rag_c = res_reasoning["rag_consensus"]
                factors.append({
                    "label": "Precedent Consensus",
                    "impact": round(rag_c["allowed_score"] * 100 - 50),
                    "type": "positive" if rag_c["allowed_score"] > 0.5 else "negative",
                    "desc": f"Majority of {rag_c['precedent_count']} retrieved cases follow this trend."
                })

        # Process similar cases to match UI structure
        similar_cases_ui = []
        for c in retrieved[:5]:
            # Improved scaling for unnormalized L2 distances
            raw_sim = 1.0 / (1.0 + (float(c.get("distance", 0.0)) / 500.0))
            sim_pct = round(raw_sim * 100, 1)
            
            # Clean case ID
            raw_id = str(c.get("case_id", "Unknown")).replace(".json", "")
            
            # Extract year from ID
            id_parts = raw_id.split("_")
            year = id_parts[1] if len(id_parts) > 1 and id_parts[1].isdigit() else "2015"
            
            similar_cases_ui.append({
                "id": raw_id,
                "outcome": c.get("outcome", "Unknown"),
                "similarity": sim_pct,
                "year": year,
                "summary": f"Case involves facts similar to {req.case_type} profile.",
                "reasoning": "Retrieval match based on InLegalBERT semantic vectors."
            })

        # Final Logic for Frontend Display
        final_score = re["score"]
        pred_label = "Allowed/Success" if final_score > 0.5 else "Dismissed/Weak"
        # Confidence is the magnitude of the assertion
        confidence_pct = round(max(final_score, 1.0 - final_score) * 100)

        # --- ML COUNTERFACTUAL LIFT (How to Improve Odds) ---
        missingEvidence = []
        for ui_key, ml_name in UI_TO_COARSE_MAP.items():
            if ml_name not in ml_evidence:
                cf_con = con_dict.copy()
                cf_con["evidence_present"] = ml_evidence + [ml_name]
                cf_re = ensemble_predictor.predict(cf_con, similar_cases=retrieved, return_breakdown=False)
                lift = cf_re["score"] - final_score
                
                # Lower threshold so we always show *some* sensitivity, even if minor
                if lift > 0.001:
                    missingEvidence.append({
                        "type": ml_name,
                        "importance": int(min(99, max(5, lift * 5000))), # Scale up importance for visual bar
                        "lift": f"+{round(lift * 100, 1)}%",
                        "reason": f"ML projects a {round(lift * 100, 1)}% success probability increase if this is provided."
                    })
        
        missingEvidence.sort(key=lambda x: float(x["lift"].strip("+%")), reverse=True)
        
        advice = []
        if "delay" in req.facts.lower() or "late" in req.facts.lower():
            advice.append("Address the delay: Submit a 'Delay Condonation Affidavit' explaining the time gap to prevent limitation-based dismissal.")
        for ev in missingEvidence[:2]:
            advice.append(f"Crucial evidence gap: Provide {ev['type']} to strengthen your claim. This is projected to give a {ev['lift']} confidence lift according to our ML model.")
        if len(req.evidence) < 2:
            advice.append(f"Your evidence base ({len(req.evidence)} documents) is thin. Cases with 3+ evidence types have significantly higher success rates.")
        elif len(advice) == 0:
            advice.append("Your evidence profile aligns well with successful cases. Ensure all documents are properly authenticated and exhibited.")

        return {
            "prediction": pred_label,
            "confidence": confidence_pct,
            "explanation": llm_res.get("explanation", "Reasoning available in backend logs."),
            "factors": factors,
            "similarCases": similar_cases_ui,
            "alignment": {
                "consistency": "High" if confidence_pct > 75 else "Conflict",
                "score": final_score,
                "notes": re["method"]
            },
            "symbolic": {
                "signal": "Positive" if final_score > 0.6 else "Neutral",
                "score": final_score,
                "detected": 2
            },
            "relevantStatutes": dynamic_statutes,
            "primaryPivot": {
                "feature": missingEvidence[0]["type"] if missingEvidence else "None",
                "lift": missingEvidence[0]["lift"] if missingEvidence else "0%"
            },
            "counterfactuals": [
                {"scenario": "If missing evidence is produced", "impact": missingEvidence[0]["lift"] if missingEvidence else "+0%", "newOutcome": "Allowed"},
            ],
            "advice": advice,
            "contradictions": {
                "count": 1 if "delay" in req.facts.lower() else 0,
                "score": 0.15 if "delay" in req.facts.lower() else 0.0,
                "details": ["Significant time gap mentioned in facts."] if "delay" in req.facts.lower() else []
            },
            "evidenceDensity": (len(req.evidence) / len(EVIDENCE_OPTIONS)) if EVIDENCE_OPTIONS else 0.4,
            "missingEvidence": missingEvidence
        }

    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
