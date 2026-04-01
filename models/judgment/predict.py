import os
import json

class StatisticalPredictor:
    """
    Step 7: Judgment = Retrieval Statistics (Minimal Approach).
    Calculates outcome probability based purely on retrieval patterns.
    """
    def predict(self, con_dict, similar_cases):
        """No ML yet. We analyze outcomes of RAG counterparts."""
        if not similar_cases:
            return {
                "prediction": "Inconclusive",
                "confidence": "0.0%",
                "stats": {"allowed": 0, "dismissed": 0}
            }

        outcomes = [c.get("outcome", "Unknown") for c in similar_cases]
        
        # Mapping variations for consistency
        allowed_count = outcomes.count("Allowed/Success")
        dismissed_count = outcomes.count("Dismissed/Weak")
        total = len(outcomes)

        allowed_prob = (allowed_count / total) * 100
        dismissed_prob = (dismissed_count / total) * 100
        
        # Decide final prediction
        if allowed_prob > dismissed_prob:
            final = "Allowed/Success likely"
            confidence = allowed_prob
        elif dismissed_prob > allowed_prob:
            final = "Dismissed/Weak likely"
            confidence = dismissed_prob
        else:
            final = "Equally likely outcome"
            confidence = 50.0

        return {
            "prediction": final,
            "confidence": f"{confidence:.1f}%",
            "stats": {
                "allowed_percent": f"{allowed_prob:.1f}%",
                "dismissed_percent": f"{dismissed_prob:.1f}%"
            }
        }

def predict_judgment(con_dict, similar_cases):
    predictor = StatisticalPredictor()
    return predictor.predict(con_dict, similar_cases)
