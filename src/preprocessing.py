import emoji
import re
import json
import random
import os

# ============================================
# 1.  EMOJI SENTIMENT MAPPING (Tableau d'emojis)
# ============================================
EMOJI_SENTIMENT_MAP = {
    # Positif
    '😀': {'sentiment': 'positive', 'score': 1, 'label': 'farhan'},
    '😊': {'sentiment': 'positive', 'score': 1, 'label': 'farhan'},
    '😍': {'sentiment': 'positive', 'score': 1, 'label': 'hob'},
    '🥰': {'sentiment': 'positive', 'score': 1, 'label': 'hob'},
    '❤️': {'sentiment': 'positive', 'score': 1, 'label': 'hob'},
    '💕': {'sentiment': 'positive', 'score': 1, 'label': 'hob'},
    '👍': {'sentiment': 'positive', 'score': 0.8, 'label': 'behi'},
    '🎉': {'sentiment': 'positive', 'score': 1, 'label': 'jaw'},
    '🔥': {'sentiment': 'positive', 'score': 0.9, 'label': 'nar'},
    '💪': {'sentiment': 'positive', 'score': 0.8, 'label': 'kwi'},
    '✨': {'sentiment': 'positive', 'score': 0.7, 'label': 'jaw'},
    '🙏': {'sentiment': 'positive', 'score': 0.7, 'label': 'chokr'},
    '😂': {'sentiment': 'positive', 'score': 0.8, 'label': 'edahek'},
    '🤣': {'sentiment': 'positive', 'score': 0.8, 'label': 'edahek'},
    '👏': {'sentiment': 'positive', 'score': 0.9, 'label': 'bravo'},
    '🥳': {'sentiment': 'positive', 'score': 1, 'label': 'jaw'},
    '😎': {'sentiment': 'positive', 'score': 0.7, 'label': 'jaw'},
    '🌟': {'sentiment': 'positive', 'score': 0.8, 'label': 'jaw'},
    '🎶': {'sentiment': 'positive', 'score': 0.6, 'label': 'jaw'},
    # Négatif
    '😢': {'sentiment': 'negative', 'score': -0.8, 'label': 'hzin'},
    '😭': {'sentiment': 'negative', 'score': -1, 'label': 'yebki'},
    '😡': {'sentiment': 'negative', 'score': -1, 'label': 'metghachech'},
    '😠': {'sentiment': 'negative', 'score': -0.9, 'label': 'metghachech'},
    '🤬': {'sentiment': 'negative', 'score': -1, 'label': 'metghachech'},
    '👎': {'sentiment': 'negative', 'score': -0.8, 'label': 'mouch_behi'},
    '💔': {'sentiment': 'negative', 'score': -0.9, 'label': '9alb_maksour'},
    '😤': {'sentiment': 'negative', 'score': -0.7, 'label': 'metghachech'},
    '😩': {'sentiment': 'negative', 'score': -0.8, 'label': 'taab'},
    '😫': {'sentiment': 'negative', 'score': -0.9, 'label': 'taab'},
    '🙄': {'sentiment': 'negative', 'score': -0.5, 'label': 'mech_ajbou'},
    '😒': {'sentiment': 'negative', 'score': -0.6, 'label': 'mech_ajbou'},
    '😞': {'sentiment': 'negative', 'score': -0.7, 'label': 'hzin'},
    '😔': {'sentiment': 'negative', 'score': -0.6, 'label': 'hzin'},
    
    # Neutre
    '🤔': {'sentiment': 'neutral', 'score': 0, 'label': 'yfaker'},
    '🤷': {'sentiment': 'neutral', 'score': 0, 'label': 'marefch'},
    '📍': {'sentiment': 'neutral', 'score': 0, 'label': 'blasa'},
    '📸': {'sentiment': 'neutral', 'score': 0, 'label': 'taswira'},
    '🚗': {'sentiment': 'neutral', 'score': 0, 'label': 'karhba'},
    '🏖️': {'sentiment': 'neutral', 'score': 0.3, 'label': 'bhar'},
    '⚽': {'sentiment': 'neutral', 'score': 0.2, 'label': 'koura'},
}


