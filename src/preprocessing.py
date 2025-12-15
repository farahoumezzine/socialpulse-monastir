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
      # Positifs supplémentaires
    '💃':  {'sentiment': 'positive', 'score': 0.9, 'label': 'jaw'},
    '😌': {'sentiment': 'positive', 'score': 0.7, 'label': 'mertah'},
    '💙': {'sentiment': 'positive', 'score': 1, 'label': 'hob'},
    '🌞': {'sentiment': 'positive', 'score': 0.8, 'label': 'chams'},
    '🙌':  {'sentiment': 'positive', 'score': 0.9, 'label': 'tok_aleha'},
    '❤':  {'sentiment': 'positive', 'score': 1, 'label': 'hob'},
    '🌅': {'sentiment': 'positive', 'score': 0.8, 'label': 'ghroub'},
    '🏆': {'sentiment': 'positive', 'score': 1, 'label': 'rebeh'},
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
      # Négatifs supplémentaires
    '🤢': {'sentiment': 'negative', 'score': -0.9, 'label':  'mokref'},
    '😕': {'sentiment': 'negative', 'score': -0.5, 'label': 'mech_fehim'},
    '😓': {'sentiment': 'negative', 'score': -0.6, 'label': 'taab'},
    '🥴':  {'sentiment': 'negative', 'score': -0.5, 'label': 'mouch_merteh'},
    # Neutre
    '🤔': {'sentiment': 'neutral', 'score': 0, 'label': 'yfaker'},
    '🤷': {'sentiment': 'neutral', 'score': 0, 'label': 'marefch'},
    '📍': {'sentiment': 'neutral', 'score': 0, 'label': 'blasa'},
    '📸': {'sentiment': 'neutral', 'score': 0, 'label': 'taswira'},
    '🚗': {'sentiment': 'neutral', 'score': 0, 'label': 'karhba'},
    '🏖️': {'sentiment': 'neutral', 'score': 0.3, 'label': 'bhar'},
    '⚽': {'sentiment': 'neutral', 'score': 0.2, 'label': 'koura'},
    '🏨': {'sentiment': 'neutral', 'score': 0, 'label': 'hotel'},
    '🏛': {'sentiment': 'neutral', 'score': 0, 'label': 'maalem'},
    # Neutres supplémentaires
    '☕': {'sentiment': 'neutral', 'score': 0.2, 'label': 'kahwa'},
    '🏀': {'sentiment': 'neutral', 'score': 0.2, 'label': 'basket'},
    '🛴': {'sentiment': 'neutral', 'score': 0, 'label': 'trotinette'},
    '📅':  {'sentiment': 'neutral', 'score': 0, 'label': 'date'},
    '📽': {'sentiment': 'neutral', 'score': 0, 'label': 'film'},
    '📖': {'sentiment': 'neutral', 'score': 0.2, 'label': 'kteb'},
    '🎤': {'sentiment': 'neutral', 'score': 0.3, 'label': 'micro'},
    '😐': {'sentiment': 'neutral', 'score': 0, 'label': 'normal'},
    '📚': {'sentiment': 'neutral', 'score': 0.2, 'label': 'ktob'},
    '💡': {'sentiment': 'neutral', 'score': 0.1, 'label': 'fikra'},
    '🎭': {'sentiment': 'neutral', 'score': 0.3, 'label': 'masrah'},
    '🎨': {'sentiment': 'neutral', 'score': 0.4, 'label': 'fann'},
    '🥬': {'sentiment': 'neutral', 'score': 0, 'label': 'khodhra'},
    '🍳':  {'sentiment': 'neutral', 'score': 0.1, 'label': 'tabkh'},
    '👩': {'sentiment': 'neutral', 'score': 0, 'label': 'mra'},
    '📢': {'sentiment': 'neutral', 'score': 0, 'label': 'ilan'},
}

# ============================================
# EMOJIS CONTEXTUELS (Ambigus)
# ============================================
CONTEXT_DEPENDENT_EMOJIS = {
    '🔊': {
        'positive_context': ['festival', 'fete', 'jaw', 'ambiance', 'musique', 'hbel', 'rawaa', 'heyel', 'concert', 'party', 'sahriya', 'match'],
        'negative_context': ['bruit', 'kwi', 'derangement', 'sot', 'ali', 'barcha', 'mochkla', 'hess'],
        'positive_label': 'ambiance',
        'negative_label': 'sot_ali',
        'neutral_label': 'sot',
        'positive_score': 0.6,
        'negative_score':  -0.5,
    },
    '🚧':  {
        'positive_context':  ['tajdid', 'isalhou', 'tahsin', 'travaux', 'amelioration'],
        'negative_context': ['zahma', 'trafic', 'mochkla', 'nestanaw', 'retard', 'habsin', 'msaker'],
        'positive_label': 'islah',
        'negative_label': 'achghal',
        'neutral_label': 'achghal',
        'positive_score': 0.3,
        'negative_score':  -0.4,
    },
    '😬': {
        'positive_context': ['hbel', 'rawaa', 'excitement', 'suspense', 'jaw'],
        'negative_context': ['mochkla', 'khayeb', 'ghalat', 'fdhiha'],
        'positive_label': 'excite',
        'negative_label':  'mech_merta7',
        'neutral_label': 'mech_merta7',
        'positive_score': 0.4,
        'negative_score':  -0.4,
    },
    '🌙': {
        'positive_context': ['festival', 'sahriya', 'fete', 'lila', 'ramadan', 'sohour', 'ambiance', 'concert'],
        'negative_context': ['nejmech_norked', 'insomnie', 'taab', 'mochkla','jenich_noum'],
        'positive_label': 'lila_helwa',
        'negative_label':  'lil',
        'neutral_label': 'lil',
        'positive_score': 0.5,
        'negative_score':  -0.3,
    },
    '⏰': {
        'positive_context': ['wakt', 'bda', 'commence', 'rappel'],
        'negative_context': ['retard', 'makher', 'fout', 'fisa', 'testana', 'mochkla'],
        'positive_label': 'wa9t',
        'negative_label':  'takhir',
        'neutral_label': 'wa9t',
        'positive_score': 0.2,
        'negative_score':  -0.4,
    },
}


