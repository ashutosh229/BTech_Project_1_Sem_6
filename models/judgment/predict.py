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
                "stats": {"allowed": 0, "dismissed": 0, "partial": 0, "unknown": 0}
            }

        outcomes = [c.get("outcome", "Unknown") for c in similar_cases]
        weights = [1.0 / (float(c.get("distance", 0.0)) + 1e-6) for c in similar_cases]
        total = len(outcomes)
        total_weight = sum(weights) or 1.0

        allowed_count = outcomes.count("Allowed/Success")
        dismissed_count = outcomes.count("Dismissed/Weak")
        partial_count = outcomes.count("Partial/Mixed")
        unknown_count = total - allowed_count - dismissed_count - partial_count

        allowed_prob = (allowed_count / total) * 100
        dismissed_prob = (dismissed_count / total) * 100
        partial_prob = (partial_count / total) * 100

        weighted_allowed = 0.0
        weighted_dismissed = 0.0
        weighted_partial = 0.0
        for outcome, weight in zip(outcomes, weights):
            if outcome == "Allowed/Success":
                weighted_allowed += weight
            elif outcome == "Dismissed/Weak":
                weighted_dismissed += weight
            else:
                weighted_partial += weight

        # Decide final prediction
        if weighted_allowed > weighted_dismissed and weighted_allowed > weighted_partial:
            final = "Allowed/Success likely"
            confidence = (weighted_allowed / total_weight) * 100
        elif weighted_dismissed > weighted_allowed and weighted_dismissed > weighted_partial:
            final = "Dismissed/Weak likely"
            confidence = (weighted_dismissed / total_weight) * 100
        elif weighted_partial > 0:
            final = "Partial/Mixed likely"
            confidence = (weighted_partial / total_weight) * 100
        else:
            final = "Equally likely outcome"
            confidence = 50.0

        return {
            "prediction": final,
            "confidence": f"{confidence:.1f}%",
            "stats": {
                "allowed_percent": f"{allowed_prob:.1f}%",
                "dismissed_percent": f"{dismissed_prob:.1f}%",
                "partial_percent": f"{partial_prob:.1f}%",
                "unknown_percent": f"{(unknown_count / total) * 100:.1f}%",
            }
        }

def predict_judgment(con_dict, similar_cases):
    predictor = StatisticalPredictor()
    return predictor.predict(con_dict, similar_cases)