def extract_emoji_sentiment(text):
    """
    Extrait les emojis du texte et calcule un score de sentiment agrégé.
    """
    found_emojis = []
    total_score = 0
    emoji_count = 0
    
    for char in text:
        if char in EMOJI_SENTIMENT_MAP:
            emoji_info = EMOJI_SENTIMENT_MAP[char]
            found_emojis.append({
                'emoji': char,
                'sentiment': emoji_info['sentiment'],
                'score': emoji_info['score'],
                'label_darija': emoji_info['label']
            })
            total_score += emoji_info['score']
            emoji_count += 1
        elif emoji. is_emoji(char):
            found_emojis.append({
                'emoji': char,
                'sentiment': 'neutral',
                'score': 0,
                'label_darija': 'emoji'
            })
    
    avg_score = total_score / emoji_count if emoji_count > 0 else 0
    
    return {
        'emojis': found_emojis,
        'emoji_count': emoji_count,
        'total_score': total_score,
        'avg_score': avg_score,
        'dominant_sentiment': 'positive' if avg_score > 0.2 else ('negative' if avg_score < -0.2 else 'neutral')
    }


def remove_emojis(text):
    """Supprime tous les emojis du texte après extraction."""
    return emoji.replace_emoji(text, replace='')



# ============================================
# 2.  CONVERSION DES CHIFFRES DARIJA -> LETTRES
# ============================================

# Mapping des chiffres arabes utilisés en Darija vers lettres latines
DARIJA_NUMBER_TO_LETTER = {
    '3': 'a',    # ع (3aslema -> aslema)
    '7': 'h',    # ح (7aja -> haja)
    '9': 'k',    # ق (9ahwa -> kahwa)
    '5': 'kh',   # خ (5ouya -> khouya)
    '2': 'a',    # ء (2aman -> aman)
    '8': 'gh',   # غ (8ali -> ghali) - optionnel
    '6': 't',    # ط (6abib -> tabib) - optionnel
}


def convert_darija_numbers_to_letters(text):
    """
    Convertit les chiffres utilisés en Darija vers leurs équivalents en lettres. 
    
    Exemples:
        - 9ahwa -> kahwa
        - 7aja -> haja
        - 3aslema -> aslema
        - 5ouya -> khouya
        - b7ar -> bhar
        - raw3a -> rawaa
    """
    result = text
    
    # Appliquer les conversions (ordre important:  5 avant les autres car 'kh' = 2 caractères)
    # On traite d'abord les patterns spéciaux puis les chiffres simples
    
    # Conversion des chiffres vers lettres
    for number, letter in DARIJA_NUMBER_TO_LETTER.items():
        result = result.replace(number, letter)
    
    return result


def convert_darija_numbers_smart(word):
    """
    Convertit intelligemment les chiffres dans un mot Darija.
    Gère les cas spéciaux comme les chiffres en début, milieu ou fin de mot.
    
    Exemples:
        - 9wi -> kwi
        - 3aslema -> aslema
        - b7ar -> bhar
        - raw3a -> rawaa
        - 7ala -> hala
        - 5niss -> khniss
    """
    result = word
    
    # Ordre de remplacement important (5 -> kh doit être avant les autres)
    replacements = [
        ('5', 'kh'),   # خ - doit être en premier car produit 2 caractères
        ('9', 'k'),    # ق
        ('7', 'h'),    # ح
        ('3', 'a'),    # ع
        ('2', 'a'),    # ء
        ('8', 'gh'),   # غ
        ('6', 't'),    # ط
    ]
    
    for number, letter in replacements:
        result = result.replace(number, letter)
    return result


# ============================================
# 3.  NORMALISATION VERS DARIJA TUNISIEN
# ============================================

