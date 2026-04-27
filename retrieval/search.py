import json
import os
import re
from pathlib import Path

import faiss
import numpy as np
import torch
from transformers import AutoModel, AutoTokenizer

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")

INDEX_PATH = os.path.join(DATA_DIR, "index", "legal_fact_index.faiss")
META_PATH = os.path.join(PROCESSED_DIR, "case_indices.json")
OUTCOME_CACHE_PATH = os.path.join(PROCESSED_DIR, "case_outcomes.json")
OUTCOME_CACHE_VERSION = 2


SUCCESS_PATTERNS = [
    r"\bpetition\s+is\s+allowed\b",
    r"\bappeal\s+is\s+allowed\b",
    r"\bapplication\s+is\s+allowed\b",
    r"\bsuit\s+is\s+decreed\b",
    r"\bdecreed\s+in\s+favour\s+of\b",
    r"\bissue\s+is\s+decided\s+in\s+favour\s+of\b",
    r"\bacquitted\b",
    r"\bconviction\s+is\s+set\s+aside\b",
    r"\bimpugned\s+order\s+is\s+set\s+aside\b",
    r"\brelief\s+is\s+granted\b",
]

FAILURE_PATTERNS = [
    r"\bpetition\s+is\s+dismissed\b",
    r"\bappeal\s+is\s+dismissed\b",
    r"\bapplication\s+is\s+dismissed\b",
    r"\bsuit\s+is\s+dismissed\b",
    r"\brejected\b",
    r"\bconvicted\b",
    r"\bconviction\s+is\s+upheld\b",
    r"\bview\s+taken.*must\s+be\s+upheld\b",
    r"\bnot\s+liable\s+to\s+be\s+interfered\s+with\b",
    r"\bstands\s+dismissed\b",
]

PARTIAL_PATTERNS = [
    r"\bpartly\s+allowed\b",
    r"\bpartially\s+allowed\b",
    r"\ballowed\s+in\s+part\b",
    r"\bdisposed\s+of\b",
    r"\bmodified\s+to\s+the\s+extent\b",
]


def _load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _join_elements(elements, keys):
    chunks = []
    for key in keys:
        if key in elements:
            chunks.append(" ".join(item.get("text", "") for item in elements[key]))
    return " ".join(chunks)


def _normalize(text):
    text = (text or "").lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_case_outcome(data):
    """
    Heuristic ground-truth outcome extractor from raw judgment JSON.
    Returns one of:
    - Allowed/Success
    - Dismissed/Weak
    - Partial/Mixed
    - Unknown
    """
    elements = data.get("elements_by_title", {})
    terminal_text = _join_elements(
        elements,
        ["Conclusion", "Judgment", "Judgement", "Final Order"],
    )
    candidate_text = terminal_text if terminal_text.strip() else _join_elements(
        elements,
        ["Court's Reasoning", "Analysis of the law", "Analysis"],
    )
    text = _normalize(candidate_text)

    if not text:
        return "Unknown"

    partial_hit = any(re.search(p, text) for p in PARTIAL_PATTERNS)
    success_hit = any(re.search(p, text) for p in SUCCESS_PATTERNS)
    failure_hit = any(re.search(p, text) for p in FAILURE_PATTERNS)

    terminal_tail = text[-800:]
    terminal_success_hit = any(re.search(p, terminal_tail) for p in SUCCESS_PATTERNS)
    terminal_failure_hit = any(re.search(p, terminal_tail) for p in FAILURE_PATTERNS)

    # Explicit dismissal/rejection of the main matter should dominate
    # ancillary phrases like "application is allowed".
    if re.search(r"\b(suit|appeal|petition|revision|complaint|case)\s+is\s+(accordingly\s+)?dismissed\b", terminal_tail):
        return "Dismissed/Weak"
    if re.search(r"\b(suit|appeal|petition|revision|complaint|case)\s+is\s+(hereby\s+)?rejected\b", terminal_tail):
        return "Dismissed/Weak"
    if re.search(r"\b(suit|appeal|petition|revision|complaint)\s+is\s+(hereby\s+)?allowed\b", terminal_tail):
        return "Allowed/Success"

    if partial_hit:
        return "Partial/Mixed"
    if success_hit and not failure_hit:
        return "Allowed/Success"
    if failure_hit and not success_hit:
        return "Dismissed/Weak"
    if success_hit and failure_hit:
        # If both occur, prefer the explicit tail-end decision line.
        if terminal_success_hit and not terminal_failure_hit:
            return "Allowed/Success"
        if terminal_failure_hit and not terminal_success_hit:
            return "Dismissed/Weak"
        return "Partial/Mixed"
    return "Unknown"


