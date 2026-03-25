import json

with open("telangana_2025_48919125.json", "r", encoding="utf-8") as f:
    data = json.load(f)

issues = data["elements_by_title"]["Issue"]

# sort numerically by id (p_1, p_2, p_10 ...)
issues.sort(key=lambda x: int(x["id"].split("_")[1]))

# save back
with open("telangana_2025_48919125_sorted.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Saved in correct order → telangana_2025_48919125_sorted.json")