# Dictionnaire Français -> Darija
FRENCH_TO_DARIJA = {
    # Lieux
    'plage': 'bhar',
    'mer': 'bhar',
    'beach': 'bhar',
    'ville': 'mdina',
    'centre': 'west bled',
    'rue': 'chera',
    'quartier': 'houma',
    'maison': 'dar',
    'restaurant': 'resto',
    'café': 'kahwa',
    'hôtel': 'hotel',
    'mosquée': 'jemaa',
    'marché': 'souk',
    'gare': 'mahata',
    'aéroport': 'matar',
    'hôpital': 'sbitar',
    'école': 'madrsa',
    'université': 'fac',
    
    # Météo / Nature
    'soleil': 'chams',
    'temps': 'jaw',
    'weather': 'takes',
    'chaud': 'skhoun',
    'froid': 'bard',
    'pluie': 'mtar',
    'vent': 'rih',
    'beau': 'mezyen',
    'belle': 'mezyena',
    'magnifique': 'rawa',
    'superbe': 'rawa',
    'joli': 'mezyen',
    'jolie': 'mezyena',
    
    # Sentiments / États
    'bien': 'behi',
    'bon': 'behi',
    'bonne': 'behia',
    'mauvais': 'khayeb',
    'mauvaise': 'khayba',
    'content': 'farhan',
    'contente': 'farhana',
    'heureux': 'farhan',
    'heureuse': 'farhana',
    'triste': 'hzin',
    'fatigué': 'taab',
    'fatiguée': 'taaba',
    'énervé': 'metghachech',
    'fâché': 'metghachech',
    'super': 'hbel',
    'génial': 'heyel yesser',
    'excellent': 'momtez',
    'parfait': 'heyel',
    'nul': 'khayeb',
    'horrible': 'khayeb yesser',
    'terrible': 'fdhiha',
    
    # Actions
    'manger': 'neklou',
    'boire': 'nochreb',
    'dormir': 'norked',
    'travailler': 'nekhdem',
    'aller': 'nemchi',
    'venir': 'nji',
    'voir': 'nchouf',
    'regarder': 'netfarej',
    'attendre': 'nestana',
    'partir': 'nemchi',
    'rentrer': 'narja',
    'sortir': 'nokhrej',
    
    # Transport
    'voiture': 'karhba',
    'bus': 'kar',
    'taxi': 'taxi',
    'train': 'metro',
    'trafic': 'zahma',
    'embouteillage': 'zahma',
    'circulation': 'zahma',
    'route': 'tri9',
    
    # Problèmes
    'problème': 'mochkla',
    'panne': 'panne',
    'coupure': 'kass',
    'électricité': 'dhaw',
    'internet': 'internet',
    'connexion': 'connexion',
    
    # Temps
    'aujourd\'hui': 'lyoum',
    'demain': 'ghodwa',
    'hier': 'berah',
    'maintenant': 'tawa',
    'toujours': 'dima',
    'jamais': 'abeden',
    'souvent': 'barcha',
    'beaucoup': 'barcha',
    'peu': 'chwaya',
    'très': 'barcha',
    
    # Personnes
    'gens': 'ness',
    'personnes': 'ness',
    'ami': 'sahbi',
    'amie': 'sahebti',
    'frère': 'khouya',
    'sœur': 'okhti',
    'famille': 'ayla',
    'enfants': 'sghar',
    'homme': 'rajel',
    'femme': 'mra',
    
    # Questions
    'quoi': 'chnoua',
    'comment': 'kifech',
    'pourquoi': 'alech',
    'où': 'win',
    'quand': 'waktech',
    'qui': 'chkoun',
    
    # Autres
    'chose': 'haja',
    'jour': 'nhar',
    'nuit': 'lil',
    'matin': 'sbeh',
    'soir': 'achiya',
    'festival': 'festival',
    'match': 'match',
    'foot': 'koura',
    'football': 'koura',
    'tourisme': 'siyeha',
    'touriste': 'siyeha',
    'vacances': 'otla',
}

