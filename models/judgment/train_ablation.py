import pandas as pd
import numpy as np
import os
import joblib
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt
import seaborn as sns

def run_ablation_study(dataset_path="data/dataset/final_phi_features.csv"):
    """
    Step 12: Research Evaluation & Ablation Study.
    Tests the prediction 'Lift' of Context, Evidence, Retrieval, and Reasoning.
    """
    if not os.path.exists(dataset_path):
        print(f"⚠️ Phi-Matrix not found at {dataset_path}. Run scripts/prepare_dataset.py first.")
        return

    # 1. Load Data
    df = pd.read_csv(dataset_path)
    X = df.drop(['label', 'case_id'], axis=1)
    y = df['label']
    X_train, X_test, y_train, y_test = train_test_split(X, y.values.ravel(), test_size=0.3, random_state=42)

    # 2. Define Ablation Steps (Feature Blocks)
    # Context (phi_c), Evidence (phi_e), Reasoning (phi_g+phi_conflict), RAG (phi_rag)
    feature_sets = {
        "A: Context Only": ['is_criminal', 'num_claims', 'num_issues', 'num_parties', 'parties_density'],
        "B: Context + Evidence": ['is_criminal', 'num_claims', 'num_issues', 'num_parties', 'parties_density', 
                                 'evidence_density', 'has_medical_fsl', 'has_fir_seizure', 
                                 'cluster_0', 'cluster_1', 'cluster_2', 'cluster_3', 'cluster_4', 'cluster_5'],
        "C: C + E + Reasoning": ['is_criminal', 'num_claims', 'num_issues', 'num_parties', 'parties_density', 
                                 'evidence_density', 'has_medical_fsl', 'cluster_0', 'cluster_1', 'cluster_2', 
                                 'gap_count', 'max_gap_confidence', 'conflict_count', 'conflict_score'],
        "D: 🔥 Full Pipeline (Phi)": X.columns.tolist() # All 20 features
    }

    ablation_results = []
    sns.set_theme(style="whitegrid", palette="magma")

    print("🚀 Running Ablation Study (Module Analysis)...")
    for name, features in feature_sets.items():
        # Filter for the sub-set
        X_sub_train = X_train[features]
        X_sub_test = X_test[features]

        # Train a baseline XGBoost
        model = XGBClassifier(n_estimators=50, max_depth=3, learning_rate=0.1, random_state=42)
        model.fit(X_sub_train, y_train)
        
        # Test
        y_pred = model.predict(X_sub_test)
        acc = accuracy_score(y_test, y_pred)
        
        ablation_results.append({"model": name, "accuracy": acc})
        print(f"✅ {name}: Accuracy = {acc*100:.1f}%")

    # 3. Plot Module Impact (Ablation Results)
    df_results = pd.DataFrame(ablation_results)
    plt.figure(figsize=(10, 6))
    ax = sns.barplot(data=df_results, x='model', y='accuracy')
    plt.title("🏆 Ablation Study: Impact of Reasoning Modules on Accuracy")
    plt.ylim(0, 1.1)
    for p in ax.patches:
         ax.annotate(f"{p.get_height()*100:.1f}%", (p.get_x()+p.get_width()/2, p.get_height()), ha='center', va='bottom')
    
    os.makedirs("outputs/plots", exist_ok=True)
    plt.savefig("outputs/plots/ablation_study.png")
    plt.close()
    
    print("📊 Ablation Dashboard saved to outputs/plots/ablation_study.png")

    # 4. Save the FULL model for Inference Engine use
    full_model = XGBClassifier(n_estimators=100, max_depth=5, random_state=42)
    full_model.fit(X_train, y_train)
    joblib.dump({"model": full_model, "features": X.columns.tolist()}, "data/processed/judgment_model.joblib")
    print(f"💾 Final Inference Model saved to: data/processed/judgment_model.joblib")

if __name__ == "__main__":
    run_ablation_study()
