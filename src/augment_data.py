"""
SocialPulse Monastir - Data Augmentation
=========================================
Augmente le dataset pour améliorer l'entraînement. 

Techniques utilisées:
1. Synonyme replacement (mots Darija)
2. Random insertion
3. Back-translation simulation

"""

import json
import os
import random
from collections import Counter

# ============================================
# DICTIONNAIRE DE SYNONYMES DARIJA
# ============================================

DARIJA_SYNONYMS = {
    # Positif
    'behi': ['mezyen', 'mlih', 'bnin', 'behia'],
    'mezyen': ['behi', 'mlih', 'bnin', 'behia'],
    'rawaa': ['hbel', 'khater', 'momtez', 'top'],
    'hbel':  ['rawaa', 'khater', 'momtez', 'extra'],
    'hlou': ['hlowa', 'zin', 'zwina', 'jmil'],
    'jmil': ['jmila', 'hlou', 'zin', 'raia'],
    'farhan': ['farhana', 'masrour', 'content'],
    
    # Négatif
    'khayeb': ['khayba', 'mouch behi', 'dhaif', 'nkes'],
    'mochkla': ['machakel', 'probleme', 'souci'],
    'taab': ['taaba', 'arhek', 'mrakh'],
    'hzin': ['hzina', 'maloul', 'mahzoun'],
    'fdhiha': ['kharba', 'skandal', 'wahla'],
    
    # Neutre / Commun
    'barcha': ['yesser', 'ktir', 'bzaf'],
    'lyoum': ['elyoum', 'nhar', 'nhara'],
    'ghodwa': ['bokra', 'ghodwa nhar'],
    'tawa': ['dork', 'hala', 'tawwa'],
    'fama': ['kayen', 'mawjoud'],
    'win': ['fein', 'wayn'],
    'kifech': ['ki', 'kif'],
    
    # Lieux Monastir
    'mestir': ['monastir', 'msatir'],
    'bhar': ['plage', 'bahar', 'mer'],
    'stade': ['mlaab', 'terrain'],
    
    # Actions
    'mcha': ['mchi', 'raw', 'roh'],
    'ja': ['ija', 'jat', 'jaw'],
    'chaf': ['ra', 'chouf'],
    'kla': ['akel', 'mekla'],
}

# Mots positifs pour insertion
POSITIVE_INSERTIONS = ['behi', 'mezyen', 'mlih', 'hamdoullah', 'inchallah']

# Mots négatifs pour insertion
NEGATIVE_INSERTIONS = ['mouch', 'bla', 'mafamech', 'khsara']

# Mots neutres pour insertion
NEUTRAL_INSERTIONS = ['zeda', 'kima', 'eli', 'w', 'fi']


# ============================================
# FONCTIONS D'AUGMENTATION
# ============================================

def synonym_replacement(text, n_replacements=2):
    """
    Remplace n mots par leurs synonymes. 
    """
    words = text.split()
    new_words = words. copy()
    
    # Trouver les mots qui ont des synonymes
    replaceable = [(i, w) for i, w in enumerate(words) if w in DARIJA_SYNONYMS]
    
    if not replaceable:
        return text
    
    # Remplacer aléatoirement
    random.shuffle(replaceable)
    for i, word in replaceable[: n_replacements]:
        synonyms = DARIJA_SYNONYMS[word]
        new_words[i] = random.choice(synonyms)
    
    return ' '.join(new_words)


def random_insertion(text, label, n_insertions=1):
    """
    Insère des mots aléatoires selon le sentiment.
    """
    words = text.split()
    
    # Choisir les mots à insérer selon le label
    if label == 'positive':
        insert_words = POSITIVE_INSERTIONS
    elif label == 'negative':
        insert_words = NEGATIVE_INSERTIONS
    else:
        insert_words = NEUTRAL_INSERTIONS
    
    for _ in range(n_insertions):
        word_to_insert = random.choice(insert_words)
        position = random.randint(0, len(words))
        words.insert(position, word_to_insert)
    
    return ' '.join(words)


def random_swap(text, n_swaps=1):
    """
    Échange la position de n paires de mots.
    """
    words = text.split()
    
    if len(words) < 2:
        return text
    
    new_words = words.copy()
    
    for _ in range(n_swaps):
        idx1, idx2 = random. sample(range(len(new_words)), 2)
        new_words[idx1], new_words[idx2] = new_words[idx2], new_words[idx1]
    
    return ' '.join(new_words)


def random_deletion(text, p=0.1):
    """
    Supprime chaque mot avec une probabilité p.
    """
    words = text.split()
    
    if len(words) <= 3:
        return text
    
    new_words = [w for w in words if random.random() > p]
    
    # Garder au moins 3 mots
    if len(new_words) < 3:
        return text
    
    return ' '.join(new_words)


