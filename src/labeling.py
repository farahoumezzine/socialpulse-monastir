"""
===========================================================
Ce module pré-labelle les posts en utilisant :
1. Sentiment des emojis (déjà extrait)
2. Mots-clés positifs/négatifs en Darija
3. Règles linguistiques


"""

import json
import os
import re
from collections import Counter

# ============================================
# 1. DICTIONNAIRES DE MOTS-CLÉS DARIJA
# ============================================

# Mots positifs en Darija tunisien
POSITIVE_WORDS = {
    # Expressions de joie/satisfaction
    'rawaa', 'hbel', 'heyel', 'momtez', 'behi', 'mezyen', 'bnin', 
    'farhan', 'farhana', 'mlih', 'temem', 'barcha behi', 'top',
    
    # Qualité positive
    'jmil', 'jmila', 'hlou', 'hlowa', 'zin', 'zwina', 'raia',
    
    # Succès/Réussite
    'rebeh', 'najeh', 'bravo', 'mabrouk', 'tahya', 'yaaychek',
    
    # Gratitude
    'chokr', 'saha', 'merci', 'baraka', 'hamdoullah',
    
    # Ambiance positive
    'jaw', 'ambiance', 'hafla', 'fete', 'festival', 'concert',
    
    # Amour/Affection
    'hob', 'nheb', 'nhebek', 'nhebkom', 'habibi', 'habibti',
    
    # Recommandation
    'nchourek', 'nemchiwlou', 'lazem', 'worth it', 'yestehel',
    
    # Autres positifs
    'behia', 'skhoun', 'nar', 'kwi', 'fort', 'super', 'extra',
}

# Mots négatifs en Darija tunisien
NEGATIVE_WORDS = {
    # Expressions de mécontentement
    'khayeb', 'khayba', 'fdhiha', 'kharba', 'mochkla', 'machakel',
    
    # Qualité négative
    'mouch behi', 'mouch mlih', 'dhaif', 'nkes', 'wahel',
    
    # Émotions négatives
    'hzin', 'hzina', 'zaalet', 'metghachech', 'taab', 'taaba',
    'mokref', 'yekref', 'kalekni',
    
    # Problèmes
    'panne', 'kass', 'kassat', 'taatlet', 'msakra', 'mahbous',
    'zahma', 'retard', 'takhir', 'ghyab',
    
    # Critique
    'skandal', 'aib', 'hchouma', 'karhba', 'fawdha',
    
    # Service mauvais
    'ikalek', 'mzaej', 'sot ali', 'bruit', 'sale', 'wsekh',
    
    # Déception
    'khab amli', 'makanch', 'mafamech', 'deception', 'dommage',
    
    # Autres négatifs  
    'ghali', 'yesrek', 'voleur', 'arnaque', 'nصab',
}

# Mots neutres/informatifs (pas de sentiment clair)
NEUTRAL_WORDS = {
    'lyoum', 'ghodwa', 'lbereh', 'tawa', 'wakteh', 'saa',
    'win', 'kifech', 'chkoun', 'chnowa', 'alech',
    'mestir', 'monastir', 'khniss', 'stade', 'corniche',
    'match', 'film', 'ardh', 'maaredh', 'nadwa',
}

# Intensificateurs (amplifient le sentiment)
INTENSIFIERS = {
    'barcha':  1.5,      # beaucoup
    'yesser': 1.5,      # très
    'aalekher': 1.8,    # au max
    'bel kol': 1.6,     # complètement
    'jaw': 1.3,         # ambiance (amplifie)
    'chwaya': 0.7,      # un peu (réduit)
    'mouch barcha': 0.6,  # pas beaucoup
}

# Négateurs (inversent le sentiment)
NEGATORS = {
    'mouch', 'mech', 'ma', 'mafamech', 'makanch', 
    'jamais', 'abadan', 'la', 'non', 'bla',
}


# ============================================
# 2. FONCTION DE SCORING AUTOMATIQUE
# ============================================

