import numpy as np

from pipelines.pipeline1_old_cases.evidence_extractor import FINE_GRAINED_EVIDENCE_PATTERNS


COARSE_FEATURE_MAP = {
    "Medical/FSL Reports": "ev_medical",
    "Witness Testimony (PW)": "ev_witness",
    "Agreements & Contracts": "ev_contract",
    "Other Procedural Docs": "ev_procedural",
    "FIR/Seizure/PM Reports": "ev_memo",
    "Property Deeds": "ev_deeds",
}


def outcome_to_binary(outcome):
    label = str(outcome or "")
    if "Allowed/Success" in label:
        return 1
    if "Dismissed/Weak" in label:
        return 0
    return None


class LegalFeatureBuilder:
    """
    Canonical Phi(C, E, G, CT, R) builder used by both training and inference.
    """

    def __init__(self):
        self.coarse_feature_names = [
            "ev_medical",
            "ev_witness",
            "ev_contract",
            "ev_procedural",
            "ev_memo",
            "ev_deeds",
        ]
        self.fine_feature_names = [f"fg_{name}" for name in FINE_GRAINED_EVIDENCE_PATTERNS]
        self.feature_names = [
            "is_criminal",
            "is_service",
            "is_property",
            "is_matrimonial",
            "num_claims",
            "num_issues",
            "num_parties",
            "num_actions",
            *self.coarse_feature_names,
            *self.fine_feature_names,
            "evidence_density",
            "evidence_match_count",
            "missing_count",
            "gap_importance_sum",
            "gap_confidence_max",
            "gap_confidence_mean",
            "conflict_count",
            "conflict_score",
            "rag_allowed_ratio",
            "rag_dismissed_ratio",
            "rag_partial_ratio",
            "rag_unknown_ratio",
            "rag_weighted_outcome",
            "rag_similarity_mean",
            "rag_similarity_min",
        ]

    def _context_features(self, con_dict):
        case_type = str(con_dict.get("case_type", "")).lower()
        return {
            "is_criminal": int("criminal" in case_type),
            "is_service": int("service" in case_type),
            "is_property": int("property" in case_type or "land" in case_type),
            "is_matrimonial": int("matrimonial" in case_type or "divorce" in case_type),
            "num_claims": len(con_dict.get("claims", []) or []),
            "num_issues": len(con_dict.get("issues", []) or []),
            "num_parties": len(con_dict.get("parties", []) or []),
            "num_actions": len(con_dict.get("administrative_actions", []) or []),
        }

    def _evidence_features(self, con_dict):
        evidence_present = set(con_dict.get("evidence_present", []) or [])
        profile = con_dict.get("evidence_profile", {}) or {}
        fine_binary = profile.get("fine_binary", {}) or {}
        fine_counts = profile.get("fine_counts", {}) or {}

        coarse = {name: 0 for name in self.coarse_feature_names}
        for label, feature_name in COARSE_FEATURE_MAP.items():
            if label in evidence_present:
                coarse[feature_name] = 1

        fine = {name: 0 for name in self.fine_feature_names}
        for key in FINE_GRAINED_EVIDENCE_PATTERNS:
            fine[f"fg_{key}"] = int(fine_binary.get(key, 0))

        coarse_count = sum(coarse.values())
        fine_count = sum(fine.values())
        evidence_density = (coarse_count + fine_count) / max(len(self.coarse_feature_names) + len(self.fine_feature_names), 1)
        evidence_match_count = sum(int(v) for v in fine_counts.values())

        return {
            **coarse,
            **fine,
            "evidence_density": evidence_density,
            "evidence_match_count": evidence_match_count,
        }

    def _gap_features(self, missing_evidence):
        if not missing_evidence:
            return {
                "missing_count": 0,
                "gap_importance_sum": 0.0,
                "gap_confidence_max": 0.0,
                "gap_confidence_mean": 0.0,
            }

        scores = []
        for item in missing_evidence:
            raw_score = item.get("confidence_score") or item.get("importance") or "0%"
            try:
                score = float(str(raw_score).rstrip("%")) / 100.0
            except ValueError:
                score = 0.0
            scores.append(score)

        return {
            "missing_count": len(missing_evidence),
            "gap_importance_sum": float(sum(scores)),
            "gap_confidence_max": float(max(scores)) if scores else 0.0,
            "gap_confidence_mean": float(sum(scores) / len(scores)) if scores else 0.0,
        }

    def _conflict_features(self, contradictions):
        conflicts = contradictions.get("found_contradictions", []) or contradictions.get("contradictions", []) or []
        score = float(contradictions.get("contradiction_score", 0.0) or 0.0)
        return {
            "conflict_count": len(conflicts),
            "conflict_score": score,
        }

    def _retrieval_features(self, similar_cases):
        if not similar_cases:
            return {
                "rag_allowed_ratio": 0.0,
                "rag_dismissed_ratio": 0.0,
                "rag_partial_ratio": 0.0,
                "rag_unknown_ratio": 1.0,
                "rag_weighted_outcome": 0.5,
                "rag_similarity_mean": 0.0,
                "rag_similarity_min": 0.0,
            }

        total = len(similar_cases)
        distances = [float(case.get("distance", 0.0) or 0.0) for case in similar_cases]
        sims = [1.0 / (dist + 1e-6) for dist in distances]
        total_sim = sum(sims) or 1.0

        allowed = dismissed = partial = unknown = 0
        weighted_outcome_sum = 0.0

        for sim, case in zip(sims, similar_cases):
            label = str(case.get("outcome", "Unknown"))
            if "Allowed/Success" in label:
                allowed += 1
                weighted_outcome_sum += 1.0 * sim
            elif "Dismissed/Weak" in label:
                dismissed += 1
                weighted_outcome_sum += 0.0 * sim
            elif "Partial/Mixed" in label:
                partial += 1
                weighted_outcome_sum += 0.5 * sim
            else:
                unknown += 1
                weighted_outcome_sum += 0.5 * sim

        return {
            "rag_allowed_ratio": allowed / total,
            "rag_dismissed_ratio": dismissed / total,
            "rag_partial_ratio": partial / total,
            "rag_unknown_ratio": unknown / total,
            "rag_weighted_outcome": weighted_outcome_sum / total_sim,
            "rag_similarity_mean": float(np.mean(sims)),
            "rag_similarity_min": float(np.max(sims)),
        }

    def build_phi_dict(self, con_dict, similar_cases, missing_evidence, contradictions):
        phi = {}
        phi.update(self._context_features(con_dict))
        phi.update(self._evidence_features(con_dict))
        phi.update(self._gap_features(missing_evidence))
        phi.update(self._conflict_features(contradictions))
        phi.update(self._retrieval_features(similar_cases))

        for feature_name in self.feature_names:
            phi.setdefault(feature_name, 0.0)
        return phi

    def build_phi(self, con_dict, similar_cases, missing_evidence, contradictions):
        phi_dict = self.build_phi_dict(con_dict, similar_cases, missing_evidence, contradictions)
        phi = [phi_dict[name] for name in self.feature_names]
        return np.array(phi, dtype=float), self.feature_names