def augment_text(text, label, n_augmentations=3):
    """
    Génère plusieurs versions augmentées d'un texte.
    """
    augmented = []
    
    for i in range(n_augmentations):
        # Choisir une technique aléatoire
        technique = random.choice(['synonym', 'insert', 'swap', 'delete', 'combined'])
        
        if technique == 'synonym':
            new_text = synonym_replacement(text, n_replacements=2)
        elif technique == 'insert': 
            new_text = random_insertion(text, label, n_insertions=1)
        elif technique == 'swap':
            new_text = random_swap(text, n_swaps=1)
        elif technique == 'delete':
            new_text = random_deletion(text, p=0.15)
        else:  # combined
            new_text = synonym_replacement(text, n_replacements=1)
            new_text = random_insertion(new_text, label, n_insertions=1)
        
        # Éviter les doublons
        if new_text != text and new_text not in augmented: 
            augmented.append(new_text)
    
    return augmented


# ============================================
# GÉNÉRATION DE DONNÉES SYNTHÉTIQUES
# ============================================

# Templates pour générer des posts synthétiques
TEMPLATES = {
    'positive': [
        "jaw {adj} fi {lieu} lyoum",
        "{lieu} {adj} barcha",
        "el {event} {adj} yesser",
        "nheb {lieu} barcha {adj}",
        "lyoum {adj} el jaw fi {lieu}",
        "{event} mtaa {lieu} {adj}",
        "machina {lieu} w kant {adj}",
        "el {food} {adj} barcha fi {lieu}",
        "ness {lieu} {adj} w chaleurs",
        "{lieu} welet {adj} barcha",
        "hamdoullah {lieu} {adj}",
        "barcha {adj} el {event}",
        "cheft {event} {adj} yesser",
        "{adj} barcha lyoum fi {lieu}",
        "el jaw {adj} wel ness {adj}",
    ],
    'negative': [
        "{problem} fi {lieu} lyoum",
        "el {lieu} fiha {problem}",
        "{problem} barcha fi {event}",
        "mouch {adj} el jaw fi {lieu}",
        "{lieu} {problem} kbira",
        "lyoum {problem} fi {lieu}",
        "el {event} fih {problem}",
        "machit {lieu} w lkit {problem}",
        "barcha {problem} fi {lieu}",
        "el {service} {problem} fi {lieu}",
        "khsara {lieu} fiha {problem}",
        "taab mel {problem} fi {lieu}",
        "{problem} kol nhar fi {lieu}",
        "moch normal el {problem}",
        "fdhiha el {service} fi {lieu}",
    ],
    'neutral': [
        "lyoum fama {event} fi {lieu}",
        "ghodwa {event} fi {lieu}",
        "{event} fi {lieu} nhar {jour}",
        "win {lieu} eli fiha {event}",
        "chkoun mchi {lieu} ghodwa",
        "fama {event} jdid fi {lieu}",
        "el {lieu} andha {event} lyoum",
        "{event} mtaa {lieu} yebda {time}",
        "ki temchi {lieu} chouf {event}",
        "el {jour} fama {event} fi {lieu}",
        "wakteh {event} fi {lieu}",
        "chkoun yaaref {lieu} win",
        "{event} fi {lieu} mta {time}",
        "nsit wakteh {event}",
        "fama {event} wala le",
    ]
}

# Vocabulaire pour les templates
VOCAB = {
    'adj': ['behi', 'mezyen', 'rawaa', 'hbel', 'hlou', 'jmil', 'bnin', 'mlih', 'khater', 'momtez'],
    'lieu': ['mestir', 'corniche', 'mdina', 'stade', 'plage', 'ribat', 'port', 'centre ville', 'souika', 'khniss'],
    'event': ['match', 'festival', 'concert', 'maaredh', 'hafla', 'film', 'ardh', 'mosabka', 'tournoi', 'fete'],
    'problem': ['mochkla', 'zahma', 'panne', 'khayeb', 'wsekh', 'ghali', 'takhir', 'bruit', 'kharba', 'fawdha'],
    'food': ['makla', 'pizza', 'kefteji', 'poisson', 'couscous', 'lablebi', 'fricasse'],
    'service': ['transport', 'internet', 'dhaw', 'ma', 'car', 'metro', 'bus', 'taxi'],
    'jour': ['el had', 'etnin', 'ethlatha', 'elarbaa', 'elkhmis', 'ejjomaa', 'essebt'],
    'time': ['9h', '10h', '14h', '18h', '20h', '21h', 'fel lil', 'fel sbah'],
}


def generate_synthetic_post(label):
    """
    Génère un post synthétique selon le label.
    """
    template = random.choice(TEMPLATES[label])
    
    # Remplir le template
    for key in VOCAB: 
        placeholder = '{' + key + '}'
        while placeholder in template:
            template = template.replace(placeholder, random.choice(VOCAB[key]), 1)
    
    return template