# Dictionnaire Arabe Standard -> Darija
ARABIC_TO_DARIJA = {
    'جميل': 'mezyen',
    'جميلة': 'mezyena',
    'رائع': 'rawaa',
    'رائعة': 'rawaa',
    'ممتاز': 'momtez',
    'سيء': 'khayeb',
    'مشكلة': 'mochkla',
    'الناس': 'ness',
    'اليوم': 'lyoum',
    'غدا': 'ghodwa',
    'أمس': 'lberh',
    'الآن': 'tawa',
    'كثير': 'barcha',
    'قليل': 'chwaya',
    'البحر': 'bhar',
    'الشاطئ': 'bhar',
    'الطريق': 'triq',
    'المنزل': 'dar',
    'العمل': 'khedma',
    'الطقس': 'takes',
    'حار': 'skhoun',
    'بارد': 'bard',
    'مطر': 'mtar',
    'شمس': 'chams',
    'صديق': 'sahbi',
    'صديقة': 'sahebti',
    'أطفال': 'sghar',
    'رجل': 'rajel',
    'امرأة': 'mra',
    'ماذا': 'chnoua',
    'كيف': 'kifech',
    'لماذا': 'alech',
    'أين': 'win',
    'متى': 'waktech',
    'من': 'chkoun',
    'شيء': 'haja',
    'يوم': 'nhar',
    'ليل': 'lil',
    'صباح': 'sbeh',
    'مساء': 'achiya',
    'سعيد': 'farhan',
    'سعيدة': 'farhana',
    'حزين': 'hzin',
    'حزينة': 'hzina',
    'تعب': 'taab',
    'تعبة': 'taaba',
    'أكل': 'mekla',
    'شرب': 'chrab',
    'نوم': 'nom',
    'عمل': 'khedma',
    'مباراة': 'match',
    'كرة': 'koura',

    # === CHIFFRES ===
    'واحد': 'wahed',
    'اثنان': 'ethnin',
    'ثلاثة': 'thletha',
    'أربعة': 'arbaaa',
    'خمسة': 'khamsa',
    'ستة': 'setta',
    'سبعة': 'sbaaa',
    'ثمانية': 'thmenia',
    'تسعة': 'tsaa',
    'عشرة': 'aachra',

    # === MAISON & OBJETS ===
    'المنزل': 'dar',
    'غرفة': 'bet',
    'مطبخ': 'koujina',
    'حمام': 'toilette',
    'باب': 'beb',
    'نافذة': 'chobek',
    'سرير': 'ferach',
    'كرسي': 'korsi',
    'طاولة': 'tawla',
    'مفتاح': 'meftah',
    'نار': 'nar',
    'ثلاجة': 'frigidaire',

     # === FAMILLE ===
    'أب': 'baba',
    'أم': 'ommi',
    'أخ': 'khou',
    'أخت': 'okht',
    'عائلة': 'aayla',
    'ابن': 'wled',
    'ابنة': 'bent',
    'جد': 'jed',
    'جدة': 'jeda',

    # === TRANSPORT & LIEUX ===
    'السيارة': 'karhba',
    'القطار': 'metro',
    'الطائرة': 'tayara',
    'الحافلة': 'bus',
    'المطار': 'matar',
    'المستشفى': 'sbitar',
    'المدرسة': 'madrsa',
    'الجامعة': 'fac',
    'السوق': 'souk',
    'المدينة': 'mdina',
    'المطعم': 'resto',
    'المقهى': 'kahwa',
      # === NOURRITURE ===
    'خبز': 'khobz',
    'ماء': 'ma',
    'شاي': 'tay',
    'قهوة': 'kahwa',
    'لحم': 'lham',
    'دجاج': 'djaj',
    'سمك': 'hout',
    'ملح': 'melh',
    'سكر': 'soker',
    'فاكهة': 'ghala',
    'تفاح': 'toffah',
    'برتقال': 'lim',
    'موز': 'banan',

     # === TECHNOLOGIE ===
    'حاسوب': 'ordinateur',
    'هاتف': 'telifun',
    'إنترنت': 'internet',
    'ملف': 'fichee',
    'صورة': 'taswira',
    'برنامج': 'programme',

    'المنستير': 'mestir',

}
# Dictionnaire Translittération Darija -> Darija normalisé
DARIJA_NORMALIZATION = {
    # Variantes orthographiques courantes
    'ta7et': 'tahet',
    '7ala': 'hala',
    '7lila': 'hlila',
    '3alekher': 'alekher',
    '7ata': 'hata',
    'wa5ret': 'wakhret',
    '9a3din': 'kadin',
    'na7kiw': 'nahkiw',
    '3la': 'ala',
    'm3abba': 'maaba',
    '3ib': 'eib',
    '3malet': 'amelt',
    '9ass': 'kass',
    'ye5y': 'yekhy',
    '3alya': 'alya',
    '9wi': 'kwi',
    'tet3eda': 'tetada',
    '3aslema': 'aslema',

    'raw3a': 'rawaa',
    'raw3aa': 'rawaa',
    'raw3a': 'rawaa',
    'rou3a': 'rawaa',
    'barcha': 'barcha',
    'barchaa': 'barcha',
    'bercha': 'barcha',
    'barsha': 'barcha',
    'barshaa': 'barcha',
    '7ajet': 'hajet',
    '7weyej': 'hajet',
    '7aja': 'haja',
    '5ouya': 'khouya',
    '5oya': 'khouya',
    'kifech': 'kifech',
    'kifeh': 'kifech',
    'kifek': 'kifech',
    'chneya': 'chneya',
    'chnoua': 'chnoua',
    'chnowa': 'chnowa',
    'chnya': 'chnya',
    'wallahi': 'wallah',
    'walahi': 'wallah',
    'wlh': 'wallah',
    'wlhi' : 'wallah',
    '9ahwa': 'kahwa',
    '9ahaoua': 'kahwa',
    'm3a': 'maa',
    'b7ar': 'bhar',
    'ba7ar': 'bhar',
    'thama': 'fama',
    'thamma': 'fama',
    'famma': 'fama',
    'jaw': 'jaw',
    'jow': 'jaw',
    'ness': 'ness',
    'nas': 'ness',
    'naas': 'ness',
    'sa7': 'saha',
    'sa7a': 'saha',
    'mashi': 'machi',
    'ya3ni': 'yaani',
    'choufe': 'chouf',
    'shouf': 'chouf',
    'ra7': 'mcha',
    'msha': 'mcha',
    'mechi': 'mcha',
    'elyoum': 'lyoum',
    'lyom': 'lyoum',
    'leyouma': 'lyoum',
    # Lieux Monastir
    'monastir': 'mestir',
    'elmonstir': 'mestir',
    'el monastir': 'mestir',
    '5niss': 'khniss',
    'khnis': 'khniss',
    'usmonastir': 'us mestir',
    'steg': 'steg',
}
# Mots à garder tels quels (noms propres, etc.)
KEEP_AS_IS = {'steg', 'us', 'mestir', 'facebook', 'instagram', 'twitter'}


