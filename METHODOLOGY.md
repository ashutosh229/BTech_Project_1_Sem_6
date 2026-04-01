# ⚖️ Methodology: Representation Learning for Judicial Reasoning

This system presents a novel approach to automated case analysis by mapping court judgments into a multi-modal feature space, identified as the **Phi-Vector ($\Phi_{Full}$)**. Instead of traditional raw text classification, we represent legal reasoning as the interaction between **Expected Evidence (KG)**, **Factual Claims (CON)**, and **Historical Precedents (RAG)**.

---

## 🏗️ 1. Representation Model: The Phi-Vector ($\Phi$)

The feature vector $\Phi$ is a 20-dimensional tensor synthesized from four modular intelligence blocks:

### A. Context Dynamics ($\Phi_{C}$)
Extracted using the **Case Object Notation (CON)** builder. 
- Features: `is_criminal`, `num_claims`, `num_issues`, `num_parties`.
- **Logic:** High `num_claims` vs. low `num_evidence` indicates high-risk cases.

### B. Evidentiary Distribution ($\Phi_{E}$)
Identified via **Clustering & Key-Point Extraction**.
- Features: 6-cluster multi-hot (Medical, Witness, Agreements, etc.).
- **Logic:** Certain case types (e.g., Murder 302) have a mandatory reliance on `cluster_0: Medical/FSL Reports`.

### C. The Gap Factor ($\Phi_{G}$)
Calculated via **Differential Analysis** against retrieved "Successful Siblings" (RAG).
- Features: `gap_count`, `max_gap_confidence`.
- **Logic:** Identifies the "Causal Missing Evidence" by comparing current failures to historical successes.

### D. Symbolic Conflict ($\Phi_{CT}$)
Flags **Narrative Inconsistencies** using symbolic rules and NLI triggers.
- Features: `conflict_count`, `conflict_score`.
- **Logic:** If `con["claims"]` mentions "recovery" but `con["evidence_present"]` lacks `cluster_4: Seizure Memo`, a conflict is flagged (Penalty 0.9).

---

## 🛰️ 2. Retrieval Intelligence (RAG)

Using the **InLegalBERT** (encoder-only transformer) architecture, we embed the factual summaries into a vector space $V$.
- **Index:** FAISS (FlatL2/IVF).
- **Retrieve:** Finds top-k successful and dismissed cases.
- **Synthesized Signal:** `rag_allowed_ratio` becomes a dominant predictive feature for the final model.

---

## 🧪 3. Evaluation & Ablation Study

We evaluate the system's reasoning depth by incrementally adding feature blocks to an **XGBoost Classifier**:
1. **Model A (Baseline):** Context only. (Context Bias).
2. **Model B (Structure):** Context + Evidence Presence.
3. **Model C (Reasoning):** Context + Evidence + Reasoning Gaps.
4. **Model D (Phi):** Full system with RAG and Contradiction checks.

**Key Research Question:** Does adding **Reasoning Gaps ($\Phi_{G}$)** and **Symbolic Conflict ($\Phi_{CT}$)** provide a statistically significant "lift" in judgment prediction compared to simple text retrieval?

---

## 📈 4. Jurisdictional Bias Detection

The system analyzes outcome distributions across all Indian High Courts to identify:
- **Strictness Bias:** Higher dismissal rates for specific evidence gaps.
- **Evidentiary Reliability:** Which courts place higher weight on **Witness Testimony (PW)** vs. **Documentary Evidence**.

---
*Methodology Version 1.2 (2026)*