def calculate_text_sentiment_score(clean_text):
    """
    Calcule un score de sentiment basé sur les mots-clés. 
    
    Args:
        clean_text: Texte nettoyé en Darija latin
    
    Returns:
        dict: {
            'score': float (-1 à 1),
            'positive_words': list,
            'negative_words': list,
            'has_negator': bool,
            'intensifier': float
        }
    """
    if not clean_text:
        return {
            'score': 0,
            'positive_words':  [],
            'negative_words':  [],
            'has_negator': False,
            'intensifier': 1.0
        }
    
    words = clean_text.lower().split()
    
    # Trouver les mots positifs et négatifs
    found_positive = [w for w in words if w in POSITIVE_WORDS]
    found_negative = [w for w in words if w in NEGATIVE_WORDS]
    
    # Vérifier les négateurs
    has_negator = any(w in NEGATORS for w in words)
    
    # Calculer l'intensificateur moyen
    intensifier = 1.0
    for word in words:
        if word in INTENSIFIERS:
            intensifier *= INTENSIFIERS[word]
    
    # Calculer le score
    positive_count = len(found_positive)
    negative_count = len(found_negative)
    total_sentiment_words = positive_count + negative_count
    
    if total_sentiment_words == 0:
        score = 0
    else: 
        score = (positive_count - negative_count) / total_sentiment_words
    
    # Appliquer l'intensificateur
    score = score * intensifier
    
    # Inverser si négateur présent
    if has_negator and abs(score) > 0:
        score = -score * 0.8  # Inversion partielle
    
    # Normaliser entre -1 et 1
    score = max(-1, min(1, score))
    
    return {
        'score': round(score, 3),
        'positive_words':  found_positive,
        'negative_words': found_negative,
        'has_negator': has_negator,
        'intensifier': round(intensifier, 2)
    }


def calculate_emoji_sentiment_score(emoji_sentiment):
    """
    Extrait le score de sentiment des emojis.
    
    Args:
        emoji_sentiment:  Dict contenant les données emoji du preprocessing
    
    Returns:
        float: Score entre -1 et 1
    """
    if not emoji_sentiment or emoji_sentiment. get('emoji_count', 0) == 0:
        return 0
    
    return emoji_sentiment. get('avg_score', 0)


def combine_sentiment_scores(text_score, emoji_score, text_weight=0.6, emoji_weight=0.4):
    """
    Combine les scores de sentiment du texte et des emojis.
    
    Args:
        text_score: Score basé sur les mots-clés
        emoji_score: Score basé sur les emojis
        text_weight: Poids du score texte (défaut: 0.6)
        emoji_weight: Poids du score emoji (défaut: 0.4)
    
    Returns:
        float: Score combiné entre -1 et 1
    """
    # Si pas d'emojis, utiliser seulement le texte
    if emoji_score == 0:
        return text_score
    
    # Si pas de mots-clés sentiment, utiliser seulement les emojis
    if text_score == 0:
        return emoji_score
    
    # Combinaison pondérée
    combined = (text_score * text_weight) + (emoji_score * emoji_weight)
    
    return round(combined, 3)


def score_to_label(score, thresholds=None):
    """
    Convertit un score numérique en label catégoriel.
    
    Args:
        score: Score entre -1 et 1
        thresholds: Dict avec seuils personnalisés
    
    Returns:
        str: 'positive', 'negative', ou 'neutral'
    """
    if thresholds is None: 
        thresholds = {
            'positive': 0.2,   # score >= 0.2 → positif
            'negative': -0.2,  # score <= -0.2 → négatif
        }
    
    if score >= thresholds['positive']:
        return 'positive'
    elif score <= thresholds['negative']: 
        return 'negative'
    else:
        return 'neutral'