def normalize_to_darija(text):
    """
    Normalise le texte vers le Darija tunisien.
    Convertit Français, Arabe standard, et variantes Darija vers une forme commune.

       Pipeline: 
    1. Convertir les chiffres Darija (3, 7, 9, 5) vers lettres
    2. Chercher dans les dictionnaires de normalisation
    3. Convertir Français -> Darija
    4. Convertir Arabe -> Darija
    """
    text_lower = text.lower()
    words = text_lower.split()
    normalized_words = []
    
    for word in words:
        # Nettoyer la ponctuation
        clean_word = re.sub(r'[^\w\s]', '', word)
        punctuation = word[len(clean_word):] if len(word) > len(clean_word) else ''
        
        if not clean_word:
            continue
            
        # Garder certains mots tels quels
        if clean_word in KEEP_AS_IS:
            normalized_words.append(clean_word + punctuation)
            continue
        
        # ÉTAPE 1: Convertir les chiffres Darija vers lettres
        converted_word = convert_darija_numbers_smart(clean_word)
        
        # ÉTAPE 2: Vérifier dans le dictionnaire de normalisation Darija
        if converted_word in DARIJA_NORMALIZATION:
            normalized_words.append(DARIJA_NORMALIZATION[converted_word] + punctuation)
            continue
            
        # 2. Vérifier Français -> Darija
        if clean_word in FRENCH_TO_DARIJA:
            normalized_words.append(FRENCH_TO_DARIJA[clean_word] + punctuation)
            continue
            
        # 3. Vérifier Arabe -> Darija
        if clean_word in ARABIC_TO_DARIJA:
            normalized_words.append(ARABIC_TO_DARIJA[clean_word] + punctuation)
            continue
        
        # 4. Convertir les chiffres arabes (3, 7, 9, 5, 2) - garder tels quels en Darija
        # Le mot reste en Darija translittéré
        normalized_words. append(clean_word + punctuation)
    
    return ' '. join(normalized_words)


def normalize_arabic_chars(text):
    """Normalise les caractères arabes."""
    # Supprimer diacritiques arabes
    arabic_diacritics = re.compile(r'[\u064B-\u065F\u0670]')
    text = re.sub(arabic_diacritics, '', text)
    
    # Normaliser caractères arabes
    replacements = {
        'أ': 'ا', 'إ': 'ا', 'آ': 'ا',
        'ى': 'ي', 'ة': 'ه',
        'ؤ': 'ء', 'ئ': 'ء'
    }
    for ar, repl in replacements.items():
        text = text.replace(ar, repl)
    
    return text


