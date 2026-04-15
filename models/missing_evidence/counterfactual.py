"""
Level 3: Counterfactual Evidence Importance via Marginal Contribution.

Given a trained XGBoost judgment model, computes:
    importance(evidence_i) = P(win | evidence_i=1) - P(win | evidence_i=0)

This is the "what missing evidence would most change the outcome?" signal.
It turns the recommendation engine from "what's typically present" into
"what would actually flip this specific case's predicted result."
"""

import os
import numpy as np
import pandas as pd
import joblib

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MODEL_PATH = os.path.join(BASE_DIR, "data", "processed", "judgment_model.joblib")


class CounterfactualImportance:
    """
    Computes per-feature marginal contribution for a specific case's Φ-vector.

    Given the trained XGBoost model and a case's feature dict, it:
    1. Predicts P(win) with current features
    2. For each MISSING evidence feature, sets it to 1 and re-predicts
    3. Returns Δ = P(win | feature=1) - P(win | feature=0)

    This is interpretable counterfactual importance — not SHAP approximation.
    It directly answers: "If this evidence were present, how much would the
    model's prediction change?"
    """

    def __init__(self, model_path=MODEL_PATH):
        self.model = None
        self.feature_names = None

        if os.path.exists(model_path):
            artifact = joblib.load(model_path)
            self.model = artifact["model"]
            self.feature_names = artifact["features"]

    @property
    def available(self):
        return self.model is not None

    def compute(self, phi_dict, missing_feature_keys=None):
        """
        Compute counterfactual importance for missing features.

        Args:
            phi_dict: The Φ-feature dictionary for the current case
            missing_feature_keys: List of feature keys to test.
                If None, tests all binary evidence features that are currently 0.

        Returns:
            Dict mapping feature_key → {
                "baseline_prob": float,       # P(win) with current features
                "counterfactual_prob": float,  # P(win) if this evidence were present
                "delta": float,               # counterfactual - baseline
                "lift_percent": float,         # delta as percentage points
            }
        """
        if not self.available:
            return {}

        # Build baseline feature vector
        baseline_row = {feat: float(phi_dict.get(feat, 0.0)) for feat in self.feature_names}
        X_baseline = pd.DataFrame([baseline_row])[self.feature_names]
        baseline_prob = float(self.model.predict_proba(X_baseline)[0][1])

        # Determine which features to test
        if missing_feature_keys is None:
            # Auto-detect: binary evidence features currently at 0
            missing_feature_keys = [
                f for f in self.feature_names
                if (f.startswith("ev_") or f.startswith("fg_"))
                and baseline_row.get(f, 0.0) == 0.0
            ]

        results = {}
        for feature_key in missing_feature_keys:
            if feature_key not in self.feature_names:
                continue

            # Create counterfactual: set this evidence to present
            cf_row = baseline_row.copy()
            cf_row[feature_key] = 1.0
            X_cf = pd.DataFrame([cf_row])[self.feature_names]
            cf_prob = float(self.model.predict_proba(X_cf)[0][1])

            delta = cf_prob - baseline_prob
            results[feature_key] = {
                "baseline_prob": round(baseline_prob, 4),
                "counterfactual_prob": round(cf_prob, 4),
                "delta": round(delta, 4),
                "lift_percent": round(delta * 100, 2),
            }

        return results

    def rank_missing_by_impact(self, phi_dict, missing_feature_keys=None, top_k=10):
        """
        Rank missing evidence by counterfactual impact (descending |Δ|).

        Returns list of (feature_key, delta, details) sorted by impact.
        """
        results = self.compute(phi_dict, missing_feature_keys)
        if not results:
            return []

        ranked = sorted(
            results.items(),
            key=lambda item: abs(item[1]["delta"]),
            reverse=True,
        )
        return ranked[:top_k]