def calculate_confidence(text_analysis, emoji_sentiment, final_score):
    """
    Calcule un niveau de confiance pour le label attribué.
    
    Returns:
        float: Confiance entre 0 et 1
    """
    confidence = 0.5  # Base
    
    # Plus de mots-clés trouvés = plus de confiance
    sentiment_words = len(text_analysis['positive_words']) + len(text_analysis['negative_words'])
    if sentiment_words >= 3:
        confidence += 0.2
    elif sentiment_words >= 1:
        confidence += 0.1
    
    # Emojis présents = plus de confiance
    emoji_count = emoji_sentiment.get('emoji_count', 0) if emoji_sentiment else 0
    if emoji_count >= 2:
        confidence += 0.15
    elif emoji_count >= 1:
        confidence += 0.1
    
    # Score fort = plus de confiance
    if abs(final_score) >= 0.5:
        confidence += 0.15
    elif abs(final_score) >= 0.3:
        confidence += 0.1
    
    # Accord texte/emoji = plus de confiance
    text_score = text_analysis['score']
    emoji_score = calculate_emoji_sentiment_score(emoji_sentiment)
    if text_score != 0 and emoji_score != 0:
        if (text_score > 0 and emoji_score > 0) or (text_score < 0 and emoji_score < 0):
            confidence += 0.1  # Accord
        else:
            confidence -= 0.1  # Désaccord
    
    return round(min(1.0, max(0.0, confidence)), 2)


# ============================================
# 3. FONCTION PRINCIPALE DE LABELING
# ============================================

def label_post(post):
    """
    Labelle automatiquement un post avec son sentiment. 
    
    Args:
        post: Dict contenant 'clean_text' et 'emoji_sentiment'
    
    Returns:
        dict: Post enrichi avec le label de sentiment
    """
    clean_text = post. get('clean_text', '')
    emoji_sentiment = post.get('emoji_sentiment', {})
    
    # 1. Analyser le texte
    text_analysis = calculate_text_sentiment_score(clean_text)
    
    # 2. Obtenir le score emoji
    emoji_score = calculate_emoji_sentiment_score(emoji_sentiment)
    
    # 3. Combiner les scores
    final_score = combine_sentiment_scores(text_analysis['score'], emoji_score)
    
    # 4. Convertir en label
    label = score_to_label(final_score)
    
    # 5. Calculer la confiance
    confidence = calculate_confidence(text_analysis, emoji_sentiment, final_score)
    
    # 6. Enrichir le post
    labeled_post = post.copy()
    labeled_post['sentiment_analysis'] = {
        'label': label,
        'score': final_score,
        'confidence': confidence,
        'text_analysis': {
            'score': text_analysis['score'],
            'positive_words': text_analysis['positive_words'],
            'negative_words': text_analysis['negative_words'],
            'has_negator': text_analysis['has_negator'],
            'intensifier':  text_analysis['intensifier'],
        },
        'emoji_score': emoji_score,
        'needs_review': confidence < 0.6,  # Flag pour révision manuelle
    }
    
    return labeled_post


# ============================================
# 4. TRAITEMENT DU DATASET COMPLET
# ============================================

