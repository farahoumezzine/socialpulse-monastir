# twitter_test.py
# Purpose: Fetch and save a small sample of real tweets about Monastir (Tunisia)
# Run this ONLY ONCE to preserve your X API quota (100 tweets/month)

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Get Bearer Token
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

if not BEARER_TOKEN:
    print("❌ Error: Bearer Token not found in .env file.")
    print("   → Create a file named `.env` in this folder with:")
    print('      TWITTER_BEARER_TOKEN=your_real_token_here')
    exit(1)

# Ensure output directory exists
os.makedirs("data/raw", exist_ok=True)

# Define X API endpoint
url = "https://api.twitter.com/2/tweets/search/recent"

# Build query: Focus on Monastir, Tunisia (not football!)
params = {
    "query": "(Monastir OR المنستير) (lang:fr OR lang:ar) -is:retweet -USMonastir -\"Union Sportive\" -football -match",
    "max_results": 10,
    "tweet.fields": "lang,created_at,author_id",
    "expansions": "author_id",
    "user.fields": "location"
}

# Set headers
headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}

print("📡 Fetching real tweets about Monastir (Tunisia)...")
print("   Query:", params["query"])

# Make the request
try:
    response = requests.get(url, headers=headers, params=params, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        tweets = data.get("data", [])
        
        # Save to file
        output_path = "data/raw/real_monastir_sample.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Success! Saved {len(tweets)} tweets to:")
        print(f"   {os.path.abspath(output_path)}")
        
        # Show sample
        print("\n📄 Sample tweets:")
        for i, tweet in enumerate(tweets[:3], 1):
            lang = tweet.get("lang", "unknown")
            text = tweet.get("text", "")[:80].replace("\n", " ")
            print(f"  {i}. [{lang}] {text}...")
            
    elif response.status_code == 429:
        print("⚠️  Quota exceeded! X API monthly limit reached (100 tweets).")
        print("   → Switch to simulated data for development.")
    else:
        print(f"❌ API Error {response.status_code}: {response.text}")

except requests.exceptions.RequestException as e:
    print(f"🌐 Network error: {e}")
except Exception as e:
    print(f"💥 Unexpected error: {e}")