def normalize_text(text):
    """Pipeline de normalisation complète vers Darija."""
    # 1. Supprimer les emojis
    text = remove_emojis(text)
    
    # 2. Normaliser caractères arabes
    text = normalize_arabic_chars(text)
    
    # 3.  Convertir vers Darija
    text = normalize_to_darija(text)
    
    # 4. Nettoyer espaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def detect_language(text):
    """Détecte la langue originale du texte."""
    arabic_chars = len(re.findall(r'[\u0600-\u06FF]', text))
    latin_chars = len(re.findall(r'[a-zA-Z]', text))
    has_darija_numbers = any(c in text for c in ['3', '7', '9', '5', '2'])
    
    if arabic_chars > latin_chars:
        return 'ar'
    elif has_darija_numbers:
        return 'da'
    elif any(w in text. lower() for w in ['le', 'la', 'les', 'un', 'une', 'est', 'sont', 'avec']):
        return 'fr'
    elif latin_chars > 0:
        return 'da'  # Darija en caractères latins
    return 'da'


# ============================================
# 3. DATA AUGMENTATION
# ============================================
SYNONYMS_DARIJA = {
    'raw3a': ['hbel', 'rawaa', 'momtez'],
    'behi': ['mezyen', 'bnin', 'temem'],
    '5ayeb': ['mouch behi', 'fdhiha'],
}


def augment_with_synonyms(text):
    """Remplace aléatoirement des mots par leurs synonymes en Darija."""
    words = text.split()
    augmented_words = []
    
    for word in words:
        if word in SYNONYMS_DARIJA and random.random() > 0.5:
            augmented_words. append(random.choice(SYNONYMS_DARIJA[word]))
        else:
            augmented_words. append(word)
    
    return ' '.join(augmented_words)


def augment_by_deletion(text, p=0.1):
    """Supprime aléatoirement des mots."""
    words = text.split()
    if len(words) <= 3:
        return text
    return ' '.join([w for w in words if random.random() > p])


def augment_by_swap(text):
    """Échange aléatoirement deux mots adjacents."""
    words = text. split()
    if len(words) < 2:
        return text
    idx = random.randint(0, len(words) - 2)
    words[idx], words[idx + 1] = words[idx + 1], words[idx]
    return ' '.join(words)


def generate_augmented_samples(text, num_augmentations=3):
    """Génère plusieurs variations d'un texte."""
    augmentations = [text]
    
    for _ in range(num_augmentations):
        aug_type = random.choice(['synonym', 'deletion', 'swap'])
        if aug_type == 'synonym':
            augmentations.append(augment_with_synonyms(text))
        elif aug_type == 'deletion':
            augmentations.append(augment_by_deletion(text))
        else:
            augmentations.append(augment_by_swap(text))
    
    return list(set(augmentations))


# ============================================
# 4. PIPELINE COMPLET
# ============================================
def process_post(post, augment=False, num_augmentations=2):
    """Pipeline complet de traitement d'un post."""
    text = post.get('text', '')
    
    # Étape 1: Extraire les emojis ET leur sentiment
    emoji_data = extract_emoji_sentiment(text)
    
    # Étape 2: Détecter la langue originale
    original_lang = detect_language(text)
    
    # Étape 3: Normaliser vers Darija
    clean_text = normalize_text(text)
    
    # Créer le post enrichi
    processed_post = post.copy()
    processed_post. update({
        'original_text': text,
        'clean_text': clean_text,
        'original_lang': original_lang,
        'normalized_lang': 'darija',
        'emoji_sentiment': emoji_data,
    })
    
    results = [processed_post]
    
    # Étape 4: Data Augmentation
    if augment:
        augmented_texts = generate_augmented_samples(clean_text, num_augmentations)
        for aug_text in augmented_texts[1:]:
            aug_post = processed_post.copy()
            aug_post['clean_text'] = aug_text
            aug_post['is_augmented'] = True
            results.append(aug_post)
    
    return results


