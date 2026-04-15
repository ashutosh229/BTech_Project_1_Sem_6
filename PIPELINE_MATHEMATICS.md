# ⚖️ Mathematical & Methodological Pipeline Documentation

This document provides a highly comprehensive, mathematical, and algorithmic breakdown of the Legal Intelligence System's evidence and reasoning pipeline. It details the exact formulations, weighting mechanisms, and machine learning principles employed across the codebase.

---

## 1. Probabilistic Weak Case Detection (`weak_case_detection.py`)

The first step in the induction phase is isolating cases that failed specifically due to **evidentiary weakness**, without relying on external annotated datasets. This is achieved via **Weak Supervision and Pseudo-labeling**.

### A. Seed Identification
The system searches the joined text (Facts + Reasoning + Conclusion) for deterministic regex markers (e.g., `"benefit of doubt"`, `"insufficient evidence"`) to label cases as `weak_seed` ($W_s$) or `success_seed` ($S_s$).
- $y_{seed} = 1$ if ($W_s = 1$ and $S_s = 0$)
- $y_{anti\_seed} = 1$ if ($S_s = 1$ and $W_s = 0$)

### B. TF-IDF Feature Extraction
The raw text is vectorized using a concatenated TF-IDF representation:
- **Word n-grams (1,2)**: $\max\_df$ restrictions, yielding $X_{word}$
- **Character n-grams (3,5)**: $X_{char}$
- $X = [X_{word}, X_{char}]$ combined via Compressed Sparse Row (CSR) matrix.

### C. Refined Logistic Regression Ensemble
1. **Base Model:** A Logistic Regression model ($M_{base}$) is trained on $X$ using the $y_{seed}$ targets.
   $$ P_{base} = M_{base}.\text{predict\_proba}(X)[:, 1] $$
2. **Pseudo-Label Expansion:** Only highly confident predictions ($P_{base} \ge 0.85$ or $P_{base} \le 0.15$) are kept. A second, refined model ($M_{refined}$) is trained purely on these high-confidence examples to smooth out the noise from the noisy regex seeds.
   $$ P_{refined} = M_{refined}.\text{predict\_proba}(X)[:, 1] $$

### D. Final Calibrated Probability
The models are ensembled into a final continuous "Weakness" probability:
$$ P_{raw} = (0.40 \times P_{base}) + (0.45 \times P_{refined}) + (0.15 \times y_{seed}) $$

Heuristic adjustments are applied:
- **Seed Boost:** Adds $0.18$ if $W_s$ is present, subtracts $0.12$ if $S_s$ is present.
- **Lexical Penalty:** Subtracts $0.08$ if *both* markers are found (ambiguous).
$$ P_{weak} = \min(1.0, \max(0.0, P_{raw} + \text{Boost} - \text{Penalty})) $$

---

## 2. Ensemble Causal Importance Ranking (`importance.py`)

This step mathematically isolates which canonical pieces of evidence (Medical, Witness, Contradictions) hold the heaviest statistical weight in shifting an outcome from "Weak" to "Success".

### A. The Six-Pillar Component Normalization
A global score is constructed by blending 6 heterogeneous metrics. Each metric array $V$ is first Min-Max normalized to safely sum them:
$$ Norm(V) = \frac{V - V_{min}}{V_{max} - V_{min}} $$

The 6 components for each evidence feature $X_i$:
1. **Gradient Boosting ($GB$):** Feature importance from `GradientBoostingClassifier` (depth=3, trees=250).
2. **Random Forest ($RF$):** Feature importance from `RandomForestClassifier` (depth=10, trees=250).
3. **Mutual Information ($MI$):** Shannon entropy measure `mutual_info_classif(X, Y)`.
4. **Logistic Regression ($LR$):** Coefficients $max(0, \beta_i)$.
5. **Mean Uplift ($U$):** $\mu(X_i)_{success} - \mu(X_i)_{weak}$.
6. **Prevalence Uplift ($P$):** Differences in binary presence frequency.

