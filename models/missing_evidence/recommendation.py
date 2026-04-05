import json
import math
import os
from collections import Counter, defaultdict

import numpy as np
import pandas as pd

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")

EVIDENCE_MATRIX_PATH = os.path.join(PROCESSED_DIR, "real_evidence_matrix.csv")
WEAK_CASE_SCORES_PATH = os.path.join(PROCESSED_DIR, "weak_case_scores.json")
WEAK_CASE_INDEX_PATH = os.path.join(PROCESSED_DIR, "failed_cases_index.json")
RANKING_PATH = os.path.join(OUTPUTS_DIR, "causal_ranking.json")

COARSE_LABEL_MAP = {
    "ev_medical": "Medical/FSL Reports",
    "ev_witness": "Witness Testimony (PW)",
    "ev_contract": "Agreements & Contracts",
    "ev_procedural": "Other Procedural Docs",
    "ev_memo": "FIR/Seizure/PM Reports",
    "ev_deeds": "Property Deeds",
}


def _safe_div(num, den):
    return float(num) / float(den) if den else 0.0


def _sigmoid(x):
    return 1.0 / (1.0 + math.exp(-x))


class EvidenceRecommender:
    """
    Retrieval-conditioned missing-evidence ranker with:
    - fine-grained evidence coverage and counts
    - probabilistic weak/strong neighborhood modeling
    - prevalence + intensity + log-odds + effect-size signals
    - dynamic query-conditioned weighting instead of static alpha/beta
    """

    def __init__(
        self,
        evidence_matrix_path=EVIDENCE_MATRIX_PATH,
        weak_case_scores_path=WEAK_CASE_SCORES_PATH,
        weak_case_index_path=WEAK_CASE_INDEX_PATH,
        ranking_path=RANKING_PATH,
    ):
        self.lookup, self.label_lookup, self.binary_feature_columns = self._load_evidence_lookup(evidence_matrix_path)
        self.weak_scores = self._load_weak_scores(weak_case_scores_path, weak_case_index_path)
        self.global_importance = self._load_global_importance(ranking_path)

    def _normalize_case_id(self, case_id):
        if not case_id:
            return ""
        return str(case_id).replace(".json", "")

    def _load_evidence_lookup(self, path):
        if not os.path.exists(path):
            return {}, {}, []

        df = pd.read_csv(path)
        coarse_binary = [c for c in df.columns if c.startswith("ev_") and c != "ev_total_matches"]
        fine_binary = [c for c in df.columns if c.startswith("fg_") and not c.startswith("fgcnt_")]
        fine_count = [c for c in df.columns if c.startswith("fgcnt_")]
        label_lookup = {}

        for col in coarse_binary:
            label_lookup[col] = COARSE_LABEL_MAP.get(col, col)
        for col in fine_binary:
            label_lookup[col] = col.replace("fg_", "").replace("_", " ").title()
        for col in fine_count:
            stem = col.replace("fgcnt_", "")
            label_lookup[col] = stem.replace("_", " ").title()

        lookup = {}
        for _, row in df.iterrows():
            case_id = str(row["case_id"])
            binary = {}
            counts = {}
            for col in coarse_binary + fine_binary:
                binary[col] = int(row.get(col, 0))
            for col in fine_count:
                counts[col] = float(row.get(col, 0.0))
            lookup[case_id] = {
                "binary": binary,
                "counts": counts,
                "total_matches": float(row.get("ev_total_matches", 0.0)),
            }

        return lookup, label_lookup, coarse_binary + fine_binary

    def _load_weak_scores(self, weak_scores_path, weak_index_path):
        if os.path.exists(weak_scores_path):
            with open(weak_scores_path, "r", encoding="utf-8") as f:
                scores = json.load(f)
            return {
                case_id: float(meta.get("weak_probability", meta.get("hard_weak", 0.0)))
                for case_id, meta in scores.items()
            }

        if os.path.exists(weak_index_path):
            with open(weak_index_path, "r", encoding="utf-8") as f:
                weak_list = json.load(f)
            weak_ids = {item["case_id"] for item in weak_list if isinstance(item, dict) and item.get("case_id")}
            return {case_id: (1.0 if case_id in weak_ids else 0.0) for case_id in self.lookup}

        return {}

    def _load_global_importance(self, ranking_path):
        if not os.path.exists(ranking_path):
            return {}
        with open(ranking_path, "r", encoding="utf-8") as f:
            ranking = json.load(f)
        importance = {}
        for row in ranking:
            feature_key = row.get("feature_key")
            score = float(row.get("Importance Score (%)", 0.0)) / 100.0
            if feature_key:
                importance[feature_key] = score
        return importance

    def _current_feature_presence(self, con_dict):
        profile = con_dict.get("evidence_profile", {}) or {}
        coarse_present = set(con_dict.get("evidence_present", []) or [])
        fine_binary = profile.get("fine_binary", {}) or {}
        fine_counts = profile.get("fine_counts", {}) or {}

        present_binary = set()
        present_labels = set()
        present_counts = defaultdict(float)

        for key, label in COARSE_LABEL_MAP.items():
            if label in coarse_present:
                present_binary.add(key)
                present_labels.add(label)
                present_counts[key] = 1.0

        for fine_name, value in fine_binary.items():
            if int(value) == 1:
                binary_key = f"fg_{fine_name}"
                count_key = f"fgcnt_{fine_name}"
                present_binary.add(binary_key)
                present_labels.add(fine_name.replace("_", " ").title())
                present_counts[binary_key] = float(fine_counts.get(fine_name, 1.0))

        total_present = sum(1 for _ in present_binary)
        return present_binary, present_labels, present_counts, total_present

    def _dynamic_weights(self, query_feature_count, neighbor_count, strong_mass, weak_mass, unknown_ratio):
        sparsity = 1.0 - min(query_feature_count / 12.0, 1.0)
        neighborhood_balance = 1.0 - abs(_safe_div(strong_mass, strong_mass + weak_mass) - 0.5) * 2.0
        retrieval_reliability = max(0.0, 1.0 - unknown_ratio)

        prevalence_weight = 0.18 + 0.18 * retrieval_reliability + 0.10 * sparsity
        intensity_weight = 0.12 + 0.20 * sparsity
        odds_weight = 0.16 + 0.16 * neighborhood_balance
        effect_weight = 0.12 + 0.10 * neighborhood_balance
        global_weight = max(0.08, 1.0 - (prevalence_weight + intensity_weight + odds_weight + effect_weight))

        weights = np.asarray([prevalence_weight, intensity_weight, odds_weight, effect_weight, global_weight], dtype=float)
        weights = weights / weights.sum()
        return {
            "prevalence": float(weights[0]),
            "intensity": float(weights[1]),
            "log_odds": float(weights[2]),
            "effect": float(weights[3]),
            "global": float(weights[4]),
        }

    def _count_key(self, feature_key):
        if feature_key.startswith("fg_"):
            return feature_key.replace("fg_", "fgcnt_", 1)
        return None

    def _generate_reason(self, label, feature_key, score, stats, support_cases):
        parts = []
        if stats["prevalence_diff"] > 0:
            parts.append(
                f"prevalence is higher in strong neighbors ({stats['strong_rate']:.2f}) than weak neighbors ({stats['weak_rate']:.2f})"
            )
        if stats["intensity_diff"] > 0:
            parts.append(
                f"when present, its average intensity is higher in strong neighbors ({stats['strong_intensity']:.2f}) than weak neighbors ({stats['weak_intensity']:.2f})"
            )
        if stats["log_odds"] > 0:
            parts.append(f"the smoothed log-odds signal is positive ({stats['log_odds']:.2f})")
        if stats["effect_size"] > 0:
            parts.append(f"the standardized effect size is positive ({stats['effect_size']:.2f})")
        if stats["global_importance"] > 0:
            parts.append(f"it is globally ranked important in the corpus ({stats['global_importance']:.2f})")

        if not parts:
            parts.append("it improves the local retrieved-case evidence profile")

        case_phrase = ""
        if support_cases:
            case_phrase = f" Strongest supporting retrieved cases: {', '.join(support_cases[:3])}."

        return (
            f"{label} is recommended because " + "; ".join(parts) +
            f". Final dynamic score={score:.2f}.{case_phrase}"
        )

    def recommend(self, con_dict, similar_cases):
        if not similar_cases:
            return []

        present_binary, present_labels, present_counts, query_feature_count = self._current_feature_presence(con_dict)

        prevalence_strong = Counter()
        prevalence_weak = Counter()
        weighted_prev_strong = Counter()
        weighted_prev_weak = Counter()
        intensity_strong = Counter()
        intensity_weak = Counter()
        weighted_intensity_strong = Counter()
        weighted_intensity_weak = Counter()
        support_cases = defaultdict(list)

        total_strong_mass = 0.0
        total_weak_mass = 0.0
        unknown_mass = 0.0

        valid_neighbors = 0
        for case in similar_cases:
            case_id = self._normalize_case_id(case.get("case_id"))
            if not case_id or case_id not in self.lookup:
                continue

            valid_neighbors += 1
            record = self.lookup[case_id]
            weak_prob = float(self.weak_scores.get(case_id, 0.5))
            distance = float(case.get("distance", 1.0))
            similarity = 1.0 / (distance + 1e-6)

            strong_mass = (1.0 - weak_prob) * similarity
            weak_mass = weak_prob * similarity
            total_strong_mass += strong_mass
            total_weak_mass += weak_mass
            if case.get("outcome") == "Unknown":
                unknown_mass += similarity

            for feature_key, present in record["binary"].items():
                count_key = self._count_key(feature_key)
                count_value = float(record["counts"].get(count_key, 0.0)) if count_key else float(present)
                prevalence_strong[feature_key] += present * (1.0 - weak_prob)
                prevalence_weak[feature_key] += present * weak_prob
                weighted_prev_strong[feature_key] += present * strong_mass
                weighted_prev_weak[feature_key] += present * weak_mass

                intensity_strong[feature_key] += count_value * (1.0 - weak_prob)
                intensity_weak[feature_key] += count_value * weak_prob
                weighted_intensity_strong[feature_key] += count_value * strong_mass
                weighted_intensity_weak[feature_key] += count_value * weak_mass

                if present and len(support_cases[feature_key]) < 5:
                    support_cases[feature_key].append(case_id)

        if total_strong_mass <= 0 or valid_neighbors == 0:
            return []

        unknown_ratio = _safe_div(unknown_mass, total_strong_mass + total_weak_mass)
        weights = self._dynamic_weights(query_feature_count, valid_neighbors, total_strong_mass, total_weak_mass, unknown_ratio)
        recommendations = []

        for feature_key in self.binary_feature_columns:
            label = self.label_lookup.get(feature_key, feature_key)
            if feature_key in present_binary or label in present_labels:
                continue

            count_key = self._count_key(feature_key)
            global_binary = self.global_importance.get(feature_key, 0.0)
            global_count = self.global_importance.get(count_key, 0.0) if count_key else 0.0
            global_importance = max(global_binary, global_count)

            strong_rate = _safe_div(prevalence_strong[feature_key], valid_neighbors)
            weak_rate = _safe_div(prevalence_weak[feature_key], valid_neighbors)
            prevalence_diff = strong_rate - weak_rate

            weighted_strong_rate = _safe_div(weighted_prev_strong[feature_key], total_strong_mass)
            weighted_weak_rate = _safe_div(weighted_prev_weak[feature_key], total_weak_mass)
            weighted_prevalence_diff = weighted_strong_rate - weighted_weak_rate

            strong_intensity = _safe_div(weighted_intensity_strong[feature_key], total_strong_mass)
            weak_intensity = _safe_div(weighted_intensity_weak[feature_key], total_weak_mass)
            intensity_diff = strong_intensity - weak_intensity

            # Smoothed log-odds on weighted support.
            alpha = 1.0
            strong_present = weighted_prev_strong[feature_key] + alpha
            strong_absent = max(total_strong_mass - weighted_prev_strong[feature_key], 0.0) + alpha
            weak_present = weighted_prev_weak[feature_key] + alpha
            weak_absent = max(total_weak_mass - weighted_prev_weak[feature_key], 0.0) + alpha
            log_odds = math.log((strong_present / strong_absent) / (weak_present / weak_absent))

            pooled_var = max(
                ((strong_intensity + 1e-6) + (weak_intensity + 1e-6)) / 2.0,
                1e-6,
            )
            effect_size = intensity_diff / math.sqrt(pooled_var)

            prevalence_signal = max(prevalence_diff, 0.0) + 0.5 * max(weighted_prevalence_diff, 0.0)
            intensity_signal = max(_sigmoid(intensity_diff) - 0.5, 0.0) * 2.0
            log_odds_signal = max(_sigmoid(log_odds) - 0.5, 0.0) * 2.0
            effect_signal = max(_sigmoid(effect_size) - 0.5, 0.0) * 2.0

            score = (
                weights["prevalence"] * prevalence_signal
                + weights["intensity"] * intensity_signal
                + weights["log_odds"] * log_odds_signal
                + weights["effect"] * effect_signal
                + weights["global"] * global_importance
            )

            # Require at least one local positive signal.
            if max(prevalence_signal, intensity_signal, log_odds_signal, effect_signal) <= 0:
                continue
            if score <= 0:
                continue

            stats = {
                "strong_rate": round(strong_rate, 4),
                "weak_rate": round(weak_rate, 4),
                "weighted_strong_rate": round(weighted_strong_rate, 4),
                "weighted_weak_rate": round(weighted_weak_rate, 4),
                "strong_intensity": round(strong_intensity, 4),
                "weak_intensity": round(weak_intensity, 4),
                "prevalence_diff": round(prevalence_diff, 4),
                "weighted_prevalence_diff": round(weighted_prevalence_diff, 4),
                "intensity_diff": round(intensity_diff, 4),
                "log_odds": round(log_odds, 4),
                "effect_size": round(effect_size, 4),
                "global_importance": round(global_importance, 4),
            }
            reason = self._generate_reason(label, feature_key, score, stats, support_cases[feature_key])

            recommendations.append(
                {
                    "feature_key": feature_key,
                    "count_feature_key": count_key,
                    "type": label,
                    "confidence_score": f"{score * 100:.1f}%",
                    "importance": f"{score * 100:.1f}%",
                    "support_count": len(support_cases[feature_key]),
                    "dynamic_weights": {k: round(v, 4) for k, v in weights.items()},
                    **stats,
                    "reason": reason,
                    "supporting_cases": support_cases[feature_key][:5],
                }
            )

        recommendations.sort(
            key=lambda row: (
                float(row["confidence_score"].rstrip("%")),
                row["support_count"],
                row["weighted_strong_rate"],
                row["strong_intensity"],
            ),
            reverse=True,
        )
        return recommendations


def find_missing_evidence(con_dict, similar_cases):
    recommender = EvidenceRecommender()
    return recommender.recommend(con_dict, similar_cases)
