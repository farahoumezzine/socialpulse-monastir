"""
SocialPulse Monastir - Modèle Naive Bayes
=========================================
Entraînement d'un modèle Naive Bayes pour l'analyse de sentiment. 

"""

import os
import json
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# ============================================================
# CONFIGURATION
# ============================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_FILE = os.path.join(PROJECT_ROOT, 'data', 'processed', 'augmented_dataset.json')
MODEL_FILE = os.path. join(PROJECT_ROOT, 'models', 'sentiment_model. pkl')


def load_data():
    """Charge les données d'entraînement."""
    # Essayer le dataset augmenté d'abord
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        # Sinon, utiliser le dataset de base
        base_file = os.path.join(PROJECT_ROOT, 'data', 'processed', 'training_dataset.json')
        with open(base_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    
    texts = [item['text'] for item in data]
    labels = [item['label'] for item in data]
    
    return texts, labels


def train_model():
    """Entraîne le modèle Naive Bayes."""
    print("=" * 60)
    print("SOCIALPULSE - Entraînement Modèle Naive Bayes")
    print("=" * 60)
    
    # Charger les données
    print("\n📂 Chargement des données...")
    texts, labels = load_data()
    print("✅ " + str(len(texts)) + " échantillons chargés")
    
    # Compter par classe
    from collections import Counter
    counts = Counter(labels)
    print("   ✅ Positive: " + str(counts. get('positive', 0)))
    print("   ❌ Negative: " + str(counts.get('negative', 0)))
    print("   ⚪ Neutral:   " + str(counts.get('neutral', 0)))
    
    # Split train/test
    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )
    
    print("\n🔄 Vectorisation TF-IDF...")
    vectorizer = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),
        min_df=2
    )
    
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    
    print("✅ Vocabulaire:  " + str(len(vectorizer.vocabulary_)) + " mots")
    
    # Entraîner
    print("\n🔄 Entraînement Naive Bayes...")
    model = MultinomialNB(alpha=0.1)
    model.fit(X_train_vec, y_train)
    print("✅ Modèle entraîné!")
    
    # Évaluer
    print("\n📊 Évaluation...")
    y_pred = model. predict(X_test_vec)
    accuracy = accuracy_score(y_test, y_pred)
    
    print("\n" + "=" * 60)
    print("📊 RÉSULTATS")
    print("=" * 60)
    print("   Accuracy: " + str(round(accuracy * 100, 1)) + "%")
    print("\n" + classification_report(y_test, y_pred))
    
    # Sauvegarder
    print("\n💾 Sauvegarde du modèle...")
    
    # Créer le dossier models si nécessaire
    os.makedirs(os.path.dirname(MODEL_FILE), exist_ok=True)
    
    model_data = {
        'model': model,
        'vectorizer': vectorizer,
        'accuracy': accuracy
    }
    
    with open(MODEL_FILE, 'wb') as f:
        pickle. dump(model_data, f)
    
    print("✅ Modèle sauvegardé:  " + MODEL_FILE)
    
    return model, vectorizer, accuracy


if __name__ == "__main__": 
    train_model()