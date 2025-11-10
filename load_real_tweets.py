# load_tweets.py
import json
import re

# Load real tweets
with open("data/raw/real_monastir_sample.json", "r", encoding="utf-8") as f:
    data = json.load(f)

tweets = data.get("data", [])

# Keywords that suggest TUNISIAN Monastir (not football/sports)
MONASTIR_TN_KEYWORDS = [
    "المنستير", "Monastir ville", "Monastir Tunisie", "Ribat", "plage Monastir",
    "hôpital Monastir", "Aéroport Monastir", "Sahel", "gouvernorat", "cité",
    "منستير", "المنستيرية", "شاطئ", "مستشفى", "مطار"
]

# Keywords that suggest SPORTS (exclude)
SPORTS_KEYWORDS = [
    "US Monastir", "Union Sportive", "football", "équipe", "but", "match",
    "Challenger", "tournoi", "ATP", "joueur", " qualifications"
]

def is_relevant_to_monastir_city(text: str) -> bool:
    text_lower = text.lower()
    # If it mentions sports → likely irrelevant
    if any(kw.lower() in text_lower for kw in SPORTS_KEYWORDS):
        return False
    # If it contains local Tunisian keywords → likely relevant
    if any(kw in text for kw in MONASTIR_TN_KEYWORDS):
        return True
    # Otherwise: maybe relevant (keep with low confidence)
    return "monastir" in text_lower or "المنستير" in text

print(f"📥 Loaded {len(tweets)} tweets. Filtering for Monastir, Tunisia city context...\n")

relevant_tweets = []
for tweet in tweets:
    text = tweet["text"]
    lang = tweet.get("lang", "unknown")
    
    # Clean text: remove URLs, extra whitespace
    clean_text = re.sub(r"https?://\S+", "", text)  # remove URLs
    clean_text = re.sub(r"\s+", " ", clean_text).strip()
    
    if is_relevant_to_monastir_city(clean_text):
        relevant_tweets.append({"lang": lang, "text": clean_text})
        print(f"✅ [{lang}] {clean_text[:100]}...")
    else:
        print(f"❌ [{lang}] (filtered) {clean_text[:100]}...")

print(f"\n🎯 Kept {len(relevant_tweets)} / {len(tweets)} tweets as relevant to Monastir city.")

# Save filtered data for your pipeline
with open("data/processed/filtered_monastir_tweets.json", "w", encoding="utf-8") as f:
    json.dump(relevant_tweets, f, ensure_ascii=False, indent=2)

print("\n💾 Saved filtered tweets to: data/processed/filtered_monastir_tweets.json")