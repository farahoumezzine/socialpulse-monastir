"""
SocialPulse Monastir - Script d'Entraînement
=============================================
Entraîne le modèle de sentiment analysis sur le dataset labellisé. 

Auteur: Farah Oumezzine
Date: 2025
"""

import json
import os
import sys
import random
from model import SentimentModel, evaluate_model, print_evaluation_report


def load_training_data(filepath):
    """
    Charge le dataset d'entraînement.
    """
    print(f"📂 Chargement des données:  {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    texts = [item['text'] for item in data]
    labels = [item['label'] for item in data]
    
    print(f"✅ {len(texts)} échantillons chargés")
    
    return texts, labels


def split_data(texts, labels, test_ratio=0.2, random_seed=42):
    """
    Divise les données en ensembles d'entraînement et de test.
    """
    random.seed(random_seed)
    
    # Créer des indices et mélanger
    indices = list(range(len(texts)))
    random.shuffle(indices)
    
    # Diviser
    split_point = int(len(indices) * (1 - test_ratio))
    train_indices = indices[:split_point]
    test_indices = indices[split_point:]
    
    X_train = [texts[i] for i in train_indices]
    y_train = [labels[i] for i in train_indices]
    X_test = [texts[i] for i in test_indices]
    y_test = [labels[i] for i in test_indices]
    
    return X_train, X_test, y_train, y_test


def train_and_evaluate(training_file, model_output_path, model_type='naive_bayes'):
    """
    Pipeline complet d'entraînement et d'évaluation.
    """
    print("=" * 70)
    print("🚀 SOCIALPULSE MONASTIR - Entraînement du Modèle")
    print("=" * 70)
    
    # 1. Charger les données
    texts, labels = load_training_data(training_file)
    
    # Afficher la distribution
    from collections import Counter
    dist = Counter(labels)
    print(f"\n📊 Distribution des classes:")
    for cls, count in dist.items():
        emoji = {'positive': '✅', 'negative': '❌', 'neutral': '⚪'}.get(cls, '•')
        print(f"   {emoji} {cls}: {count} ({count/len(labels)*100:.1f}%)")
    
    # 2. Diviser les données
    print(f"\n📂 Division des données (80% train, 20% test)...")
    X_train, X_test, y_train, y_test = split_data(texts, labels, test_ratio=0.2)
    print(f"   • Entraînement: {len(X_train)} échantillons")
    print(f"   • Test: {len(X_test)} échantillons")
    
    # 3. Créer et entraîner le modèle
    model = SentimentModel(model_type=model_type, handle_imbalance=True)
    model.train(X_train, y_train)
    
    # 4. Évaluer
    print(f"\n📊 Évaluation sur l'ensemble de test...")
    metrics = evaluate_model(model, X_test, y_test)
    print_evaluation_report(metrics)
    
    # 5. Sauvegarder le modèle
    print(f"\n💾 Sauvegarde du modèle...")
    model.save(model_output_path)
    
    # 6. Test interactif
    print("\n" + "=" * 70)
    print("🧪 TEST INTERACTIF")
    print("=" * 70)
    
    test_sentences = [
        "jaw rawaa barcha hbel lyoum",
        "khayeb yesser el match taana",
        "ghodwa fama festival fi mestir",
        "mochkla kbira zahma barcha",
        "el bhar mezyen w jaw behi"
    ]
    
    print("\n📝 Exemples de prédictions:")
    for text in test_sentences:
        result = model.predict_with_confidence(text)
        emoji = {'positive': '✅', 'negative': '❌', 'neutral': '⚪'}.get(result['label'], '•')
        print(f"\n   📌 \"{text}\"")
        print(f"      {emoji} {result['label']} (confiance: {result['confidence']:.1%})")
    
    print("\n" + "=" * 70)
    print("✅ ENTRAÎNEMENT TERMINÉ!")
    print("=" * 70)
    
    return model, metrics


# ============================================
# MAIN
# ============================================

if __name__ == "__main__":
    # Chemins
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    training_file = os.path.join(project_root, 'data', 'processed', 'training_dataset.json')
    model_dir = os.path.join(project_root, 'models')
    
    # Créer le dossier models si nécessaire
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
    
    model_output = os.path.join(model_dir, 'sentiment_model.pkl')
    
    # Vérifier que le dataset existe
    if not os.path.exists(training_file):
        print(f"❌ Erreur: Fichier non trouvé: {training_file}")
        print("   → Exécutez d'abord:  python src/labeling.py")
        sys.exit(1)
    
    # Menu
    print("=" * 70)
    print("🤖 CHOIX DU MODÈLE")
    print("=" * 70)
    print("""
  1️⃣  Naive Bayes (rapide, bon pour débuter)
  2️⃣  Logistic Regression (plus précis)
    """)
    
    choice = input("Votre choix (1 ou 2): ").strip()
    
    if choice == "1":
        model_type = 'naive_bayes'
    elif choice == "2": 
        model_type = 'logistic_regression'
    else: 
        print("Choix invalide, utilisation de Naive Bayes par défaut.")
        model_type = 'naive_bayes'
    
    # Entraîner
    model, metrics = train_and_evaluate(training_file, model_output, model_type)