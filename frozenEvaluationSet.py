import json

datasets = [
    "darija_events.json",
    "instagram_arabe.json",
    "news_headlines.json",
    "filtered_monastir_twitterFINAL.json",
    "facebookecrit.json",

]

merged = []
for file in datasets:
    with open(f"data/raw/{file}", "r", encoding="utf-8") as f:
        data = json.load(f)
        for item in data:
            # Ensure all have consistent keys
            if "sentiment" not in item:
                item["sentiment"] = "neutral"  # Default
            if "event_type" not in item:
                item["event_type"] = "unknown"
            item["source"] = file.replace(".json", "")
            merged.append(item)

# Save frozen set
with open("data/processed/final_evaluation_set.json", "w", encoding="utf-8") as f:
    json.dump(merged, f, ensure_ascii=False, indent=2)