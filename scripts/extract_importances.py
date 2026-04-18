import joblib
import json
import os

model_path = 'data/processed/judgment_model.joblib'
if os.path.exists(model_path):
    artifact = joblib.load(model_path)
    model = artifact['model']
    features = artifact['features']
    importances = model.feature_importances_.tolist()
    importance_map = dict(zip(features, importances))
    
    with open('outputs/feature_importances.json', 'w') as f:
        json.dump(importance_map, f, indent=2)
    print("Saved to outputs/feature_importances.json")
else:
    print("Model not found")