### B. Global Causal Score
The system aggregates the normalized arrays via a hardcoded weight distribution to prioritize non-linear tree logic while respecting basic logistical uplift:
$$ Score_i = 0.25\cdot GB_i + 0.20\cdot RF_i + 0.15\cdot MI_i + 0.15\cdot LR_i + 0.15\cdot U_i + 0.10\cdot P_i $$

---

## 3. The Evidentiary Differential Gap (`gap_analysis.py`)

For any feature cluster $f$, the system queries the population classified as Strong ($S$) and Weak ($W$). Let $P(f|S)$ be the average frequency of feature $f$ occurring in successful cases.
$$ \text{Differential Gap}_f = P(f|S) - P(f|W) $$
This calculation surfaces anomalies (e.g., if Witness Testimony shows a 45% presence in successful cases but only 12% in failed cases, the Gap is +33%).

---

## 4. Retrieval-Conditioned Missing Evidence Recommender (`recommendation.py`)

Given a single case vector $\Phi_{target}$ and its FAISS neighborhood of similar retrieved cases $N$, the algorithm determines what evidence $\Phi_{target}$ is critically lacking.

### A. Neighborhood Mass Calculation
It segments the retrieved neighborhood into two buckets based on probabilistic outcomes:
- **Strong Mass ($M_s$):** $\sum_i (1 - P_{weak}(i)) \cdot \text{sim}(i)$
- **Weak Mass ($M_w$):** $\sum_i P_{weak}(i) \cdot \text{sim}(i)$

Where $\text{sim}(i) = 1 / (d_i + \epsilon)$ and $P_{weak}$ comes from the calibrated weak-case model.

### B. Five-Signal Scoring (Level 2)
For each candidate evidence feature $f$ missing in $\Phi_{target}$:

1. **Prevalence Signal:** $prev_s(f) - prev_w(f)$, the outcome-conditioned presence difference.
2. **Intensity Signal:** Sigmoid of similarity-weighted count difference between strong/weak neighbors.
3. **Log-Odds Signal:** Smoothed Bayesian log-odds with Laplace prior alpha=1.
4. **Effect Size:** Cohen's d-like standardized difference of intensity means.
5. **Global Importance:** From the ensemble causal ranking model (Section 2).

### C. Dynamic Context Weights
Weights adapt to query sparsity and retrieval reliability. All 5 weights are L1-normalized.

### D. Final Recommendation Score
$$ Score(f) = \sum_{k} w_k \cdot signal_k(f) $$

A feature is recommended only if at least one local signal is positive.

---

## 5. Statistical Judgment Predictor (`models/judgment/predict.py`)

A non-parametric fallback using **Inverse Distance Weighting (IDW)**. Unknown outcomes are **excluded** from the weighted vote to prevent bias:
$$ P(Allowed) = \frac{\sum_{i \in Allowed} W_i}{\sum_{i \in Known} W_i} $$

---

## 6. XGBoost Unified Output (`main_pipeline.py`)

The Phi-Vector is fed to the trained XGBoost ensemble:
$$ \hat{Y} = M_{xgb}(\Phi_{target}) $$
Where $M_{xgb}$ optimizes Log-Loss. `predict_proba(X)` emits the final judgment probability.

---

## 7. Counterfactual Evidence Importance (`counterfactual.py`)

**Level 3** importance. Given trained model $M$ and case Phi-vector:

$$ importance(e) = P(win | \Phi_{e=1}) - P(win | \Phi_{e=0}) $$

This directly answers: "If this evidence were present, how much would the prediction change?" The delta is injected into the recommendation engine as an additional ranking factor.

---

## 8. Ablation Study (`train_ablation.py`)

Validates incremental contribution of each Phi-vector block via 5-fold stratified CV:

| Step | Feature Block Added |
|------|-------------------|
| A | Context (case type, parties, claims, issues) |
| B | + Evidence (coarse/fine-grained indicators) |
| C | + Gap (missing evidence signals) |
| D | + Conflict (contradiction count/score) |
| E | + RAG (retrieval ratios, similarity stats) |

Reports Accuracy, F1, AUC-ROC with incremental lift per step.