def extract_case_query_text(con_dict):
    """
    Build a semantically meaningful retrieval query from structured CON.
    This is better than falling back to case_id when claims are sparse.
    """
    parts = []
    if con_dict.get("case_type"):
        parts.append(str(con_dict["case_type"]))

    for issue in con_dict.get("issues", []):
        if isinstance(issue, dict):
            parts.extend(str(v) for v in issue.values() if isinstance(v, str))
        elif isinstance(issue, str):
            parts.append(issue)

    for claim in con_dict.get("claims", []):
        if isinstance(claim, dict):
            for key in ["claim_type", "subject", "polarity", "text"]:
                value = claim.get(key)
                if isinstance(value, str) and value.strip():
                    parts.append(value)
        elif isinstance(claim, str):
            parts.append(claim)

    parts.extend(con_dict.get("evidence_present", []))

    query_text = _normalize(" ".join(parts))
    if query_text:
        return query_text

    return _normalize(str(con_dict.get("case_id", "")))


class LegalSearcher:
    """
    FAISS retrieval over factual embeddings, with real corpus-backed metadata.
    """

    def __init__(self, index_path=INDEX_PATH, meta_path=META_PATH, outcome_cache_path=OUTCOME_CACHE_PATH):
        self.tokenizer = AutoTokenizer.from_pretrained("law-ai/InLegalBERT", local_files_only=True)
        self.model = AutoModel.from_pretrained("law-ai/InLegalBERT", local_files_only=True)
        self.model.eval()
        self.case_ids = []
        self.case_outcomes = {}

        # New: Support for Importance-Weighted Reranking
        self.corpus_phi = {}
        self.weights = {}
        self._load_reranking_data()

        if os.path.exists(index_path):
            self.index = faiss.read_index(index_path)
            print(f"📦 Loaded FAISS index from {index_path}")
        else:
            self.index = None
            print(f"⚠️ FAISS index not found at {index_path}")

        if os.path.exists(meta_path):
            with open(meta_path, "r", encoding="utf-8") as f:
                self.case_ids = json.load(f)
            print(f"📝 Loaded {len(self.case_ids)} case mappings.")
        else:
            print(f"⚠️ Metadata mapping not found at {meta_path}")

        self.case_outcomes = self._load_or_build_outcomes(outcome_cache_path)

    def _load_reranking_data(self):
        # 1. Load Feature Importances (Gains)
        weights_path = os.path.join(BASE_DIR, "outputs", "feature_importances.json")
        if os.path.exists(weights_path):
            with open(weights_path, "r") as f:
                self.weights = json.load(f)
        
        # 2. Load Corpus PHI Vectors
        phi_path = os.path.join(DATA_DIR, "processed", "corpus_intelligence_summary.csv")
        if os.path.exists(phi_path):
            try:
                import pandas as pd
                df = pd.read_csv(phi_path)
                if df.empty:
                    return
                # Map case_id -> phi_dict
                features = list(self.weights.keys()) if self.weights else []
                if not features:
                    # Fallback if no weights found yet
                    features = [c for c in df.columns if c not in ["case_id", "true_outcome", "case_type"]]

                for _, row in df.iterrows():
                    cid = str(row["case_id"])
                    self.corpus_phi[cid] = row[features].to_dict()
            except Exception:
                pass  # CSV not ready yet (first run) — skip reranking

    def _load_or_build_outcomes(self, cache_path):
        """
        Load case outcomes from cache, or build by scanning all raw JSON files.
        Cache is versioned — if version mismatch, rebuilds automatically.
        """
        # Try loading from cache first
        if os.path.exists(cache_path):
            try:
                with open(cache_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict) and data.get("_version") == OUTCOME_CACHE_VERSION:
                    outcomes = {k: v for k, v in data.items() if not k.startswith("_")}
                    print(f"📋 Loaded {len(outcomes)} cached case outcomes.")
                    return outcomes
            except Exception:
                pass  # Fall through to rebuild

        # Build from scratch by scanning data directory
        print("🔍 Building case outcome cache from raw JSON files (one-time)...")
        outcomes = {}
        json_files = list(Path(DATA_DIR).rglob("*.json"))
        for path in json_files:
            # Skip processed/index subdirs
            if any(part in path.parts for part in ("processed", "index", "dataset", "results")):
                continue
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                outcomes[path.stem] = extract_case_outcome(data)
            except Exception:
                continue

        # Save cache with version marker
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        cache_data = {"_version": OUTCOME_CACHE_VERSION}
        cache_data.update(outcomes)
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(cache_data, f)

        print(f"✅ Built and cached outcomes for {len(outcomes)} cases → {cache_path}")
        return outcomes

    def _calculate_legal_alignment(self, query_phi, target_phi):
        """
        Computes weighted Φ-overlap between two cases.
        """
        if not self.weights: return 0.5
        
        score = 0.0
        total_weight = 0.0
        for feat, weight in self.weights.items():
            if weight <= 0: continue
            q_val = query_phi.get(feat, 0.0)
            t_val = target_phi.get(feat, 0.0)
            
            # Simple match for binary features; abs diff for continuous
            if feat.startswith(("ev_", "fg_", "is_")):
                match = 1.0 if (q_val > 0.5) == (t_val > 0.5) else 0.0
            else:
                match = 1.0 - min(abs(q_val - t_val), 1.0)
            
            score += match * weight
            total_weight += weight
            
        return score / total_weight if total_weight > 0 else 0.5

    def _encode_query(self, text: str) -> "np.ndarray":
        """Encode a single query string into a FAISS-compatible (1, dim) float32 vector."""
        with torch.no_grad():
            inputs = self.tokenizer(
                text,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors="pt",
            )
            outputs = self.model(**inputs)
            mask = inputs["attention_mask"].unsqueeze(-1)
            pooled = (outputs.last_hidden_state * mask).sum(dim=1) / mask.sum(dim=1).clamp(min=1)
        return pooled.cpu().numpy().astype("float32")

    def retrieve_similar_cases(self, con_dict, k=5, strategy="balanced"):

        if not self.index:
            return []

        query_text = extract_case_query_text(con_dict)
        if not query_text:
            return []

        # 1. Broad Vector Search (Expand candidates to allow for filtering/diversification)
        query_vector = self._encode_query(query_text)
        candidates_k = k * 10
        distances, indices = self.index.search(query_vector, candidates_k)

        # 2. Extract Query Φ for Alignment
        from con.feature_builder import LegalFeatureBuilder
        builder = LegalFeatureBuilder()
        query_phi = builder.build_phi_dict(con_dict, [], [], {})

        results = []
        query_case_id = str(con_dict.get("case_id", "")).replace(".json", "")
        
        for rank, idx in enumerate(indices[0]):
            if idx < 0 or idx >= len(self.case_ids):
                continue

            case_id = self.case_ids[idx]
            if case_id == query_case_id:
                continue

            d = float(distances[0][rank])
            vec_sim = 1.0 / (1.0 + d)

            target_phi = self.corpus_phi.get(case_id, {})
            legal_sim = self._calculate_legal_alignment(query_phi, target_phi) if target_phi else 0.5
            outcome = self.case_outcomes.get(case_id, "Unknown")

            # --- Diversification Logic ---
            # Strategy: "balanced" (Current), "fact-similar", "evidence-similar", "outcome-diverse"
            diversity_multiplier = 1.0
            if strategy == "fact-similar":
                diversity_multiplier = 1.5 if vec_sim > 0.7 else 1.0
            elif strategy == "evidence-similar":
                diversity_multiplier = 1.5 if legal_sim > 0.7 else 1.0
            elif strategy == "outcome-diverse":
                # Prioritize cases with a DIFFERENT outcome than the predicted/likely one
                # Since we don't have prediction here, we can't strictly diversify by outcome
                # unless we pass a 'target_outcome'. Let's just ensure we have a mix.
                pass

            final_sim = ((0.4 * vec_sim) + (0.6 * legal_sim)) * diversity_multiplier

            results.append({
                "case_id": case_id,
                "distance": d,
                "vector_similarity": vec_sim,
                "legal_alignment": legal_sim,
                "final_score": final_sim,
                "outcome": outcome,
            })

        results = sorted(results, key=lambda x: x["final_score"], reverse=True)

        # Final step: If strategy is 'balanced', ensure we have a mix of outcomes if possible
        if strategy == "balanced":
            balanced_results = []
            outcomes_seen = set()
            for res in results:
                if res["outcome"] not in outcomes_seen or len(balanced_results) < k // 2:
                    balanced_results.append(res)
                    outcomes_seen.add(res["outcome"])
                if len(balanced_results) == k:
                    break
            if len(balanced_results) > 0:
                return balanced_results

        return results[:k]



def retrieve_similar_cases(con_dict, k=5, strategy="balanced"):
    searcher = LegalSearcher()
    return searcher.retrieve_similar_cases(con_dict, k, strategy)
