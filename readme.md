# BLEU Evaluation Methodology

This project evaluates the reasoning capabilities of our legal judgment pipeline by computing BLEU scores against ground-truth data.

## Evaluation Process

The evaluation script (`scripts/evaluate_bleu.py`) follows a rigorous methodology to ensure the model produces independent, unbiased reasoning:

1. **Dataset Selection**: We load test cases from `data/conclusions_data.json` that contain both a ground-truth "Conclusion" and the "Court's Reasoning".
2. **Data Sanitisation**: To prevent data leakage, we strip out critical sections from the raw JSON file (e.g., "Conclusion", "Court's Reasoning", "Judgment", "Final Order"). This guarantees the pipeline cannot simply copy the final decision.
3. **Pipeline Execution**: The sanitised case data is fed into the core `main_pipeline.py`.
4. **Extraction**: We extract the LLM-induced reasoning from the pipeline's output (specifically focusing on `summary_narrative` or `logical_steps`).
5. **BLEU Computation**: We compute N-gram sentence-BLEU scores (BLEU-1 through BLEU-4) comparing the generated text against two references:
   - The ground-truth **Conclusion**
   - The ground-truth **Court's Reasoning**

## Evaluation Results (Subset Analysis)

Based on our recent evaluation runs (`outputs/bleu_summary.csv`), we analysed a subset consisting of the **first 120 cases**. The table below summarises the average sentence-BLEU scores for this cohort.

| Metric | Against Ground-Truth Conclusion | Against Ground-Truth Court's Reasoning |
| --- | --- | --- |
| **BLEU-1** | 0.1597 | 0.1064 |
| **BLEU-2** | 0.0677 | 0.0475 |
| **BLEU-3** | 0.0221 | 0.0156 |
| **BLEU-4** | 0.0088 | 0.0055 |

### Analysis

*   **Higher Overlap with Conclusion**: The model generally achieves slightly higher alignment (BLEU-1: 0.16 vs 0.11) with the final **Conclusion** than with the granular **Court's Reasoning**. This suggests the pipeline often successfully captures the high-level legal outcome, even if the exact judicial phrasing of the reasoning isn't replicated word-for-word.
*   **Low Higher-Order N-grams**: As expected with complex legal text generation, higher-order n-gram overlap (BLEU-3 and BLEU-4) is low. Generative LLMs naturally introduce paraphrasing and syntactic variation, which heavily penalises exact n-gram matching in BLEU.

## Files Generated
*   `outputs/bleu_summary.csv`: Per-case breakdown of BLEU scores.
*   `outputs/bleu_results.json`: Full evaluation payload including individual case outputs, token counts, and corpus-level metrics.