# ============================================
# 5.  TRAITEMENT DU FICHIER FINAL_EVALUATION_SET
# ============================================
def process_evaluation_data(input_path, output_path, augment=False, num_augmentations=2):
    """
    Traite le fichier final_evaluation_set.json et sauvegarde les résultats. 
    
    Args:
        input_path: Chemin vers le fichier d'entrée JSON
        output_path: Chemin vers le fichier de sortie JSON
        augment: Activer l'augmentation de données
        num_augmentations: Nombre de variations à générer
    """
    
    print("=" * 70)
    print("🚀 SOCIALPULSE MONASTIR - Preprocessing Pipeline")
    print("=" * 70)
    
    # Vérifier que le fichier existe
    if not os.path.exists(input_path):
        print(f"❌ Erreur: Fichier non trouvé: {input_path}")
        return None
    
    # Charger les données
    print(f"\n📂 Chargement des données depuis: {input_path}")
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"✅ {len(data)} posts chargés")
    
    # Statistiques
    stats = {
        'total_input': len(data),
        'total_output': 0,
        'by_original_lang': {'ar': 0, 'fr': 0, 'da': 0},
        'by_emoji_sentiment': {'positive': 0, 'negative': 0, 'neutral': 0},
        'posts_with_emojis': 0,
        'total_emojis_found': 0,
        'augmented_samples': 0
    }
    
    # Traiter chaque post
    print(f"\n🔄 Traitement en cours...")
    all_results = []
    
    for i, post in enumerate(data):
        # Traitement
        results = process_post(post, augment=augment, num_augmentations=num_augmentations)
        
        for result in results:
            all_results.append(result)
            
            # Mise à jour des statistiques
            lang = result.get('original_lang', 'da')
            stats['by_original_lang'][lang] = stats['by_original_lang']. get(lang, 0) + 1
            
            emoji_sent = result['emoji_sentiment']['dominant_sentiment']
            stats['by_emoji_sentiment'][emoji_sent] += 1
            
            if result['emoji_sentiment']['emoji_count'] > 0:
                stats['posts_with_emojis'] += 1
                stats['total_emojis_found'] += result['emoji_sentiment']['emoji_count']
            
            if result. get('is_augmented'):
                stats['augmented_samples'] += 1
        
        # Afficher la progression
        if (i + 1) % 10 == 0 or i == 0:
            print(f"   Traité: {i + 1}/{len(data)} posts")
    
    stats['total_output'] = len(all_results)
    
    # Créer le dossier de sortie si nécessaire
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Sauvegarder les résultats
    print(f"\n💾 Sauvegarde des résultats vers: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        json. dump(all_results, f, ensure_ascii=False, indent=2)
    
    print(f"✅ {len(all_results)} posts sauvegardés")
    
    # Afficher les statistiques
    print("\n" + "=" * 70)
    print("📊 STATISTIQUES")
    print("=" * 70)
    
    print(f"\n📌 Posts traités:")
    print(f"   • Input: {stats['total_input']} posts")
    print(f"   • Output: {stats['total_output']} posts")
    if augment:
        print(f"   • Augmentés: {stats['augmented_samples']} nouveaux samples")
    
    print(f"\n🌍 Répartition par langue originale:")
    for lang, count in stats['by_original_lang'].items():
        if count > 0:
            pct = (count / stats['total_output']) * 100
            bar = "█" * int(pct / 5)
            print(f"   • {lang}: {count} ({pct:.1f}%) {bar}")
    
    print(f"\n😀 Emojis:")
    print(f"   • Posts avec emojis: {stats['posts_with_emojis']}")
    print(f"   • Total emojis trouvés: {stats['total_emojis_found']}")
    
    print(f"\n📊 Sentiment (basé sur emojis):")
    print(f"   • ✅ Positif: {stats['by_emoji_sentiment']['positive']}")
    print(f"   • ❌ Négatif: {stats['by_emoji_sentiment']['negative']}")
    print(f"   • ⚪ Neutre: {stats['by_emoji_sentiment']['neutral']}")
    
    # Afficher quelques exemples
    print("\n" + "=" * 70)
    print("📝 EXEMPLES DE RÉSULTATS")
    print("=" * 70)
    
    for i, result in enumerate(all_results[:5]):
        print(f"\n{'─'*70}")
        print(f"Post #{i+1}")
        print(f"{'─'*70}")
        original = result.get('original_text', result.get('text', ''))[:60]
        print(f"📌 Original: {original}...")
        print(f"🔄 Normalisé: {result['clean_text'][:60]}...")
        print(f"🌍 Langue: {result['original_lang']} → darija")
        print(f"😀 Sentiment emoji: {result['emoji_sentiment']['dominant_sentiment']} (score: {result['emoji_sentiment']['avg_score']})")
        if result['emoji_sentiment']['emojis']:
            emojis = [(e['emoji'], e['label_darija']) for e in result['emoji_sentiment']['emojis'][:4]]
            print(f"   Emojis: {emojis}")
    
    print("\n" + "=" * 70)
    print("✅ TRAITEMENT TERMINÉ!")
    print("=" * 70)
    
    return all_results, stats


# ============================================
# MAIN - EXÉCUTION
# ============================================
if __name__ == "__main__":
    # Déterminer le chemin de base (racine du projet)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)  # Remonter d'un niveau (de src/ vers racine)
    
    # Chemins des fichiers
    input_file = os.path.join(project_root, 'data', 'processed', 'final_evaluation_set.json')
    output_file = os.path.join(project_root, 'data', 'processed', 'result_after_validation.json')
    
    print(f"\n📁 Chemin d'entrée: {input_file}")
    print(f"📁 Chemin de sortie: {output_file}")
    
    # Traiter les données (sans augmentation pour la validation)
    results, stats = process_evaluation_data(
        input_path=input_file,
        output_path=output_file,
        augment=False,  # Mettre True pour activer l'augmentation
        num_augmentations=2
    )
    
    # Optionnel: Générer aussi une version augmentée
    print("\n" + "=" * 70)
    print("📈 Génération du dataset augmenté...")
    print("=" * 70)
    
    output_augmented = os.path.join(project_root, 'data', 'processed', 'result_augmented.json')
    results_aug, stats_aug = process_evaluation_data(
        input_path=input_file,
        output_path=output_augmented,
        augment=True,
        num_augmentations=3
    )



# ============================================
# TESTS

# if __name__ == "__main__":

 #   print("=" * 60)
 #   print("TEST: Normalisation vers Darija Tunisien")
  #  print("=" * 60)
    
  #  test_posts = [
        # Darija original
    #    {"id": 1, "text": "El jaw fi monastir raw3a 😍🔥 barcha ness fel plage! "},
        
        # Français
   #     {"id": 2, "text": "La plage de Monastir est magnifique aujourd'hui!  🏖️"},
        
        # Arabe standard
    #    {"id": 3, "text": "الطقس جميل في المنستير اليوم ☀️"},
        
        # Mix
    #    {"id": 4, "text": "Panne de courant à Khniss 😡 barcha mochkla! "},
        
        # Darija avec variantes
      #  {"id": 5, "text": "Kifech el jaw lyoum?  Thama barcha ness fel b7ar"},
 #   ]
    
  #  for post in test_posts:
  #      print(f"\n{'='*60}")
  #      print(f"Post ID: {post['id']}")
  #      print(f"Original: {post['text']}")
        
    #    results = process_post(post, augment=False)
    #    result = results[0]
    #    
   #     print(f"Langue originale: {result['original_lang']}")
    #    print(f"Normalisé (Darija): {result['clean_text']}")
    #    print(f"Emoji sentiment: {result['emoji_sentiment']['dominant_sentiment']}")
       # if result['emoji_sentiment']['emojis']:
       #     print(f"Emojis: {[(e['emoji'], e['label_darija']) for e in result['emoji_sentiment']['emojis']]}")
    
  #  print(f"\n{'='*60}")
  #  print("TEST: Data Augmentation en Darija")
  #  print("=" * 60)
    
   # sample = {"id": 99, "text": "El jaw raw3a barcha fi mestir! "}
  #  results = process_post(sample, augment=True, num_augmentations=3)
    
   # print(f"\nOriginal: {sample['text']}")
   # for i, r in enumerate(results):
   #     aug_label = " (augmenté)" if r. get('is_augmented') else " (original)"
   #     print(f"  {i+1}. {r['clean_text']}{aug_label}")
        # ============================================