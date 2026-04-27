"""
tests/test_core.py
─────────────────────────────────────────────────────────────────────────────
Basic unit tests for the Legal Intelligence System.
Run with:  python -m pytest tests/ -v
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest


# ─────────────────────────────────────────────────────────────────────────────
# 1. CON Builder
# ─────────────────────────────────────────────────────────────────────────────

class TestBuildCON:
    """Tests for con/builder.py — infer_case_type and build_con."""

    def setup_method(self):
        from con.builder import infer_case_type
        self.infer = infer_case_type

    def test_criminal_inference(self):
        text = "The accused filed a charge sheet. The FIR was registered. Prosecution filed."
        assert self.infer(text) == "Criminal"

    def test_matrimonial_inference(self):
        text = "The husband filed for divorce. Maintenance and custody of child in dispute."
        assert self.infer(text) == "Matrimonial"

    def test_property_inference(self):
        text = "The land title is disputed. Sale deed was executed. Partition of property."
        assert self.infer(text) == "Property"

    def test_service_inference(self):
        text = "The promotion was denied. Seniority list disputed. Departmental proceedings."
        assert self.infer(text) == "Service"

    def test_civil_fallback(self):
        # Sparse text — should fall back to Civil
        assert self.infer("The court heard the matter.") == "Civil"

    def test_build_con_schema_keys(self):
        """build_con must return all required CON schema keys."""
        from con.builder import build_con
        parsed = {
            "case_id": "test_case_001",
            "facts": "The accused was found with the weapon.",
            "issues": ["Whether prosecution proved guilt beyond doubt."],
            "claims": [{"id": "c1", "text": "Accused denies all charges."}],
            "parties": ["State of UP", "Ramesh"],
            "outcome": "Dismissed/Weak",
        }
        con = build_con(parsed)
        required_keys = {
            "case_id", "case_type", "parties", "issues", "claims",
            "administrative_actions", "evidence_present", "evidence_profile",
            "claim_outcomes", "outcome",
        }
        assert required_keys.issubset(set(con.keys()))
        assert con["case_id"] == "test_case_001"


# ─────────────────────────────────────────────────────────────────────────────
# 2. Outcome Extractor
# ─────────────────────────────────────────────────────────────────────────────

class TestExtractCaseOutcome:
    """Tests for retrieval/search.py — extract_case_outcome."""

    def setup_method(self):
        from retrieval.search import extract_case_outcome
        self.extract = extract_case_outcome

    def _make_data(self, conclusion_text):
        return {"elements_by_title": {"Conclusion": [{"text": conclusion_text}]}}

    def test_allowed(self):
        data = self._make_data("The petition is allowed with costs.")
        assert self.extract(data) == "Allowed/Success"

    def test_dismissed(self):
        data = self._make_data("The appeal is dismissed for lack of merit.")
        assert self.extract(data) == "Dismissed/Weak"

    def test_partly_allowed(self):
        data = self._make_data("The appeal is partly allowed. Sentence reduced.")
        assert self.extract(data) == "Partial/Mixed"

    def test_empty_returns_unknown(self):
        data = {"elements_by_title": {}}
        assert self.extract(data) == "Unknown"

    def test_terminal_line_dominates(self):
        """Explicit dismissal in the last 800 chars should override ancillary allowed phrase."""
        text = (
            "The application for exemption is allowed. "
            "However, on merits, the appeal is accordingly dismissed."
        )
        data = self._make_data(text)
        assert self.extract(data) == "Dismissed/Weak"


# ─────────────────────────────────────────────────────────────────────────────
# 3. Contradiction Engine
# ─────────────────────────────────────────────────────────────────────────────

class TestContradictionEngine:
    """Tests for models/contradiction/detect.py — ContradictionEngine."""

    def setup_method(self):
        from models.contradiction.detect import ContradictionEngine
        self.engine = ContradictionEngine()

    def _make_con(self, claims_text, evidence_present=None):
        return {
            "claims": [{"text": claims_text}],
            "evidence_present": evidence_present or [],
        }

    def test_no_contradictions(self):
        con = self._make_con("The petitioner filed timely.", ["Witness Testimony (PW)"])
        result = self.engine.analyze(con)
        assert result["contradiction_score"] == 0.0
        assert result["found_contradictions"] == []

    def test_delayed_fir_fires(self):
        con = self._make_con("There was a delayed FIR without explanation.")
        result = self.engine.analyze(con)
        rule_ids = [c["rule_id"] for c in result["found_contradictions"]]
        assert "delayed_fir" in rule_ids
        assert result["contradiction_score"] > 0

    def test_recovery_no_seizure_fires(self):
        con = self._make_con("The police claimed recovery of the weapon.")
        # No FIR/Seizure/PM Reports in evidence
        result = self.engine.analyze(con)
        rule_ids = [c["rule_id"] for c in result["found_contradictions"]]
        assert "recovery_no_seizure" in rule_ids

    def test_recovery_no_seizure_suppressed_when_evidence_present(self):
        con = self._make_con(
            "The police claimed recovery of the weapon.",
            evidence_present=["FIR/Seizure/PM Reports"],
        )
        result = self.engine.analyze(con)
        rule_ids = [c["rule_id"] for c in result["found_contradictions"]]
        assert "recovery_no_seizure" not in rule_ids

    def test_injury_no_medical_fires(self):
        con = self._make_con("The victim suffered grievous hurt in the attack.")
        result = self.engine.analyze(con)
        rule_ids = [c["rule_id"] for c in result["found_contradictions"]]
        assert "injury_no_medical" in rule_ids

    def test_score_normalised_correctly(self):
        """Score must be average severity, not severity/2 (which broke at >2 contradictions)."""
        # Trigger 3 rules: delayed_fir (0.8) + injury_no_medical (0.85) + alibi_no_witness (0.8)
        con = self._make_con(
            "There was a delayed FIR. The victim suffered injury. The accused claims an alibi."
        )
        result = self.engine.analyze(con)
        severities = [c["severity"] for c in result["found_contradictions"]]
        expected_score = sum(severities) / len(severities)
        assert abs(result["contradiction_score"] - expected_score) < 1e-4


# ─────────────────────────────────────────────────────────────────────────────
# 4. Argument Generator
# ─────────────────────────────────────────────────────────────────────────────

class TestArgumentGenerator:
    """Tests for models/arguments/generate.py."""

    def setup_method(self):
        from models.arguments.generate import generate_arguments, generate_case_improvement_plan
        self.gen_args = generate_arguments
        self.gen_plan = generate_case_improvement_plan

    def _make_judgment(self, allowed_prob=0.75):
        return {
            "prediction": "Allowed/Success likely",
            "confidence": f"{allowed_prob * 100:.1f}%",
            "probabilities": {"allowed": allowed_prob, "dismissed": 1 - allowed_prob},
        }

    def test_returns_required_keys(self):
        con = {"evidence_present": ["Medical/FSL Reports"], "claims": []}
        result = self.gen_args(con, [], {"found_contradictions": []}, self._make_judgment())
        assert {"summary", "arguments_for", "arguments_against", "confidence_note"}.issubset(result)

    def test_strong_prediction_adds_for_argument(self):
        con = {"evidence_present": [], "claims": []}
        result = self.gen_args(con, [], {"found_contradictions": []}, self._make_judgment(0.8))
        assert any("80.0%" in a for a in result["arguments_for"])

    def test_weak_prediction_adds_against_argument(self):
        con = {"evidence_present": [], "claims": []}
        result = self.gen_args(con, [], {"found_contradictions": []}, self._make_judgment(0.3))
        assert any("30.0%" in a for a in result["arguments_against"])

    def test_contradiction_appears_in_against(self):
        con = {"evidence_present": [], "claims": []}
        contradictions = {
            "found_contradictions": [{
                "rule_id": "delayed_fir",
                "type": "temporal_mismatch",
                "severity": 0.8,
                "detail": "Delayed FIR weakens the prosecution.",
            }]
        }
        result = self.gen_args(con, [], contradictions, self._make_judgment(0.6))
        assert any("Delayed FIR" in a for a in result["arguments_against"])

    def test_improvement_plan_sorted_by_priority(self):
        missing = [
            {"type": "Witness Testimony", "confidence_score": "45.0%", "strong_rate": 0.6, "weak_rate": 0.2},
            {"type": "Medical/FSL Report", "confidence_score": "80.0%", "strong_rate": 0.9, "weak_rate": 0.1},
        ]
        contradictions = {"found_contradictions": []}
        plan = self.gen_plan(missing, contradictions)
        assert plan[0]["priority"] == "HIGH"
        assert plan[0]["confidence"] > plan[1]["confidence"]


# ─────────────────────────────────────────────────────────────────────────────
# 5. Feature Builder
# ─────────────────────────────────────────────────────────────────────────────

class TestLegalFeatureBuilder:
    """Tests for con/feature_builder.py — LegalFeatureBuilder."""

    def setup_method(self):
        from con.feature_builder import LegalFeatureBuilder
        self.builder = LegalFeatureBuilder()

    def _make_con(self):
        return {
            "case_type": "Criminal",
            "parties": ["State", "Accused"],
            "issues": ["Whether conviction is sustainable."],
            "claims": [{"text": "Accused denies all charges."}],
            "administrative_actions": [],
            "evidence_present": ["Medical/FSL Reports", "Witness Testimony (PW)"],
            "evidence_profile": {"coarse_binary": {}, "fine_binary": {}, "fine_counts": {}},
        }

    def test_phi_dict_contains_all_feature_names(self):
        con = self._make_con()
        phi = self.builder.build_phi_dict(con, [], [], {"found_contradictions": [], "contradiction_score": 0.0})
        for name in self.builder.feature_names:
            assert name in phi, f"Missing feature: {name}"

    def test_rag_similarity_min_is_actual_min(self):
        """Regression test for the np.max → np.min bug (#1 in analysis)."""
        similar = [
            {"outcome": "Allowed/Success", "distance": 0.1},
            {"outcome": "Dismissed/Weak", "distance": 5.0},
            {"outcome": "Allowed/Success", "distance": 1.0},
        ]
        feats = self.builder._retrieval_features(similar)
        sims = [1.0 / (d + 1e-6) for d in [0.1, 5.0, 1.0]]
        assert abs(feats["rag_similarity_min"] - min(sims)) < 1e-5

    def test_no_similar_cases_returns_defaults(self):
        feats = self.builder._retrieval_features([])
        assert feats["rag_allowed_ratio"] == 0.0
        assert feats["rag_unknown_ratio"] == 1.0
        assert feats["rag_weighted_outcome"] == 0.5
