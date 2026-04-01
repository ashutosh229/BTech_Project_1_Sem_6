import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def generate_dashboard(summary_path="data/processed/corpus_intelligence_summary.csv", output_path="outputs/corpus_intelligence_dashboard.png"):
    """
    Generates a 4-Panel Intelligence Dashboard for the Corpus.
    """
    if not os.path.exists(summary_path):
        print(f"⚠️ Summary not found at {summary_path}. Skipping plotting.")
        return

    df = pd.read_csv(summary_path)
    sns.set_theme(style="whitegrid", palette="viridis")
    
    fig, axes = plt.subplots(2, 2, figsize=(20, 15))
    
    # 1. Prediction Confidence Distribution
    sns.histplot(data=df, x='judgment_probability', bins=30, ax=axes[0, 0], kde=True)
    axes[0, 0].set_title("Corpus Prediction Confidence Distribution")
    axes[0, 0].set_xlabel("Predicted Confidence (0.0 to 1.0)")

    # 2. Evidence vs Missing Evidence Correlation
    sns.scatterplot(data=df, x='evidence_present', y='missing_evidence', hue='predicted_outcome', ax=axes[0, 1], alpha=0.5)
    axes[0, 1].set_title("Evidence Gap Analysis: Present vs Missing")

    # 3. Contradiction Score vs Outcome
    sns.boxplot(data=df, x='predicted_outcome', y='contradiction_score', ax=axes[1, 0])
    axes[1, 0].set_title("Symbolic Contradictions by Outcome Prediction")

    # 4. Case Type Distribution
    df['case_type'].value_counts().plot.pie(ax=axes[1, 1], autopct='%1.1f%%', colors=sns.color_palette("magma"))
    axes[1, 1].set_ylabel("")
    axes[1, 1].set_title("System Composition: Criminal vs Civil")

    plt.tight_layout()
    plt.savefig(output_path)
    print(f"📊 Dashboard saved to: {output_path}")

if __name__ == "__main__":
    generate_dashboard()
