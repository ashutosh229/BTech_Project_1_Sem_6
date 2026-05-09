"""
evaluation/
──────────────────────────────────────────────────────────────────────────────
NyayaRAG Evaluation Suite

Each module implements one automatic metric against the pipeline's generated
reasoning narrative vs. ground-truth conclusion / court's reasoning:

  evaluate_bleu.py       – BLEU-1/2/3/4 (corpus + sentence)
  evaluate_rouge.py      – ROUGE-1, ROUGE-2, ROUGE-L
  evaluate_meteor.py     – METEOR
  evaluate_bertscore.py  – BERTScore (Precision / Recall / F1)
  evaluate_blanc.py      – BLANC (BLANC-help & BLANC-tune)
  evaluate_geval.py      – G-Eval  (LLM-as-a-Judge via Groq)
  evaluate_expert.py     – Expert / Human Score loader & aggregator
  run_all.py             – Run every metric and merge into one report
"""
