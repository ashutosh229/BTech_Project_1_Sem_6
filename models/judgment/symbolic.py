import os
import pandas as pd
import json

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

class SymbolicLegalAligner:
    """
    Simulates Knowledge Graph reasoning by cross-referencing statutes
    with historical outcome distributions.
    """
    
    def __init__(self):
        self.statute_stats = {}
        self._load_symbolic_knowledge()
        
    def _load_symbolic_knowledge(self):
        path = os.path.join(BASE_DIR, "data", "processed", "case_statutes.csv")
        if os.path.exists(path):
            df = pd.read_csv(path)
            # Simple simulation: calculate win-rate per statute
            # In a real KG, this would involve triplet traversal (Statute --cite--> Outcome)
            if "statute" in df.columns and "outcome" in df.columns:
                stats = df.groupby("statute")["outcome"].apply(
                    lambda x: (x == "Allowed/Success").mean()
                ).to_dict()
                self.statute_stats = stats
                
    def align_statutes(self, con_dict):
        """
        Calculates the 'Statutory Strength' of the current case.
        """
        # Extract statutes from CON (claims or facts)
        # Note: This usually requires a NER pass, we simulate by checking claims
        detected = []
        for claim in con_dict.get("claims", []):
            text = str(claim.get("text", "")).upper()
            if "IPC" in text or "SECTION" in text:
                detected.append(text)
                
        if not detected or not self.statute_stats:
            return {"symbolic_score": 0.5, "signal": "Neutral"}
            
        # Match detected snippets to KG statistics
        scores = []
        for s in self.statute_stats:
            if any(s.upper() in d for d in detected):
                scores.append(self.statute_stats[s])
                
        if not scores:
            return {"symbolic_score": 0.5, "signal": "Indeterminate"}
            
        avg_score = sum(scores) / len(scores)
        return {
            "symbolic_score": round(avg_score, 4),
            "signal": "Positive" if avg_score > 0.6 else "Weak" if avg_score < 0.4 else "Neutral",
            "detected_count": len(scores)
        }