def get_emoji_sentiment_with_context(emoji_char, text):
    """
    Détermine le sentiment d'un emoji selon le contexte de la phrase.
    
    Args:
        emoji_char: L'emoji à analyser
        text: Le texte complet contenant l'emoji
    
    Returns:
        dict: {'sentiment': str, 'score':  float, 'label': str}
    """
    # Si l'emoji n'est pas ambigu, utiliser le mapping normal
    if emoji_char not in CONTEXT_DEPENDENT_EMOJIS:
        if emoji_char in EMOJI_SENTIMENT_MAP:
            info = EMOJI_SENTIMENT_MAP[emoji_char]
            return {
                'sentiment': info['sentiment'],
                'score': info['score'],
                'label': info['label']
            }
        # Emoji inconnu
        return {'sentiment': 'neutral', 'score': 0, 'label': 'emoji'}
    
    # Emoji ambigu - analyser le contexte
    context_info = CONTEXT_DEPENDENT_EMOJIS[emoji_char]
    text_lower = text.lower()
    
    # Compter les mots de contexte positif et négatif
    positive_count = sum(1 for word in context_info['positive_context'] if word in text_lower)
    negative_count = sum(1 for word in context_info['negative_context'] if word in text_lower)
    
    # Décider selon le contexte dominant
    if positive_count > negative_count:
        return {
            'sentiment': 'positive',
            'score': context_info['positive_score'],
            'label': context_info['positive_label']
        }
    elif negative_count > positive_count:
        return {
            'sentiment': 'negative',
            'score': context_info['negative_score'],
            'label': context_info['negative_label']
        }
    else: 
        # Contexte neutre ou égalité
        return {
            'sentiment': 'neutral',
            'score': 0,
            'label': context_info['neutral_label']
        }
    
def extract_emoji_sentiment(text):
    """
    Extrait les emojis du texte et calcule un score de sentiment agrégé.
    Utilise l'analyse contextuelle pour les emojis ambigus. 
    """
    found_emojis = []
    total_score = 0
    emoji_count = 0
    
    for char in text:
        if char in EMOJI_SENTIMENT_MAP or char in CONTEXT_DEPENDENT_EMOJIS:
            # Utiliser l'analyse contextuelle
            emoji_info = get_emoji_sentiment_with_context(char, text)
            found_emojis.append({
                'emoji': char,
                'sentiment': emoji_info['sentiment'],
                'score': emoji_info['score'],
                'label_darija': emoji_info['label']
            })
            total_score += emoji_info['score']
            emoji_count += 1
        elif emoji. is_emoji(char):
            # Emoji non mappé - traité comme neutre
            found_emojis.append({
                'emoji':  char,
                'sentiment': 'neutral',
                'score':  0,
                'label_darija': 'emoji'
            })
            emoji_count += 1
    
    avg_score = total_score / emoji_count if emoji_count > 0 else 0
    
    return {
        'emojis': found_emojis,
        'emoji_count': emoji_count,
        'total_score': round(total_score, 2),
        'avg_score': round(avg_score, 2),
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
    'route': 'trik',
    
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
    'tortue' : 'soulehfet',
    'sauvée' : 'monktha',

    'vaccination': 'talkih',
    'gratuite' : 'blech',
    'chats' : 'ktates',
    'chiens' : 'klab',
    'campagne' : 'hemla',

   'inquiète' : 'yhazen',
    'autorités' : 'masoulin',
    'tunisiennes' : 'twensa',

    'coupures' : 'kassen',
    'électricité' : 'dhaw',
    'zones' : 'manatek',
    'concernées' : 'eli ihemha',

     # === Jours de la semaine ===
    'dimanche': 'el had',
    'lundi':   'etnin',
    'mardi':  'ethlatha',
    'mercredi':  'elarbaa',
    'jeudi': 'elkhmis',
    'vendredi': 'ejjomaa',
    'samedi':  'essebt',

    'et' : 'w',
    'à' : 'fi',
    'ce': 'hadha',
    'cet': 'hadha',
    'cette': 'hedhi',
    'ces': 'hedhom',
 
    'dans': 'fi',
    'parc': 'hadika',
     'rentre': 'yarja',
    'parc': 'hadika',
    'chaque': 'koll',
    'fois': 'marra',

        'je': 'ani',
        'vois': 'nchouf',

        
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
     # === Verbes ===
    'protéger': 'nahmiw',
    'proteger': 'nahmiw',
    'protège': 'nahmi',
    'protegeons': 'nahmiwha',
    
    # === Possessifs ===
    'notre': 'mtaana',
    'nos': 'mtaana',
    'votre': 'mtaakom',
    'vos': 'mtaakom',
    'leur': 'mtaahom',
    'leurs': 'mtaahom',
    'mon': 'mtaai',
    'ma': 'mtaai',
    'mes': 'mtaai',
    'ton': 'mtaak',
    'ta': 'mtaak',
    'tes': 'mtaak',
    'son': 'mtaah',
    'sa': 'mtaah',
    'ses': 'mtaahom',
    
    # === Expressions ===
    "c'est": 'howa',
    'cest': 'howa',
    "c'était": 'ken',
    'cetait': 'ken',
    
    # === Vie / Nature ===
    'vie': 'hayet',
    'la vie': 'el hayet',
    'mort': 'mott',
    'nature': 'tabiaa',
    'environnement': 'biaa',
    'pollution': 'talawoth',
    
    # === Articles ===
    'le': 'el',
    'la':  'el',
    'les': 'el',
    'un': 'wahed',
    'une': 'wahda',
    'des': '',
    
    # === Pronoms ===
    'il': 'houwa',
    'elle': 'hiya',
    'ils': 'houma',
    'elles': 'houma',
    'nous': 'ahna',
    'vous': 'entouma',
    'on': 'ahna',
    
    # === Autres verbes courants ===
    'est': 'howa',
    'sont': 'houma',
    'suis': 'ena',
    'es': 'enti',
    'sommes': 'ahna',
    'êtes': 'entouma',
    'avoir': 'andou',
    'ai': 'andi',
    'as': 'andek',
    'a': 'andou',
    'avons': 'andna',
    'avez': 'andkom',
    'ont': 'andhom',
    'faire': 'naamel',
    'fait': 'aamel',
    'aimer': 'nheb',
    'aime': 'nheb',
}

# ============================================
# TRANSLITTÉRATION ARABE → DARIJA LATIN
# ============================================