def generate_synthetic_dataset(n_per_class=20):
    """
    Génère un dataset synthétique équilibré.
    """
    synthetic_data = []
    
    for label in ['positive', 'negative', 'neutral']:
        for _ in range(n_per_class):
            text = generate_synthetic_post(label)
            synthetic_data.append({
                'text': text,
                'label': label,
                'source': 'synthetic'
            })
    
    return synthetic_data


# ============================================
# PIPELINE D'AUGMENTATION
# ============================================

def augment_dataset(input_path, output_path, target_per_class=50):
    """
    Augmente le dataset pour équilibrer les classes.
    """
    print("=" * 70)
    print("SOCIALPULSE MONASTIR - Data Augmentation")
    print("=" * 70)
    
    # Charger les données originales
    print("\n[1] Chargement:  " + input_path)
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("    " + str(len(data)) + " echantillons charges")
    
    # Compter les classes
    counter = Counter(item['label'] for item in data)
    print("\n[2] Distribution originale:")
    for label, count in counter.items():
        print("    - " + label + ":  " + str(count))
    
    # Séparer par classe
    by_class = {'positive': [], 'negative': [], 'neutral': []}
    for item in data:
        by_class[item['label']]. append(item)
    
    # Augmenter chaque classe
    augmented_data = []
    
    print("\n[3] Augmentation en cours...")
    
    for label in ['positive', 'negative', 'neutral']:
        original = by_class[label]
        current_count = len(original)
        
        print("\n    Classe '" + label + "':  " + str(current_count) + " -> " + str(target_per_class))
        
        # Ajouter les originaux
        for item in original: 
            augmented_data.append({
                'text': item['text'],
                'label': label,
                'source': 'original'
            })
        
        # Augmenter si nécessaire
        needed = target_per_class - current_count
        
        if needed > 0:
            augmented_count = 0
            
            # D'abord, augmenter les données existantes
            max_from_augmentation = current_count * 3
            while augmented_count < needed and augmented_count < max_from_augmentation:
                for item in original:
                    if augmented_count >= needed:
                        break
                    
                    aug_texts = augment_text(item['text'], label, n_augmentations=2)
                    for aug_text in aug_texts: 
                        if augmented_count >= needed:
                            break
                        augmented_data.append({
                            'text': aug_text,
                            'label': label,
                            'source': 'augmented'
                        })
                        augmented_count += 1
            
            # Si pas assez, générer des données synthétiques
            remaining = needed - augmented_count
            if remaining > 0:
                print("      + Generation de " + str(remaining) + " posts synthetiques")
                for _ in range(remaining):
                    text = generate_synthetic_post(label)
                    augmented_data.append({
                        'text': text,
                        'label': label,
                        'source': 'synthetic'
                    })
            
            print("      + " + str(needed) + " echantillons ajoutes")
        else:
            print("      (pas besoin d'augmentation)")
    
    # Mélanger
    random.shuffle(augmented_data)
    
    # Sauvegarder
    print("\n[4] Sauvegarde: " + output_path)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(augmented_data, f, ensure_ascii=False, indent=2)
    
    # Statistiques finales
    final_counter = Counter(item['label'] for item in augmented_data)
    source_counter = Counter(item['source'] for item in augmented_data)
    
    print("\n" + "=" * 70)
    print("RESULTATS")
    print("=" * 70)
    
    print("\n[+] Distribution finale:")
    for label in ['positive', 'negative', 'neutral']:
        count = final_counter[label]
        bar = "#" * (count // 2)
        print("    " + label + ": " + str(count) + " " + bar)
    
    print("\n[+] Sources des donnees:")
    for source, count in source_counter.items():
        print("    - " + source + ": " + str(count))
    
    print("\n[+] Total: " + str(len(augmented_data)) + " echantillons")
    
    print("\n" + "=" * 70)
    print("TERMINE!")
    print("=" * 70)
    
    return augmented_data


# ============================================
# MAIN
# ============================================

if __name__ == "__main__": 
    # Chemins
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    input_file = os.path.join(project_root, 'data', 'processed', 'training_dataset.json')
    output_file = os.path.join(project_root, 'data', 'processed', 'training_dataset_augmented.json')
    
    # Vérifier que le fichier existe
    if not os.path.exists(input_file):
        print("ERREUR:  Fichier non trouve:  " + input_file)
        print("Executez d'abord: python src/labeling. py")
        exit(1)
    
    # Augmenter
    augment_dataset(input_file, output_file, target_per_class=50)
    
    print("\nPROCHAINE ETAPE:")
    print("    python src/model_bert.py")