def label_dataset(input_path, output_path):
    """
    Labelle tout le dataset et sauvegarde les résultats.
    
    Args:
        input_path:  Chemin vers le fichier JSON preprocessé
        output_path:  Chemin vers le fichier de sortie labellisé
    """
    print("=" * 70)
    print("🏷️  SOCIALPULSE MONASTIR - Labeling Semi-Automatique")
    print("=" * 70)
    
    # Charger les données
    print(f"\n📂 Chargement des données depuis:  {input_path}")
    if not os.path.exists(input_path):
        print(f"❌ Erreur: Fichier non trouvé:  {input_path}")
        return None
    
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"✅ {len(data)} posts chargés")
    
    # Labeller chaque post
    print(f"\n🔄 Labeling en cours...")
    labeled_data = []
    
    stats = {
        'total':  len(data),
        'positive': 0,
        'negative': 0,
        'neutral': 0,
        'high_confidence': 0,
        'needs_review': 0,
    }
    
    for i, post in enumerate(data):
        labeled_post = label_post(post)
        labeled_data.append(labeled_post)
        
        # Mise à jour des stats
        label = labeled_post['sentiment_analysis']['label']
        stats[label] += 1
        
        confidence = labeled_post['sentiment_analysis']['confidence']
        if confidence >= 0.7:
            stats['high_confidence'] += 1
        if labeled_post['sentiment_analysis']['needs_review']: 
            stats['needs_review'] += 1
        
        # Progression
        if (i + 1) % 20 == 0:
            print(f"   Traité:  {i + 1}/{len(data)} posts")
    
    # Sauvegarder
    print(f"\n💾 Sauvegarde vers: {output_path}")
    
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path. exists(output_dir):
        os.makedirs(output_dir)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(labeled_data, f, ensure_ascii=False, indent=2)
    
    # Afficher les statistiques
    print("\n" + "=" * 70)
    print("📊 STATISTIQUES DE LABELING")
    print("=" * 70)
    
    print(f"\n📌 Total posts:  {stats['total']}")
    
    print(f"\n📊 Répartition des sentiments:")
    for sentiment in ['positive', 'negative', 'neutral']:
        count = stats[sentiment]
        pct = (count / stats['total']) * 100
        bar = "█" * int(pct / 2)
        emoji = {'positive': '✅', 'negative': '❌', 'neutral': '⚪'}[sentiment]
        print(f"   {emoji} {sentiment. capitalize():10}:  {count:4} ({pct: 5.1f}%) {bar}")
    
    print(f"\n🎯 Confiance:")
    print(f"   • Haute confiance (≥0.7): {stats['high_confidence']} ({stats['high_confidence']/stats['total']*100:.1f}%)")
    print(f"   • À réviser (<0.6):       {stats['needs_review']} ({stats['needs_review']/stats['total']*100:.1f}%)")
    
    # Exemples
    print("\n" + "=" * 70)
    print("📝 EXEMPLES DE LABELING")
    print("=" * 70)
    
    # Un exemple de chaque catégorie
    examples = {'positive': None, 'negative': None, 'neutral': None}
    for post in labeled_data:
        label = post['sentiment_analysis']['label']
        if examples[label] is None: 
            examples[label] = post
        if all(v is not None for v in examples. values()):
            break
    
    for sentiment, post in examples.items():
        if post: 
            print(f"\n{'─' * 70}")
            emoji = {'positive': '✅', 'negative': '❌', 'neutral': '⚪'}[sentiment]
            print(f"{emoji} {sentiment.upper()}")
            print(f"{'─' * 70}")
            print(f"📝 Texte: {post. get('clean_text', '')[:80]}...")
            sa = post['sentiment_analysis']
            print(f"📊 Score: {sa['score']} | Confiance: {sa['confidence']}")
            if sa['text_analysis']['positive_words']:
                print(f"   ✅ Mots positifs: {sa['text_analysis']['positive_words']}")
            if sa['text_analysis']['negative_words']:
                print(f"   ❌ Mots négatifs: {sa['text_analysis']['negative_words']}")
    
    print("\n" + "=" * 70)
    print("✅ LABELING TERMINÉ!")
    print("=" * 70)
    
    return labeled_data, stats


# ============================================
# 5. OUTILS DE RÉVISION MANUELLE
# ============================================

def get_posts_for_review(labeled_data, max_posts=50):
    """
    Récupère les posts qui nécessitent une révision manuelle.
    
    Args:
        labeled_data: Liste des posts labellisés
        max_posts: Nombre maximum de posts à réviser
    
    Returns: 
        list: Posts à réviser, triés par confiance croissante
    """
    needs_review = [
        post for post in labeled_data 
        if post['sentiment_analysis']['needs_review']
    ]
    
    # Trier par confiance croissante (les moins sûrs en premier)
    needs_review.sort(key=lambda x: x['sentiment_analysis']['confidence'])
    
    return needs_review[:max_posts]


