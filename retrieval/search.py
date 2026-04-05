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

    def _encode_query(self, text):
        with torch.no_grad():
            inputs = self.tokenizer(
                [text],
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors="pt",
            )
            outputs = self.model(**inputs)
            token_embeddings = outputs.last_hidden_state
            attention_mask = inputs["attention_mask"].unsqueeze(-1)
            masked_embeddings = token_embeddings * attention_mask
            pooled = masked_embeddings.sum(dim=1) / attention_mask.sum(dim=1).clamp(min=1)
            return pooled.cpu().numpy().astype(np.float32)

    def _load_or_build_outcomes(self, outcome_cache_path):
        if os.path.exists(outcome_cache_path):
            with open(outcome_cache_path, "r", encoding="utf-8") as f:
                cached = json.load(f)
            if isinstance(cached, dict) and "version" in cached and "outcomes" in cached:
                if cached["version"] == OUTCOME_CACHE_VERSION:
                    return cached["outcomes"]

        outcomes = {}
        for case_id in self.case_ids:
            json_path = Path(DATA_DIR) / f"{case_id}.json"
            if not json_path.exists():
                outcomes[case_id] = "Unknown"
                continue
            try:
                data = _load_json(json_path)
                outcomes[case_id] = extract_case_outcome(data)
            except Exception:
                outcomes[case_id] = "Unknown"

        os.makedirs(PROCESSED_DIR, exist_ok=True)
        with open(outcome_cache_path, "w", encoding="utf-8") as f:
            json.dump({"version": OUTCOME_CACHE_VERSION, "outcomes": outcomes}, f, indent=2)

        return outcomes

    def retrieve_similar_cases(self, con_dict, k=5):
        if not self.index:
            return []

        query_text = extract_case_query_text(con_dict)
        if not query_text:
            return []

        query_vector = self._encode_query(query_text)
        distances, indices = self.index.search(query_vector, k)

        results = []
        query_case_id = str(con_dict.get("case_id", "")).replace(".json", "")
        for rank, idx in enumerate(indices[0]):
            if idx < 0 or idx >= len(self.case_ids):
                continue

            case_id = self.case_ids[idx]
            if case_id == query_case_id:
                continue

            results.append({
                "case_id": case_id,
                "distance": float(distances[0][rank]),
                "outcome": self.case_outcomes.get(case_id, "Unknown"),
            })
        return results


def retrieve_similar_cases(con_dict, k=5):
    searcher = LegalSearcher()
    return searcher.retrieve_similar_cases(con_dict, k)
