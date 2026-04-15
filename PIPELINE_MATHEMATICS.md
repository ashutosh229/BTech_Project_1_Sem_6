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

Given a single case vector $\Phi_{target}$ and its FAISS neighborhood of similar retrieved cases $N$, the algorithm must determine what evidence $\Phi_{target}$ is critically lacking.

### A. Neighborhood Mass Calculation
It segments the retrieved neighborhood into two buckets based on their historical outcomes:
- **Strong Neighborhood ($N_s$):** $\sum \text{similarity\_score}$ of successful neighbors.
- **Weak Neighborhood ($N_w$):** $\sum \text{similarity\_score}$ of dismissed/weak neighbors.

### B. Dynamic Context Weights
A custom log-based formulation is used to weight how heavily the recommender leans on local neighborhood statistics vs. global dataset heuristics.
$$ \text{Multiplier} = 1.0 + \log(1.0 + \frac{N_{total}}{5}) $$
If the current target case has very few retrieved neighbors, global heuristic weights act as a fallback smoothing factor.

### C. Prevalence & Log-Odds Difference
For a specific candidate evidence feature $f$ missing in $\Phi_{target}$:
1. **Strong Prevalence ($Prev_s$):** % of $N_s$ cases possessing $f$.
2. **Weak Prevalence ($Prev_w$):** % of $N_w$ cases possessing $f$.
3. **Log-Odds Shift:** 
   $$ L\_Odds = \log\left(\frac{Prev_s + 0.05}{Prev_w + 0.05}\right) $$
   (A constant $0.05$ is added to prevent division by zero/math domain errors).

### D. Final Recommendation Confidence Score
For every candidate feature not found in the current case, the algorithm calculates a raw score:
$$ Score_{raw} = \left(Prev_s \cdot 3.5\right) + \left(L\_Odds \cdot 1.5\right) + \left(\text{Global\_Importance}_f \cdot 0.8\right) $$
This raw score is run through a Sigmoid activation function to bound it beautifully between $0$ and $1$, representing the `% Confidence` that the user *should* procure this evidence:
$$ Confidence = \frac{1}{1 + e^{-Score_{raw}}} $$

---

## 5. Statistical Judgment Predictor (`models/judgment/predict.py`)

A non-parametric fallback algorithm utilizing pure **Inverse Distance Weighting (IDW)** inside the Semantic Vector Space.
For $k$ similar retrieved documents, each having a known outcome $O_i$ (Allowed/Dismissed) and distance $d_i$:
$$ W_i = \frac{1}{d_i + \epsilon} $$
Where $\epsilon = 1e-6$ to prevent zero-division. 
The probabilities are calculated as:
$$ P(\text{Allowed}) = \frac{\sum_{i \in \text{Allowed}} W_i}{\sum W_{total}} $$

---

## 6. XGBoost / Deep Learning Unified Output (`main_pipeline.py`)

When the ML model is initialized (`judgment_model.joblib`), the RAG stats, Multi-Hot evidence bit-vectors, calculated contradiction severity score (between `0.0 - 1.0`), and contextual heuristics (Claim types) are flattened into the **Phi-Vector** $\Phi_{1...N}$.
$$ \hat{Y} = M_{xgb}(\Phi_{target}) $$
Where $M_{xgb}$ is the trained tree-ensemble optimizing for Log-Loss. The function `predict_proba(X)` emits the true final AI Judgment Probability.
