import emoji
import re
import unicodedata
import json

def normalize_darija_transliteration(text):
    """
    Convert Tunisian Darija written in Latin script with numbers to Arabic script.
    Handles common patterns like 3->ع, 7->ح, 9->ق, ch->ش, kh->خ, etc.
    Only maps words that appear in your dataset for efficiency.
    """
    # Mappings based on your Darija data
    mappings = [
        # Core letters
        ('3', 'ع'),  # 3aslema → عaslema
        ('7', 'ح'),  # b7ar → bحar
        ('9', 'ق'),  # 9wi → قwi, 9ass → قass
        ('kh', 'خ'), # khir → خير
        ('ch', 'ش'), # not in your data, but common
        
        # Words from your dataset
        ('el', 'ال'),  # el khir → al khir
        ('elyoum', 'اليوم'),  # elyoum → اليوم
        ('makch', 'ماكش'),  # makch → ماكش (can't)
        ('tnajm', 'تقدر'),  # tnajm → تقدر (can you)
        ('tet3eda', 'تتعدا'),  # tet3eda → تتعدا (get back)
        ('hbel', 'هابيل'),  # hbel → هابيل (cool/awesome)
        ('wallahi', 'والله'),  # wallahi → والله
        ('khniss', 'خنيس'),  # Khniss → خنيس
        ('steg', 'الشركة التونسية للكهرباء والغاز'),  # STEG (keep short: STEG)
        ('usmonastir', 'نادي المنستير'),  # USMonastir → نادي المنستير
        ('monastir', 'المنستير'),  # Monastir → المنستير
        ('match', 'مباراة'),  # match → مباراة
        ('plage', 'شاطئ'),  # plage → شاطئ
        ('trafik', 'زحمة'),  # trafik → زحمة
        ('centre', 'مركز'),  # centre → مركز
        ('courant', 'تيار'), # courant → تيار
        ('khouya', 'خويا'),  # khouya → خويا (bro)
        ('barcha', 'برشا'),  # barcha → برشا (a lot) - keep or map to "ب"
        ('ness', 'نّاس'),  # ness → الناس (people)
        ('jaw', 'jaw'),  # jaw → jaw (there is) - keep or map to "فيه"
        ('raw3a', 'روعة'),  # raw3a → روعة (amazing)
        ('kifek', 'كيفك'),  # kifek → كيفك (how are you)
        ('chneya', 'شنية'),  # chneya → شنية (what)
        ('sah', 'صح'),  # sah → صح (correct)
        ('mashi', 'ماشي'),  # mashi → ماشي (not)
        ('ya3ni', 'يعني'),  # ya3ni → يعني (means)
        ('haja', 'حاجة'),  # haja → حاجة (thing)
        ('chouf', 'شوف'),  # chouf → شوف (see)
        ('ra7', 'راح'),  # ra7 → راح (gone)
        ('m3a', 'مع'),  # m3a → مع (with)
        ('b7ar', 'بحر'),  # b7ar → بحر (sea)
        ('hbel', 'هبيل'),  # hbel → هبيل (cool)
        ('thama', 'ثمة'),  # thama → ثمة (there is)
        ('nochr', 'نُشر'),  # nochrbou → نُشر (we drink)
        ('9ahwa', 'قهوة'),  # 9ahwa → قهوة (coffee)
        ('mahata', 'محطة'),  # mahata → محطة (station)
        ('connex', 'اتصال'),  # connex → اتصال (connection)
        ('internet', 'انترنت'),  # internet → انترنت
        ('panne', 'عطل'),  # panne → عطل (breakdown)
        ('connexion', 'اتصال'),  # connexion → اتصال (connection)
        ('music', 'موسيقى'),  # music → موسيقى
        ('culture', 'ثقافة'),  # culture → ثقافة
        ('tourisme', 'سياحة'),  # tourisme → سياحة
        ('transport', 'نقل'),  # transport → نقل
        ('environnement', 'بيئة'),  # environnement → بيئة
        ('sport', 'رياضة'),  # sport → رياضة
        ('vie_locale', 'حياة_محلية'),  # vie_locale → حياة_محلية
        ('panne_électrique', 'انقطاع_كهرباء'),  # panne_électrique → انقطاع_كهرباء
        ('panne_internet', 'انقطاع_انترنت'),  # panne_internet → انقطاع_انترنت
    ]

    # Apply mappings in order (longer patterns first to avoid conflicts)
    for latin, arabic in mappings:
        # Use word boundaries to avoid partial replacements
        text = re.sub(r'\b' + re.escape(latin) + r'\b', arabic, text, flags=re.IGNORECASE)

    return text

def normalize_text(text):
    # 1. Handle Darija transliteration first (convert Latin to Arabic script)
    text = normalize_darija_transliteration(text)

    # 2. Replace emojis with text labels
    text = emoji.demojize(text)
    text = text.replace("_", " ")  # make emoji words readable
    text = re.sub(r':[a-zA-Z ]+:', lambda m: m.group(0).replace(':', ''), text)

    # 3. Remove Arabic diacritics and tatweel
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

    # 4. Normalize common Arabic character variants
    replacements = {
        'أ': 'ا', 'إ': 'ا', 'آ': 'ا',
        'ى': 'ي', 'ة': 'ه',
        'ؤ': 'ء', 'ئ': 'ء'
    }
    for ar, repl in replacements.items():
        text = text.replace(ar, repl)

    # 5. Remove extra whitespace and normalize punctuation
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text


def detect_language(text):
    arabic_chars = re.findall(r'[\u0600-\u06FF]', text)
    latin_chars = re.findall(r'[a-zA-Z]', text)
    has_numbers_for_arabic = any(c in text for c in ['3', '7', '9', '5', '2'])

    if len(arabic_chars) > len(latin_chars):
        return 'ar'  # mostly Arabic script
    elif has_numbers_for_arabic or (len(latin_chars) > 0 and len(arabic_chars) > 0):
        return 'da'  # Darija (transliteration or mixed)
    elif any(word in text.lower() for word in ['monastir', 'plage', 'match', 'festival', 'ville', 'centre', 'trafik', 'panne', 'tourisme']):
        return 'fr'
    else:
        return 'da'  # default to Darija if uncertain


# Load the JSON data from the file
with open('../data/processed/final_evaluation_set.json', 'r', encoding='utf-8') as file:
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

# Save the processed data
with open('../data/processed/normalized_data.json', 'w', encoding='utf-8') as f:
    json.dump(cleaned_data, f, ensure_ascii=False, indent=2)

print("✅ Normalization completed! Processed data saved to 'normalized_data.json'")