# Mapping des lettres arabes vers caractères latins (Darija tunisien)
ARABIC_TO_LATIN = {
    # Lettres de base
    'ا': 'a',
    'أ': 'a',
    'إ': 'i',
    'آ': 'a',
    'ب': 'b',
    'ت':  't',
    'ث': 'th',
    'ج': 'j',
    'ح': 'h',
    'خ': 'kh',
    'د': 'd',
    'ذ': 'dh',
    'ر': 'r',
    'ز':  'z',
    'س': 's',
    'ش': 'ch',
    'ص': 's',
    'ض':  'dh',
    'ط':  't',
    'ظ': 'dh',
    'ع':  'a',
    'غ': 'gh',
    'ف': 'f',
    'ق': 'k',
    'ك': 'k',
    'ل': 'l',
    'م': 'm',
    'ن': 'n',
    'ه': 'h',
    'ة': 'a',
    'و': 'w',
    'ي': 'y',
    'ى': 'a',
    'ء': '',
    'ئ': 'i',
    'ؤ': 'ou',
    
    # Voyelles longues / diacritiques (si présents)
    'َ': 'a',   # Fatha
    'ِ':  'i',   # Kasra
    'ُ': 'ou',  # Damma
    'ً': 'an',  # Tanwin fath
    'ٍ': 'in',  # Tanwin kasr
    'ٌ': 'on',  # Tanwin damm
    'ْ': '',    # Sukun
    'ّ': '',    # Shadda (on double la lettre précédente)
}
# ============================================
# DICTIONNAIRE ARABE → DARIJA LATIN (Fusionné)
# ============================================
ARABIC_WORDS_TO_DARIJA_LATIN = {
    # === SENTIMENTS ===
    'جميل': 'mezyan',
    'جميلة': 'mezyaa',
    'جميله': 'mezyaa', 
    'رائع': 'heyel',
    'رائعة': 'heyla',
    'رائعه': 'heyla',
    'ممتاز': 'momtez',
    'سيء': 'khayeb',
    'خايب': 'khayeb',
    'مشكلة': 'mochkla',
    'مشكله': 'mochkla',
    'مشاكل': 'machakel',
    'حزين': 'hzin',
    'حزينة':  'hzina',
    'حزينه': 'hzina',
    'فرحان': 'farhan',
    'فرحانة': 'farhana',
    'فرحانه': 'farhana',
    'سعيد': 'farhan',
    'سعيدة': 'farhana',
    'سعيده': 'farhana',
    'تعب': 'taab',
    'تعبة':  'taaba',
    'تعبه': 'taaba',
    'تعبان': 'taaban',
    'تعبانة': 'taabana',
    'تعبانه': 'taabana',
    # === TEMPS ===
    'اليوم': 'lyoum',
    'غدوة': 'ghodwa',
    'غدا': 'ghodwa',
    'البارح': 'lbereh',
    'أمس': 'lbereh',
    'توا': 'tawa',
    'الآن': 'tawa',
    'دايما': 'dima',
    'دائما': 'dima',
    'برشا': 'barcha',
    'كثير': 'barcha',
    'ياسر': 'yesser',
    'شوية': 'chwaya',
    'قليل': 'chwaya',
    'يوم': 'nhar',
    'ليل': 'lil',
    'صباح': 'sbeh',
    'مساء': 'achiya',
    
    # === LIEUX ===
    'البحر': 'bhar',
    'الشاطئ': 'chatt',
    'المدينة': 'mdina',
    'البلاد': 'bled',
    'الحومة': 'houma',
    'الدار': 'dar',
    'المنزل': 'dar',
    'السوق': 'souk',
    'الجامع': 'jemaa',
    'المطار': 'matar',
    'المحطة': 'mahata',
    'السبيطار': 'sbitar',
    'المستشفى': 'sbitar',
    'المدرسة': 'madrsa',
    'الجامعة': 'fac',
    'الكورنيش': 'corniche',
    'الملعب': 'stade',
    'الرباط': 'ribat',
    'قصر': 'ksar',
    'المركب': 'morakeb',
    'الطريق': 'trik',
    'المنستير': 'mestir',
    'المستير': 'mestir',
    'منستير': 'mestir',
    'المطعم': 'resto',
    'المقهى': 'kahwa',
    
    # === PERSONNES ===
    'الناس': 'ness',
    'ناس': 'ness',
    'صاحبي': 'sahbi',
    'صديق': 'sahbi',
    'صديقة': 'sahebti',
    'خويا': 'khouya',
    'أخ': 'khou',
    'أختي': 'okhti',
    'أخت': 'okht',
    'العايلة': 'ayla',
    'عائلة': 'ayla',
    'الصغار': 'sghar',
    'أطفال': 'sghar',
    'راجل': 'rajel',
    'رجل': 'rajel',
    'مرا': 'mra',
    'امرأة': 'mra',
    'أب': 'baba',
    'أم': 'ommi',
    'ابن': 'wled',
    'ابنة':  'bent',
    'جد': 'jed',
    'جدة': 'jeda',
    
    # === TRANSPORT ===
    'الكرهبة': 'karhba',
    'كرهبة': 'karhba',
    'السيارة': 'karhba',
    'الكار': 'kar',
    'الحافلة': 'kar',
    'الطاكسي': 'taxi',
    'الميترو': 'metro',
    'القطار': 'metro',
    'الطائرة': 'tayara',
    'زحمة': 'zahma',
    'الزحمة': 'zahma',
    
    # === MÉTÉO ===
    'الجو': 'jaw',
    'جو': 'jaw',
    'الطقس': 'jaw',
    'الشمس': 'chams',
    'شمس': 'chams',
    'سخون': 'skhoun',
    'حار': 'skhoun',
    'برد': 'bard',
    'بارد': 'bard',
    'مطر': 'mtar',
    'ريح': 'rih',
    
    # === ACTIONS ===
    'ناكل': 'nekel',
    'أكل': 'mekla',
    'نشرب': 'nochreb',
    'شرب':  'chrab',
    'نرقد': 'norked',
    'نوم':  'rked',
    'نخدم': 'nekhdem',
    'عمل': 'khedma',
    'العمل': 'khedma',
    'نمشي': 'nemchi',
    'نجي': 'nji',
    'نشوف': 'nchouf',
    'نتفرج': 'netfarej',
    'نستنى': 'nestana',
    'نرجع': 'narja',
    'نخرج': 'nokhrej',
    
    # === QUESTIONS ===
    'شنوة': 'chnoua',
    'ماذا': 'chnoua',
    'كيفاش': 'kifech',
    'كيف': 'kifech',
    'علاش': 'alech',
    'لماذا': 'alech',
    'وين': 'win',
    'أين': 'win',
    'وقتاش': 'wakteh',
    'متى': 'wakteh',
    'شكون': 'chkoun',
    'من': 'men',
    'شيء': 'chy',
    'وزين': 'w mezyan',
    'التأخير': 'tawkhir',
    'تذمّوا': 'tdhamrou',
    'فولكلور': 'folklore',
    # === CHIFFRES ===
    'واحد': 'wahed',
    'اثنان':  'zouz',
    'ثلاثة': 'thletha',
    'أربعة': 'arbaa',
    'خمسة': 'khamsa',
    'ستة': 'setta',
    'سبعة': 'sebaa',
    'ثمانية': 'thmenia',
    'تسعة': 'tesaa',
    'عشرة': 'achra',
    
    # === MAISON & OBJETS ===
    'غرفة': 'bit',
    'غرفه': 'bit',
    'مطبخ': 'koujina',
    'حمام': 'hamem',
    'باب': 'beb',
    'نافذة': 'chobek',
    'سرير': 'srir',
    'كرسي': 'korsi',
    'طاولة': 'tawle',
    'مفتاح': 'mefteh',
    'نار':  'nar',
    'ثلاجة': 'frigidaire',
    
    # === NOURRITURE ===
    'خبز': 'khobz',
    'ماء':  'ma',
    'شاي': 'tey',
    'قهوة': 'kahwa',
    'لحم': 'lham',
    'دجاج': 'djej',
    'سمك':  'hout',
    'ملح': 'melh',
    'سكر':  'sokkar',
    'فاكهة': 'ghalla',
    'تفاح': 'toffeh',
    'برتقال': 'bordgen',
    'موز': 'banane',
       # === MOIS ===
    'يناير': 'janvier',
    'جانفي': 'janvier',
    'فبراير':  'fevrier',
    'فيفري': 'fevrier',
    'مارس':  'mars',
    'أبريل': 'avril',
    'افريل': 'avril',
    'ماي': 'mai',
    'مايو': 'mai',
    'يونيو': 'juin',
    'جوان':  'juin',
    'يوليو': 'juillet',
    'جويلية': 'juillet',
    'أغسطس': 'aout',
    'اوت': 'aout',
    'سبتمبر': 'septembre',
    'أكتوبر': 'octobre',
    'اكتوبر': 'octobre',
    'نوفمبر': 'novembre',
    'ديسمبر': 'decembre',
    # === TECHNOLOGIE ===
    'حاسوب': 'pc',
    'هاتف': 'portable',
    'إنترنت': 'internet',
    'صورة': 'taswira',
    
    # === ÉVÉNEMENTS ===
    'حفلة': 'hafla',
    'حفله': 'hafla',
    'عرض': 'ardh',
    'مباراة': 'match',
    'مباراه': 'match',
    'كرة': 'koura',
    'كره':  'koura',
    'فيلم': 'film',
    'مسرح': 'masrah',
    'موسيقى': 'mousika',

    'فن': 'fann',
    'ثقافة': 'thakafa',
    'سياحة': 'siyeha',
    'عطلة': 'otla',
    'مهرجان': 'mahrejen',
    'تنظيم': 'tandhim',
    'تأخير': 'takhir',
    
    # === EXPRESSIONS ===
    'والله': 'wallah',
    'يعني': 'yaani',
    'برك': 'bark',
    'زعمة': 'zaama',
    'باهي': 'behi',
    'صحة': 'saha',
    'عسلامة': 'aslema',
    'الخير': 'khir',
    'ليلة': 'lila',
    'مبروك': 'mabrouk',
    
    # === MOTS SPÉCIFIQUES AUX DONNÉES ===
    'الدنيا': 'denya',
    'حلوة': 'hlowa',
    'حلوه': 'hlowa',    
    'حلو': 'hlou',
    'معبي': 'maabi',
    'معبّي': 'maabi',
    'الافتتاح': 'eftiteh',
    'الكبير': 'kbir',
    'كبير': 'kbir',
    'متاع': 'mtaa',
    'صراحة': 'sraha',
    'التوقعات': 'tawakkoaat',
    'تذكير': 'tadhkir',
    'عند': 'and',
    'على': 'ala',
    'الساعة': 'saa',
    'عامر': 'amer',
    'قوية': 'kwiya',
    'قويه':  'kwiya',
    'قوي': 'kwi',
    'تشجع': 'tchajaa',
    'بكري': 'bekri',
    'جديدة': 'jdida',
    'جديده':  'jdida',
    'جديد': 'jdid',
    'الإضاءة': 'dhaw',
    'المقابلة': 'match',
    'تعطلت': 'taatlet',
    'الطبخ': 'tabkh',
    'المركزي': 'markazi',
    'خضر': 'khodhra',
    'طازجة': 'tazja',
    'طازجه': 'tazja',
    'طماطم': 'tmatem',
    'بنينة': 'bnina',
    'بنينه': 'bnina',
    'بنين': 'bnin',
    'عروض': 'oroudh',
    'البهجة': 'behja',
    'الشارع': 'cheraa',
    'قدام': 'koddem',
    'التصاور': 'tsawer',
    'سياحي': 'siyehi',
    'منظم': 'mnadhem',
    'مزيان': 'mezyen',
    'الصوت': 'sot',
    'القاعة': 'salla',
    'مزعج': 'ikalek',
    'جمعة': 'jomaa',
    'ثقافية': 'thakafiya',
    'ثقافيه': 'thakafiya',
    'معرض': 'maaredh',
    'كتب': 'kotob',
    'صغير': 'sghir',
    'صغيرة': 'sghira',
    'صغيره': 'sghira',
    'للكورنيش': 'lel_corniche',
    'الغروب': 'ghroub',
    'هادي': 'hedi',
    'زين': 'zin',
    'المسرحي': 'masrahi',
    'ضعيف': 'dhaif',
    'شوي': 'chwi',
    'المنطقة': 'mantka',
    'طرقات': 'torkaat',
    'صيانة': 'siyana',
    'المرور': 'morour',
    'أخبار': 'akhbar',
    'سريعة': 'sriaa',
    'سريعه': 'sriaa',
    'ندوة': 'nadwa',
    'ندوه': 'nadwa',
    'العلوم': 'oloum',
    'مشاريع': 'macharia',
    'جامعة': 'jemaa',
    'صورة': 'soura',
    'صوره': 'soura',
    'المستوى': 'mostwa',
    'كلية': 'koliya',
    'نقص': 'noks',
    'الطلبة': 'talaba',
    'أيام': 'ayem',
    'سينما': 'cinema',
    'تحت': 'taht',
    'النجوم': 'njoum',
    'السهرة': 'sahra',
    'طويلة': 'twila',
    'طويله':  'twila',
    'طويل': 'twil',
    'الفرقة': 'ferka',
    'المودرن': 'moderna',
    'للاعبين': 'lel_laabin',
    'أول': 'awel',
    'رسمي': 'rasmi',
    'حركة': 'haraka',
    'حركه': 'haraka', 
    'رياضية': 'riyadhiya',
    'الشباب': 'chabeb',
    'حول': 'hawel',
    'تاريخ': 'tarikh',
    'آخر': 'akher',
    'العلمية': 'ilmiya',
    'علمية': 'ilmiya',
    'علميه': 'ilmiya',
    'موعدنا': 'mawidna',
    'جمهور': 'jomhour',
    'الحبيب': 'hbib',
    'نغني': 'nghanni',
    'الموسم': 'mawsem',
    'تخفيض': 'takhfidh',
    'فندق': 'fondok',
    'موقع': 'mawkaa',
    'خدمات': 'khadamet',
    'مسابقة': 'mosabka',
    'مسابقه': 'mosabka',
    'جمال': 'jamel',
    'فوج': 'fawj',
    'رياضية': 'riyadhiya',
    'رياضيه': 'riyadhiya',
    'التونسية': 'tounsiya',
    'التونسيه': 'tounsiya',
    'جهة': 'jiha',
    'قلب': 'kalb',
    'أجواء': 'ajwaa',
    'العيد': 'eid',
    'كبار': 'kbar',
    'تفاصيل': 'tafasil',
    'ناجح': 'najeh',
    'المسؤول': 'masoul',
    'المسءول': 'masoul',
    'النقل': 'nakl',
    'معاناة': 'mouanet',
    'المسافرين': 'msafrin',
    'غياب': 'ghyab',
    'رحلات': 'rahlat',
    'موش': 'mouch',
    'قد': 'ked',
    'في': 'fi',
    'و': 'w',
    'ما': 'ma',
    'هي': 'hiya',
    'هو': 'houwa',
    'كان': 'ken',
    'كانت': 'kenet',
    'فيه': 'fih',
    'فيها': 'fiha',
    'عليه': 'alih',
    'عليها':  'aliha',
    'منه': 'menou',
    'منها': 'menha',
    'إلى': 'lel',
    'مع': 'maa',
    'بعد': 'baad',
    'قبل': 'kabl',
    'بين': 'bin',
    'كل': 'kol',
    'بعض': 'baadh',
    'هذا': 'hadha',
    'هذه': 'hedhi',
    'ذلك': 'dhalik',
    'هنا': 'hne',
    'هناك':  'ghadika',
    'الذي': 'eli',
    'التي': 'eli',
    'اللي': 'eli',
    'و': 'w',
    'موكنين': 'moknin',
    'بسبب': 'bisebab',
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

# ============================================
# PROTECTION DES NOMBRES ET FORMATS SPÉCIAUX
# ============================================

import re

# Variable globale pour stocker les patterns protégés
_protected_values = {}
_protection_counter = 0

# Mois en arabe et français pour la protection
MONTHS_ARABIC = [
    'يناير', 'جانفي', 'جانفييه',     # Janvier
    'فبراير', 'فيفري',               # Février
    'مارس',                          # Mars
    'أبريل', 'افريل',                # Avril
    'ماي', 'مايو',                   # Mai
    'يونيو', 'جوان',                 # Juin
    'يوليو', 'جويلية',               # Juillet
    'أغسطس', 'اوت',                  # Août
    'سبتمبر', 'سبتامبر',             # Septembre
    'أكتوبر', 'اكتوبر',              # Octobre
    'نوفمبر', 'نوفامبر',             # Novembre
    'ديسمبر', 'ديسامبر',             # Décembre
]

MONTHS_FRENCH = [
    'janvier', 'fevrier', 'février', 'mars', 'avril', 'mai', 'juin',
    'juillet', 'aout', 'août', 'septembre', 'octobre', 'novembre', 'decembre', 'décembre'
]

def extract_protected_patterns(text):
    """
    Extrait et protège les patterns spéciaux (temps, dates, nombres).
    """
    global _protected_values, _protection_counter
    _protected_values = {}
    _protection_counter = 0
    
    result_text = text
    
   # 1. Protéger les PLAGES de dates avec mois en arabe (ex: 2 و3 ماي 2025, 30 أكتوبر لـ1 نوفمبر)
    for month in MONTHS_ARABIC:
        # Pattern:  nombre + و/- + nombre + mois + année optionnelle
        # Ex: 2 و3 ماي 2025 ou 2-3 ماي 2025
        pattern = rf'\b(\d{{1,2}})\s*[وو\-]\s*(\d{{1,2}})\s+{month}(\s+\d{{4}})?\b'
        matches = list(re.finditer(pattern, result_text))
        for match in reversed(matches):
            original_value = match.group()
            placeholder = f"PROT{_protection_counter}PROT"
            _protected_values[placeholder] = original_value
            _protected_values[placeholder.lower()] = original_value
            result_text = result_text[: match.start()] + placeholder + result_text[match.end():]
            _protection_counter += 1
    
    # 2. Protéger les dates simples avec mois en arabe (ex: 30 أكتوبر, 1 نوفمبر)
    for month in MONTHS_ARABIC:
        # Pattern: nombre + espace + mois + année optionnelle
        pattern = rf'\b(\d{{1,2}})\s+{month}(\s+\d{{4}})?\b'
        matches = list(re.finditer(pattern, result_text))
        for match in reversed(matches):
            # Vérifier que ce n'est pas déjà protégé
            if 'PROT' in result_text[max(0, match.start()-10):match.end()+10]:
                continue
            original_value = match.group()
            placeholder = f"PROT{_protection_counter}PROT"
            _protected_values[placeholder] = original_value
            _protected_values[placeholder.lower()] = original_value
            result_text = result_text[:match.start()] + placeholder + result_text[match.end():]
            _protection_counter += 1
    
      # 3. Protéger les plages de dates avec mois en français
    for month in MONTHS_FRENCH:
        pattern = rf'\b(\d{{1,2}})\s*[et\-وو]\s*(\d{{1,2}})\s+{month}(\s+\d{{4}})?\b'
        matches = list(re.finditer(pattern, result_text, re.IGNORECASE))
        for match in reversed(matches):
            original_value = match.group()
            placeholder = f"PROT{_protection_counter}PROT"
            _protected_values[placeholder] = original_value
            _protected_values[placeholder.lower()] = original_value
            result_text = result_text[: match.start()] + placeholder + result_text[match.end():]
            _protection_counter += 1
    
    # 4. Protéger les dates simples avec mois en français
    for month in MONTHS_FRENCH:
        pattern = rf'\b(\d{{1,2}})\s+{month}(\s+\d{{4}})?\b'
        matches = list(re.finditer(pattern, result_text, re.IGNORECASE))
        for match in reversed(matches):
            if 'PROT' in result_text[max(0, match.start()-10):match.end()+10]:
                continue
            original_value = match.group()
            placeholder = f"PROT{_protection_counter}PROT"
            _protected_values[placeholder] = original_value
            _protected_values[placeholder.lower()] = original_value
            result_text = result_text[:match.start()] + placeholder + result_text[match.end():]
            _protection_counter += 1
    
    # 5. Protéger les plages de dates entre deux mois (ex: 30 أكتوبر لـ1 نوفمبر)
    for month1 in MONTHS_ARABIC: 
        for month2 in MONTHS_ARABIC:
            pattern = rf'\b(\d{{1,2}})\s+{month1}\s+[لِـل]+\s*(\d{{1,2}})\s+{month2}\b'
            matches = list(re. finditer(pattern, result_text))
            for match in reversed(matches):
                if 'PROT' in result_text[max(0, match.start()-10):match.end()+10]:
                    continue
                original_value = match. group()
                placeholder = f"PROT{_protection_counter}PROT"
                _protected_values[placeholder] = original_value
                _protected_values[placeholder.lower()] = original_value
                result_text = result_text[:match.start()] + placeholder + result_text[match.end():]
                _protection_counter += 1
    
    # 3. Patterns numériques classiques
    patterns = [
        (r'\b\d{1,2}:\d{2}\b', 'time'),              # 18:30, 9:00
        (r'\b\d{1,2}h\d{2}\b', 'time'),              # 14h30
        (r'\b\d{1,2}[/\-\. ]\d{1,2}[/\-\. ]\d{2,4}\b', 'date'),  # 25/12/2024
        (r'\b\d{1,2}[/\-\.]\d{1,2}\b', 'date'),      # 25/12
        (r'\b(19|20)\d{2}\b', 'year'),               # 1990, 2024
        (r'\b\d+%', 'percentage'),                   # 50%, 100%
        (r'\b\d+(\.\d+)?\s*(dt|tnd|دينار)\b', 'price'),  # 50dt
        (r'\b\d+\s*(dt|tnd|دينار)\b', 'price'),     # 50 dt
    ]
    
    for pattern, pattern_type in patterns:
        matches = list(re.finditer(pattern, result_text, re. IGNORECASE))
        for match in reversed(matches):
            # Vérifier que ce n'est pas déjà un placeholder
            if 'PROT' in match.group():
                continue
            original_value = match.group()
            placeholder = f"PROT{_protection_counter}PROT"
            _protected_values[placeholder] = original_value
            _protected_values[placeholder.lower()] = original_value
            result_text = result_text[:match.start()] + placeholder + result_text[match.end():]
            _protection_counter += 1
    
    return result_text


def restore_protected_patterns(text):
    """
    Restaure les patterns protégés après la conversion.
    """
    global _protected_values
    
    result = text
    
    # Restaurer tous les placeholders (en minuscule car le texte est converti en minuscule)
    for placeholder, original in _protected_values.items():
        result = result.replace(placeholder, original)
        result = result.replace(placeholder.lower(), original)
    
    return result


def convert_arabic_dates_to_latin(text):
    """
    Convertit les dates avec mois arabes vers le format latin.
    Ex: 2 و3 ماي 2025 -> 2 w 3 mai 2025
        30 أكتوبر -> 30 octobre
    """
    month_mapping = {
        'يناير': 'janvier', 'جانفي': 'janvier', 'جانفييه': 'janvier',
        'فبراير':  'fevrier', 'فيفري': 'fevrier',
        'مارس': 'mars',
        'أبريل':  'avril', 'افريل': 'avril',
        'ماي': 'mai', 'مايو': 'mai',
        'يونيو': 'juin', 'جوان': 'juin',
        'يوليو': 'juillet', 'جويلية': 'juillet',
        'أغسطس': 'aout', 'اوت': 'aout',
        'سبتمبر': 'septembre', 'سبتامبر': 'septembre',
        'أكتوبر': 'octobre', 'اكتوبر': 'octobre',
        'نوفمبر': 'novembre', 'نوفامبر': 'novembre',
        'ديسمبر': 'decembre', 'ديسامبر': 'decembre',
    }
    
    result = text
    
    # Convertir les mois
    for arabic, latin in month_mapping.items():
        result = result.replace(arabic, latin)
    
    # Convertir و en w (pour les dates)
    # Pattern: chiffre + و + chiffre
    result = re.sub(r'(\d)\s*و\s*(\d)', r'\1 w \2', result)
    
    # Convertir لـ/ل en "lel" (pour les plages)
    result = re.sub(r'\s*[لِـل]+\s*', ' lel ', result)
    
    return result
# ============================================
# GESTION DES PRÉFIXES ARABES
# ============================================

# Préfixes arabes courants (ordre important - du plus long au plus court)
ARABIC_PREFIXES = [
    'وال',    # w + al (et le/la)
    'بال',    # b + al (avec le/la)
    'لل',     # l + al (pour le/la)
    'فال',    # f + al (alors le/la)
    'كال',    # k + al (comme le/la)
    'وب',     # w + b (et avec)
    'ول',     # w + l (et pour)
    'ال',     # al (le/la)
    'و',      # w (et)
    'ب',      # b (avec)
    'ل',      # l (pour)
    'ف',      # f (alors)
    'ك',      # k (comme)
]

# Traduction des préfixes en Darija latin
PREFIX_TO_DARIJA = {
    'وال': 'wel_',
    'بال': 'bel_',
    'لل': 'lel_',
    'فال': 'fel_',
    'كال':  'kel_',
    'وب': 'w_b',
    'ول': 'w_l',
    'ال': '',        # Article défini - souvent omis en darija
    'و': 'w_',
    'ب': 'b_',
    'ل': 'l_',
    'ف': 'f_',
    'ك':  'k_',
}


def separate_arabic_prefix(word):
    """
    Sépare le préfixe arabe du mot de base.
    
    Args:
        word:  Mot arabe potentiellement avec préfixe
    
    Returns:
        tuple: (préfixe_darija, mot_base) ou (None, mot_original)
    
    Exemples:
        والموسيقى -> ('w_', 'الموسيقى') -> ensuite 'الموسيقى' -> 'mousika'
        وحلو -> ('w_', 'حلو')
        الجو -> ('', 'جو')
    """
    for prefix in ARABIC_PREFIXES:
        if word.startswith(prefix) and len(word) > len(prefix):
            base_word = word[len(prefix):]
            darija_prefix = PREFIX_TO_DARIJA.get(prefix, '')
            
            # Cas spécial: si le préfixe est 'ال' et le mot de base commence par une lettre solaire
            # on garde le mot tel quel pour le chercher dans le dictionnaire
            if prefix == 'ال': 
                # Vérifier si le mot avec 'ال' est dans le dictionnaire
                if word in ARABIC_WORDS_TO_DARIJA_LATIN: 
                    return (None, word)
                # Sinon retourner le mot sans 'ال'
                return ('', base_word)
            
            return (darija_prefix, base_word)
    
    return (None, word)


def transliterate_arabic_to_latin(text):
    """
    Convertit le texte arabe en caractères latins (Darija).
    Gère les préfixes arabes attachés aux mots.
    """
    words = text.split()
    result_words = []
    
    for word in words:
        # Extraire la ponctuation
        punctuation_before = ''
        punctuation_after = ''
        clean_word = word
        
        # Extraire ponctuation avant
        while clean_word and not (clean_word[0]. isalnum() or '\u0600' <= clean_word[0] <= '\u06FF'):
            punctuation_before += clean_word[0]
            clean_word = clean_word[1:]
        
        # Extraire ponctuation après
        while clean_word and not (clean_word[-1].isalnum() or '\u0600' <= clean_word[-1] <= '\u06FF'):
            punctuation_after = clean_word[-1] + punctuation_after
            clean_word = clean_word[:-1]
        
        if not clean_word:
            if punctuation_before or punctuation_after:
                result_words.append(punctuation_before + punctuation_after)
            continue
        
        # Vérifier si c'est un mot arabe
        if re.search(r'[\u0600-\u06FF]', clean_word):
            
            # 1. Chercher d'abord le mot complet dans le dictionnaire
            if clean_word in ARABIC_WORDS_TO_DARIJA_LATIN:
                transliterated = ARABIC_WORDS_TO_DARIJA_LATIN[clean_word]
                result_words.append(punctuation_before + transliterated + punctuation_after)
                continue
            
            # 2.  Essayer de séparer le préfixe
            prefix_darija, base_word = separate_arabic_prefix(clean_word)
            
            if prefix_darija is not None:
                # Chercher le mot de base dans le dictionnaire
                if base_word in ARABIC_WORDS_TO_DARIJA_LATIN:
                    transliterated = prefix_darija + ARABIC_WORDS_TO_DARIJA_LATIN[base_word]
                    # Nettoyer les underscores en trop
                    transliterated = transliterated.replace('_', ' ').strip()
                    transliterated = re.sub(r'\s+', ' ', transliterated)
                    result_words. append(punctuation_before + transliterated + punctuation_after)
                    continue
                
                # Essayer sans le 'ال' si présent
                if base_word. startswith('ال') or base_word.startswith('ال'):
                    base_without_al = base_word[2: ] if base_word.startswith('ال') else base_word[2:]
                    if base_without_al in ARABIC_WORDS_TO_DARIJA_LATIN:
                        transliterated = prefix_darija + ARABIC_WORDS_TO_DARIJA_LATIN[base_without_al]
                        transliterated = transliterated.replace('_', ' ').strip()
                        transliterated = re.sub(r'\s+', ' ', transliterated)
                        result_words.append(punctuation_before + transliterated + punctuation_after)
                        continue
            
            # 3. Translittération lettre par lettre en dernier recours
            transliterated = ''
            for char in clean_word:
                if char in ARABIC_TO_LATIN:
                    transliterated += ARABIC_TO_LATIN[char]
                else:
                    transliterated += char
            
            result_words.append(punctuation_before + transliterated + punctuation_after)
        
        else:
            # Mot non-arabe, garder tel quel
            result_words.append(word)
    
    return ' '. join(result_words)

def is_arabic_text(text):
    """
    Vérifie si le texte contient principalement des caractères arabes. 
    """
    arabic_chars = len(re.findall(r'[\u0600-\u06FF]', text))
    total_chars = len(re.findall(r'\w', text))
    
    if total_chars == 0:
        return False
    
    return arabic_chars / total_chars > 0.3  # Plus de 30% de caractères arabes

def normalize_to_darija(text):
    """
    Normalise le texte vers le Darija tunisien.
    """
    text_lower = text.lower()
    words = text_lower.split()
    normalized_words = []
    
    for word in words:
        clean_word = re.sub(r'[^\w\s]', '', word)
        punctuation = word[len(clean_word):] if len(word) > len(clean_word) else ''
        
        if not clean_word:
            continue
        
        # ÉTAPE 1: Convertir les chiffres Darija vers lettres
        converted_word = convert_darija_numbers_smart(clean_word)
        
        if converted_word in KEEP_AS_IS:
            normalized_words.append(converted_word + punctuation)
            continue
        
        # ÉTAPE 2: Vérifier Darija normalization
        if converted_word in DARIJA_NORMALIZATION:
            normalized_words.append(DARIJA_NORMALIZATION[converted_word] + punctuation)
            continue
        
        # ÉTAPE 3: Vérifier Français -> Darija
        if clean_word in FRENCH_TO_DARIJA:
            normalized_words.append(FRENCH_TO_DARIJA[clean_word] + punctuation)
            continue
            
        # ÉTAPE 4: Vérifier Arabe -> Darija (MODIFIÉ)
        if clean_word in ARABIC_WORDS_TO_DARIJA_LATIN:
            normalized_words.append(ARABIC_WORDS_TO_DARIJA_LATIN[clean_word] + punctuation)
            continue
        
        # ÉTAPE 5: Garder le mot converti
        normalized_words.append(converted_word + punctuation)
    
    return ' '.join(normalized_words)

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

def clean_special_characters(text):
    """
    Nettoie les caractères spéciaux (guillemets, apostrophes, tirets, etc.)
    Couvre TOUTES les variantes possibles d'apostrophes. 
    """
    if not text:
        return text
    
    # Liste exhaustive de toutes les apostrophes possibles
    apostrophes = [
        '\u0027',  # ' APOSTROPHE
        '\u2019',  # ' RIGHT SINGLE QUOTATION MARK
        '\u2018',  # ' LEFT SINGLE QUOTATION MARK
        '\u02BC',  # ʼ MODIFIER LETTER APOSTROPHE
        '\u02B9',  # ʹ MODIFIER LETTER PRIME
        '\u0060',  # ` GRAVE ACCENT
        '\u00B4',  # ´ ACUTE ACCENT
        '\u2032',  # ′ PRIME
        '\u2035',  # ‵ REVERSED PRIME
        '\uFF07',  # ＇ FULLWIDTH APOSTROPHE
        '\u02BB',  # ʻ MODIFIER LETTER TURNED COMMA
        '\u02CA',  # ˊ MODIFIER LETTER ACUTE ACCENT
        '\u02CB',  # ˋ MODIFIER LETTER GRAVE ACCENT
    ]
    
    # Remplacer toutes les apostrophes par l'apostrophe standard
    for apos in apostrophes:
        text = text.replace(apos, "'")
    
    # Autres remplacements
    replacements = {
        # Guillemets
        '«':  '',
        '»': '',
        '"': '',
        '"':  '',
        '„': '',
        '"': '',
        
        # Tirets
        '—': '-',
        '–': '-',
        '−': '-',
        
        # Espaces spéciaux
        '\u00a0': ' ',  # Non-breaking space
        '\u200b': '',   # Zero-width space
        '\u200c': '',   # Zero-width non-joiner
        '\u200d': '',   # Zero-width joiner
        '\ufeff': '',   # BOM
        
        # Autres
        '…': '...',
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    return text


def clean_punctuation(text):
    """
    Nettoie la ponctuation du texte. 
    Options: 
    - Supprimer toute la ponctuation
    - OU garder seulement certains caractères utiles
    """
    if not text:
        return text
    
    # Option 1: Supprimer TOUTE la ponctuation
    # Garder seulement:  lettres, chiffres, espaces
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # Nettoyer les espaces multiples
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text
# ============================================
# GESTION DES CONTRACTIONS FRANÇAISES
# ============================================
def expand_french_contractions(text):
    """
    Traite les contractions françaises (mots avec apostrophe).
    
    Étape 1: Remplace les expressions complètes (d'électricité → dhaw)
    Étape 2: Sépare les contractions restantes (l'eau → l eau)
    """
    result = text
    
    # 1. Expressions complètes avec contractions → traduction directe
    full_expressions = {
        # Électricité / Services
        "d'électricité": "dhaw",
        "d'electricité": "dhaw",
        "d'electricite": "dhaw",
        "d'internet": "internet",
        "d'eau": "ma",
        
        # Lieux avec article
        "l'eau": "el ma",
        "l'école": "el madrsa",
        "l'hôpital": "el sbitar",
        "l'aéroport": "el matar",
        "l'hôtel": "el hotel",
        "l'université": "el fac",
        "l'église": "el knisa",
        "l'entrée": "el dkhoul",
        "l'événement": "el event",
        
        # Expressions courantes
        "aujourd'hui": "lyoum",
        "d'accord": "mwefek",
        "quelqu'un": "wahed",
        "quelqu'une": "wahda",
        "c'est-à-dire": "yaani",
        "n'est-ce pas": "mouch keka",
        "s'il vous plaît": "aychek",
        "s'il te plaît": "aychek",
        
        # C'est / C'était
        "c'est": "howa",
        "c'était": "ken",
    }
    
    for expression, replacement in full_expressions. items():
        pattern = re.compile(re.escape(expression), re.IGNORECASE)
        result = pattern. sub(replacement, result)
    
    # 2. Contractions restantes → séparer en deux mots
    simple_contractions = [
        ("d'", "de "),
        ("l'", "el "),
        ("j'", "ena "),
        ("m'", "m "),
        ("t'", "t "),
        ("s'", "s "),
        ("n'", "n "),
        ("qu'", "qu "),
    ]
    
    for contraction, expansion in simple_contractions:
        result = re. sub(re.escape(contraction), expansion, result, flags=re.IGNORECASE)
    
    return result

def normalize_text(text):
    """Pipeline de normalisation complète vers Darija Latin."""
    if not text:
        return text
    
    # 1. Supprimer les emojis
    text = remove_emojis(text)
    
    # 2. Nettoyer les caractères spéciaux (guillemets, apostrophes)
    text = clean_special_characters(text)
    
    # 3. Protéger les nombres, heures, dates
    text = extract_protected_patterns(text)
    
    # 4. Traiter les contractions françaises
    text = expand_french_contractions(text)
    
    # 5. Translittérer l'arabe vers le latin
    if is_arabic_text(text):
        text = transliterate_arabic_to_latin(text)
    
    # 6. Normaliser les caractères arabes
    text = normalize_arabic_chars(text)
    
    # 7. Convertir vers Darija normalisé
    text = normalize_to_darija(text)
    
    # 8. Restaurer les patterns protégés
    text = restore_protected_patterns(text)
    
    # 9. Convertir les dates arabes en latin (si la fonction existe)
    if 'convert_arabic_dates_to_latin' in dir():
        text = convert_arabic_dates_to_latin(text)
    
    # 10. NOUVEAU: Nettoyer la ponctuation
    text = clean_punctuation(text)
    
    # 11. Nettoyer espaces finaux
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
    
    # NOUVEAU:  Nettoyer les caractères spéciaux dès le début
    text = clean_special_characters(text)
    
    # Étape 1: Extraire les emojis ET leur sentiment
    emoji_data = extract_emoji_sentiment(text)
    
    # Étape 2: Détecter la langue originale
    original_lang = detect_language(text)
    
    # Étape 3: Normaliser vers Darija
    clean_text = normalize_text(text)
    
    # Créer le post enrichi
    processed_post = post.copy()
    processed_post. update({
        'original_text': post.get('text', ''),  # Garder l'original non modifié
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


        # ============================================

    
    print("=" * 70)
    print("🔍 DIAGNOSTIC - Problème d'électricité")
    print("=" * 70)
    
    # Texte de test
    test_text = "Coupures d'électricité, ce dimanche, à Monastir"
    
    # 1. Vérifier le type d'apostrophe
    print("\n1️⃣ ANALYSE DES CARACTÈRES :")
    print(f"   Texte: {test_text}")
    for i, char in enumerate(test_text):
        code = ord(char)
        if code > 127 or char in ["'", "'", "'", "ʼ", "´", "`", "'"]:
            print(f"   Position {i}: '{char}' → Unicode: U+{code:04X} ({code})")
    
    # 2. Vérifier si clean_special_characters existe
    print("\n2️⃣ VÉRIFICATION DES FONCTIONS :")
    functions_to_check = [
        'clean_special_characters',
        'expand_french_contractions', 
        'normalize_text',
        'normalize_to_darija'
    ]
    for func_name in functions_to_check:
        exists = func_name in dir()
        print(f"   {func_name}: {'✅ Existe' if exists else '❌ MANQUANTE'}")
    
    # 3. Vérifier le dictionnaire
    print("\n3️⃣ VÉRIFICATION DU DICTIONNAIRE FRENCH_TO_DARIJA :")
    words_to_check = ['électricité', 'electricite', 'coupure', 'coupures', 'dimanche']
    for word in words_to_check:
        exists = word in FRENCH_TO_DARIJA
        value = FRENCH_TO_DARIJA. get(word, 'NON TROUVÉ')
        print(f"   '{word}': {'✅' if exists else '❌'} → {value}")
    
    # 4. Test étape par étape
    print("\n4️⃣ TEST ÉTAPE PAR ÉTAPE :")
    
    text = test_text
    print(f"   Original: {text}")
    
    # Étape:  clean_special_characters
    if 'clean_special_characters' in dir():
        text = clean_special_characters(text)
        print(f"   Après clean_special_characters: {text}")
    else:
        print("   ❌ clean_special_characters N'EXISTE PAS!")
    
    # Étape: expand_french_contractions  
    if 'expand_french_contractions' in dir():
        text = expand_french_contractions(text)
        print(f"   Après expand_french_contractions: {text}")
    else:
        print("   ❌ expand_french_contractions N'EXISTE PAS!")
    
    # Étape: normalize_to_darija
    text_lower = text.lower()
    print(f"   Après lowercase: {text_lower}")
    
    text = normalize_to_darija(text_lower)
    print(f"   Après normalize_to_darija: {text}")
    
    # 5. Test final
    print("\n5️⃣ TEST FINAL normalize_text() :")
    final_result = normalize_text(test_text)
    print(f"   Input:   {test_text}")
    print(f"   Output: {final_result}")
    
    print("\n" + "=" * 70)