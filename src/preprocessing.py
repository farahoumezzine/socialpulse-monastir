import emoji
import re
import unicodedata
import json
def normalize_text(text):
    # 1. Replace emojis with text labels
    text = emoji.demojize(text)
    text = text.replace("_", " ")  # make emoji words readable
    text = re.sub(r':[a-zA-Z ]+:', lambda m: m.group(0).replace(':', ''), text)

    # 2. Remove Arabic diacritics and tatweel
    arabic_diacritics = re.compile("""
        ّ    | # Shadda
        َ    | # Fatha        
        ً    | # Tanwin Fath
        ُ    | # Damma
        ٌ    | # Tanwin Damm
        ِ    | # Kasra
        ٍ    | # Tanwin Kasr
        ْ    | # Sukun
        ـ     # Tatwil/Kashida
    """, re.VERBOSE)
    text = re.sub(arabic_diacritics, '', text)

    # 3. Normalize common Arabic character variants
    replacements = {
        'أ': 'ا', 'إ': 'ا', 'آ': 'ا',
        'ى': 'ي', 'ة': 'ه',
        'ؤ': 'ء', 'ئ': 'ء'
    }
    for ar, repl in replacements.items():
        text = text.replace(ar, repl)

    # 4. Remove extra whitespace and normalize punctuation
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text


def detect_language(text):
    arabic_chars = re.findall(r'[\u0600-\u06FF]', text)
    latin_chars = re.findall(r'[a-zA-Z]', text)

    if len(arabic_chars) > len(latin_chars):
        return 'ar'  # mostly Arabic script (could include Darija)
    elif len(latin_chars) > 0 and len(arabic_chars) > 0:
        return 'da'  # mixed Latin/Arabic → likely Darija translit
    elif any(word in text.lower() for word in ['monastir', 'plage', 'match', 'festival', 'ville']):
        return 'fr'
    else:
        return 'da'



# Load the JSON data from the file
with open('../data/processed/copy.json', 'r', encoding='utf-8') as file:
    merged = json.load(file)

# Apply normalization to dataset
cleaned_data = []
for post in merged:  # assuming merged is your full JSON list
    print(f"Processing post ID: {post.get('id', 'Unknown')}")
    new_post = post.copy()
    new_post["clean_text"] = normalize_text(post["text"])
    print(f"Normalized text: {new_post['clean_text']}")
    new_post["detected_lang"] = detect_language(post["text"])
    print(f"Detected language: {new_post['detected_lang']}")
    cleaned_data.append(new_post)
    print(f"Post processed: {new_post}\n")