def export_for_manual_review(labeled_data, output_path, max_posts=100):
    """
    Exporte les posts à réviser dans un format simple pour annotation manuelle.
    
    Args:
        labeled_data: Liste des posts labellisés
        output_path: Chemin du fichier de sortie
        max_posts: Nombre maximum de posts à exporter
    """
    posts_to_review = get_posts_for_review(labeled_data, max_posts)
    
    print(f"\n📝 Export de {len(posts_to_review)} posts pour révision manuelle...")
    
    # Format simplifié pour révision
    review_data = []
    for i, post in enumerate(posts_to_review):
        review_item = {
            'id': post. get('id', i),
            'original_text': post.get('original_text', post.get('text', '')),
            'clean_text': post.get('clean_text', ''),
            'auto_label': post['sentiment_analysis']['label'],
            'auto_score': post['sentiment_analysis']['score'],
            'confidence':  post['sentiment_analysis']['confidence'],
            'positive_words': post['sentiment_analysis']['text_analysis']['positive_words'],
            'negative_words':  post['sentiment_analysis']['text_analysis']['negative_words'],
            # Champ à remplir manuellement
            'manual_label': '',  # positive, negative, neutral
            'reviewer_notes': '',
        }
        review_data.append(review_item)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(review_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Fichier de révision exporté: {output_path}")
    print(f"   → Ouvrez ce fichier et remplissez 'manual_label' pour chaque post")
    
    return review_data


def merge_manual_labels(labeled_data, review_path):
    """
    Fusionne les labels manuels avec le dataset labellisé.
    
    Args:
        labeled_data:  Liste des posts labellisés automatiquement
        review_path:  Chemin vers le fichier avec les labels manuels
    
    Returns:
        list: Dataset avec labels corrigés
    """
    print(f"\n🔄 Fusion des labels manuels...")
    
    with open(review_path, 'r', encoding='utf-8') as f:
        reviewed = json.load(f)
    
    # Créer un mapping id -> manual_label
    manual_labels = {
        item['id']: item['manual_label']
        for item in reviewed
        if item. get('manual_label')  # Seulement si rempli
    }
    
    # Appliquer les corrections
    corrections = 0
    for post in labeled_data:
        post_id = post. get('id')
        if post_id in manual_labels:
            old_label = post['sentiment_analysis']['label']
            new_label = manual_labels[post_id]
            if old_label != new_label: 
                post['sentiment_analysis']['label'] = new_label
                post['sentiment_analysis']['manually_corrected'] = True
                post['sentiment_analysis']['original_auto_label'] = old_label
                corrections += 1
    
    print(f"✅ {corrections} labels corrigés manuellement")
    
    return labeled_data


# ============================================
# 6. GÉNÉRATION DU DATASET FINAL
# ============================================

def generate_training_dataset(labeled_data, output_path, min_confidence=0.5):
    """
    Génère le dataset final pour l'entraînement du modèle.
    
    Args:
        labeled_data:  Liste des posts labellisés
        output_path: Chemin de sortie
        min_confidence:  Confiance minimale pour inclure un post
    
    Returns:
        dict:  Statistiques du dataset généré
    """
    print("\n" + "=" * 70)
    print("📦 GÉNÉRATION DU DATASET D'ENTRAÎNEMENT")
    print("=" * 70)
    
    # Filtrer par confiance
    training_data = []
    for post in labeled_data:
        confidence = post['sentiment_analysis']['confidence']
        manually_corrected = post['sentiment_analysis']. get('manually_corrected', False)
        
        # Inclure si confiance suffisante OU corrigé manuellement
        if confidence >= min_confidence or manually_corrected:
            training_item = {
                'id': post.get('id'),
                'text': post.get('clean_text', ''),
                'label': post['sentiment_analysis']['label'],
                'confidence': confidence,
                'source': 'manual' if manually_corrected else 'auto',
            }
            training_data.append(training_item)
    
    # Statistiques
    stats = {
        'total': len(training_data),
        'positive': sum(1 for x in training_data if x['label'] == 'positive'),
        'negative': sum(1 for x in training_data if x['label'] == 'negative'),
        'neutral': sum(1 for x in training_data if x['label'] == 'neutral'),
        'from_manual': sum(1 for x in training_data if x['source'] == 'manual'),
        'from_auto': sum(1 for x in training_data if x['source'] == 'auto'),
    }
    
    # Sauvegarder
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(training_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Dataset d'entraînement généré: {output_path}")
    print(f"\n📊 Statistiques:")
    print(f"   • Total: {stats['total']} posts")
    print(f"   • Positif: {stats['positive']} ({stats['positive']/stats['total']*100:.1f}%)")
    print(f"   • Négatif: {stats['negative']} ({stats['negative']/stats['total']*100:.1f}%)")
    print(f"   • Neutre:  {stats['neutral']} ({stats['neutral']/stats['total']*100:.1f}%)")
    print(f"   • Labels auto:  {stats['from_auto']}")
    print(f"   • Labels manuels: {stats['from_manual']}")
    
    return training_data, stats




if __name__ == "__main__":
    import sys
    
    # Chemins
    script_dir = os. path.dirname(os.path. abspath(__file__))
    project_root = os.path. dirname(script_dir)
    
    # Fichiers
    input_file = os.path. join(project_root, 'data', 'processed', 'result_after_validation.json')
    labeled_file = os. path.join(project_root, 'data', 'processed', 'labeled_data.json')
    review_file = os. path.join(project_root, 'data', 'processed', 'posts_to_review.json')
    training_file = os.path.join(project_root, 'data', 'processed', 'training_dataset.json')
    
    # ══════════════════════════════════════════════════════════════
    # MENU INTERACTIF
    # ══════════════════════════════════════════════════════════════
    print("=" * 70)
    print("🏷️  SOCIALPULSE MONASTIR - Système de Labeling")
    print("=" * 70)
    print("""
Choisissez une option: 

  1️⃣  Labeling automatique (première fois)
      → Génère les labels automatiques et le fichier de révision
      
  2️⃣  Fusionner les labels manuels (après révision)
      → Fusionne vos corrections avec le dataset
      
  3️⃣  Générer le dataset d'entraînement
      → Crée le fichier final pour l'entraînement
    """)
    
    choice = input("Votre choix (1, 2, ou 3): ").strip()
    
    # ══════════════════════════════════════════════════════════════
    # OPTION 1: Labeling automatique (première fois)
    # ══════════════════════════════════════════════════════════════
    if choice == "1":
        print("\n⚠️  ATTENTION:  Ceci va écraser les fichiers existants!")
        confirm = input("Continuer? (oui/non): ").strip().lower()
        
        if confirm in ['oui', 'o', 'yes', 'y']:
            labeled_data, stats = label_dataset(input_file, labeled_file)
            if labeled_data: 
                export_for_manual_review(labeled_data, review_file, max_posts=50)
                print("\n✅ Labeling terminé!")
                print(f"📝 Maintenant, ouvrez et remplissez:  {review_file}")
                print("   Puis relancez avec l'option 2")
        else:
            print("❌ Annulé.")
    
    # ══════════════════════════════════════════════════════════════
    # OPTION 2: Fusionner les labels manuels
    # ══════════════════════════════════════════════════════════════
    elif choice == "2":
        print("\n" + "=" * 70)
        print("🔄 FUSION DES LABELS MANUELS")
        print("=" * 70)
        
        # Vérifier que les fichiers existent
        if not os.path.exists(labeled_file):
            print(f"❌ Erreur: Fichier non trouvé: {labeled_file}")
            print("   → Exécutez d'abord l'option 1")
            sys.exit(1)
        
        if not os.path.exists(review_file):
            print(f"❌ Erreur: Fichier non trouvé: {review_file}")
            print("   → Exécutez d'abord l'option 1")
            sys.exit(1)
        
        # Charger les données labellisées automatiquement
        print(f"\n📂 Chargement du dataset labellisé: {labeled_file}")
        with open(labeled_file, 'r', encoding='utf-8') as f:
            labeled_data = json.load(f)
        print(f"✅ {len(labeled_data)} posts chargés")
        
        # Afficher un aperçu du fichier de révision
        print(f"\n📂 Vérification du fichier de révision: {review_file}")
        with open(review_file, 'r', encoding='utf-8') as f:
            review_data = json.load(f)
        
        # Compter les labels manuels remplis
        filled_labels = [r for r in review_data if r. get('manual_label')]
        print(f"✅ {len(review_data)} posts à réviser")
        print(f"✏️  {len(filled_labels)} labels manuels remplis")
        
        if len(filled_labels) == 0:
            print("\n⚠️  ATTENTION: Aucun label manuel trouvé!")
            print(f"   → Ouvrez le fichier: {review_file}")
            print("   → Remplissez le champ 'manual_label' pour chaque post")
            print("   → Valeurs possibles: 'positive', 'negative', 'neutral'")
            print("\n📝 Exemple de ce qu'il faut faire:")
            print('''
    {
        "id": 5,
        "auto_label": "neutral",
        "manual_label": "",          ← CHANGEZ EN:  "positive" ou "negative" ou "neutral"
        ... 
    }
            ''')
            sys.exit(1)
        
        # Afficher les corrections à appliquer
        print("\n📋 Corrections à appliquer:")
        for item in filled_labels[: 5]:  # Afficher les 5 premiers
            print(f"   ID {item['id']}: {item['auto_label']} → {item['manual_label']}")
        if len(filled_labels) > 5:
            print(f"   ... et {len(filled_labels) - 5} autres")
        
        # Fusionner avec les labels manuels
        labeled_data = merge_manual_labels(labeled_data, review_file)
        
        # Sauvegarder le dataset corrigé
        print(f"\n💾 Sauvegarde du dataset corrigé: {labeled_file}")
        with open(labeled_file, 'w', encoding='utf-8') as f:
            json.dump(labeled_data, f, ensure_ascii=False, indent=2)
        
        # Statistiques
        print("\n✅ Fusion terminée!")
        print("   → Relancez avec l'option 3 pour générer le dataset d'entraînement")
    
    # ══════════════════════════════════════════════════════════════
    # OPTION 3: Générer le dataset d'entraînement
    # ══════════════════════════════════════════════════════════════
    elif choice == "3":
        print("\n" + "=" * 70)
        print("📦 GÉNÉRATION DU DATASET D'ENTRAÎNEMENT")
        print("=" * 70)
        
        # Vérifier que le fichier existe
        if not os.path.exists(labeled_file):
            print(f"❌ Erreur:  Fichier non trouvé:  {labeled_file}")
            print("   → Exécutez d'abord l'option 1")
            sys.exit(1)
        
        # Charger les données
        print(f"\n📂 Chargement du dataset labellisé: {labeled_file}")
        with open(labeled_file, 'r', encoding='utf-8') as f:
            labeled_data = json.load(f)
        print(f"✅ {len(labeled_data)} posts chargés")
        
        # Générer le dataset d'entraînement
        training_data, stats = generate_training_dataset(labeled_data, training_file, min_confidence=0.5)
        
        # Statistiques finales
        print("\n" + "=" * 70)
        print("📊 STATISTIQUES FINALES")
        print("=" * 70)
        
        manual_corrections = sum(
            1 for post in labeled_data 
            if post['sentiment_analysis']. get('manually_corrected', False)
        )
        
        print(f"\n✏️  Corrections manuelles:  {manual_corrections}")
        
        final_stats = {'positive': 0, 'negative':  0, 'neutral': 0}
        for post in labeled_data:
            label = post['sentiment_analysis']['label']
            final_stats[label] += 1
        
        print(f"\n📊 Répartition finale:")
        total = len(labeled_data)
        for sentiment in ['positive', 'negative', 'neutral']:
            count = final_stats[sentiment]
            pct = (count / total) * 100
            bar = "█" * int(pct / 2)
            emoji = {'positive': '✅', 'negative': '❌', 'neutral': '⚪'}[sentiment]
            print(f"   {emoji} {sentiment.capitalize():10}:  {count: 4} ({pct: 5.1f}%) {bar}")
        
        print("\n" + "=" * 70)
        print("✅ DATASET PRÊT POUR L'ENTRAÎNEMENT!")
        print("=" * 70)
        print(f"\n📁 Fichier généré: {training_file}")
        print("\n🚀 Prochaine étape: python src/train.py")
    
    else:
        print("❌ Option invalide.  Choisissez 1, 2, ou 3.")