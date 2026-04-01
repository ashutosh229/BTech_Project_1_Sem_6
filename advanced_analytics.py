import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import re

def advanced_corpus_analytics(summary_path="data/processed/corpus_intelligence_summary.csv"):
    """
    Step 9: Academic Evaluation Engine.
    Examines Jurisdictional Bias, Temporal Trends, and Evidence Synergy.
    """
    if not os.path.exists(summary_path):
        print("🕒 Corpus summary not ready yet.")
        return

    df = pd.read_csv(summary_path)
    
    # 1. Feature Engineering from Metadata (filename)
    # allahabad_2015_3099880 -> [Court, Year]
    def extract_meta(cid):
        parts = cid.split('_')
        court = parts[0]
        year = parts[1] if len(parts) > 1 and parts[1].isdigit() else "Unknown"
        return court, year

    df[['court', 'year']] = df['case_id'].apply(lambda x: pd.Series(extract_meta(x)))
    df = df[df['year'] != "Unknown"] # Clean noise

    sns.set_theme(style="whitegrid", palette="flare")
    plt.rcParams['figure.figsize'] = (20, 15)

    # ---------------------------------------------------------
    # PANEL 1: Jurisdictional Outcome Heatmap (High Court Bias)
    # ---------------------------------------------------------
    plt.figure(figsize=(15, 8))
    court_outcomes = pd.crosstab(df['court'], df['predicted_outcome'], normalize='index')
    sns.heatmap(court_outcomes, annot=True, cmap="YlOrRd", fmt=".2f")
    plt.title("⚖️ High Court Outcome Distribution (Jurisdictional Strictness)")
    plt.savefig("outputs/judicial_bias_heatmap.png")
    plt.close()

    # ---------------------------------------------------------
    # PANEL 2: Temporal Evolution of Evidence (2015-2025)
    # ---------------------------------------------------------
    plt.figure(figsize=(15, 8))
    yearly_avg = df.groupby('year')['judgment_probability'].mean().reset_index()
    sns.lineplot(data=yearly_avg, x='year', y='judgment_probability', marker='o', linewidth=3)
    plt.title("📅 Confidence Trends in Judicial Forecasting (2015-2025)")
    plt.savefig("outputs/legal_temporal_trends.png")
    plt.close()

    # ---------------------------------------------------------
    # PANEL 3: Cluster Distribution (Criminal vs Civil)
    # ---------------------------------------------------------
    plt.figure(figsize=(15, 8))
    sns.countplot(data=df, x='case_type', palette='viridis')
    plt.title("📂 System Composition (Criminal vs Civil)")
    plt.savefig("outputs/corpus_composition.png")
    plt.close()

    print("🏁 Advanced Analytics Complete. 3 High-Impact Plots saved to outputs/")

if __name__ == "__main__":
    advanced_corpus_analytics()
