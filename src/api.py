"""
SocialPulse Monastir - API Flask
================================
API REST pour l'analyse de sentiment en Darija tunisien. 

Auteur: Farah Oumezzine
Date: 2025
"""

import os
import sys
import pickle
import torch
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# ============================================================
# CONFIGURATION
# ============================================================

# Chemins
SCRIPT_DIR = os. path.dirname(os.path. abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
STATIC_DIR = os.path. join(PROJECT_ROOT, 'static')

app = Flask(__name__, static_folder=STATIC_DIR)
CORS(app)

# Labels
LABEL_EMOJI = {'positive': '✅', 'negative': '❌', 'neutral': '⚪'}
ID_TO_LABEL = {0: 'negative', 1: 'neutral', 2: 'positive'}

# Variables globales pour les modèles
BERT_MODEL = None
SKLEARN_MODEL = None


# ============================================================
# CHARGEMENT DES MODÈLES
# ============================================================

def get_project_root():
    """Retourne le chemin racine du projet."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path. dirname(script_dir)


def load_bert_model():
    """Charge le modèle BERT."""
    global BERT_MODEL
    
    project_root = get_project_root()
    checkpoints_dir = os. path. join(project_root, 'models', 'bert_checkpoints')
    
    if os.path.exists(checkpoints_dir):
        checkpoints = [d for d in os.listdir(checkpoints_dir) if d.startswith('checkpoint-')]
        if checkpoints: 
            checkpoints.sort(key=lambda x: int(x. split('-')[1]))
            checkpoint_path = os.path.join(checkpoints_dir, checkpoints[-1])
            
            print("📥 Chargement BERT:  " + checkpoints[-1])
            
            tokenizer = AutoTokenizer.from_pretrained('CAMeL-Lab/bert-base-arabic-camelbert-mix')
            model = AutoModelForSequenceClassification.from_pretrained(checkpoint_path)
            device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            model.to(device)
            model.eval()
            
            BERT_MODEL = {
                'model': model,
                'tokenizer': tokenizer,
                'device': device
            }
            print("✅ BERT chargé!")
            return True
    
    print("⚠️ BERT non trouvé")
    return False


def load_sklearn_model():
    """Charge le modèle Naive Bayes."""
    global SKLEARN_MODEL
    
    project_root = get_project_root()
    model_path = os.path.join(project_root, 'models', 'sentiment_model.pkl')
    
    if os.path. exists(model_path):
        print("📥 Chargement Naive Bayes...")
        with open(model_path, 'rb') as f:
            SKLEARN_MODEL = pickle. load(f)
        print("✅ Naive Bayes chargé!")
        return True
    
    print("⚠️ Naive Bayes non trouvé")
    return False


# ============================================================
# FONCTIONS DE PRÉDICTION
# ============================================================

def predict_bert(text):
    """Prédiction avec BERT."""
    if BERT_MODEL is None:
        return None
    
    model = BERT_MODEL['model']
    tokenizer = BERT_MODEL['tokenizer']
    device = BERT_MODEL['device']
    
    encoding = tokenizer(
        text,
        truncation=True,
        padding='max_length',
        max_length=128,
        return_tensors='pt'
    )
    
    input_ids = encoding['input_ids'].to(device)
    attention_mask = encoding['attention_mask'].to(device)
    
    with torch.no_grad():
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        probs = torch.nn.functional.softmax(outputs. logits, dim=-1)[0]
        pred_id = torch.argmax(probs).item()
        confidence = probs[pred_id].item()
    
    return {
        'label': ID_TO_LABEL[pred_id],
        'confidence': round(confidence * 100, 1),
        'probabilities': {
            'positive':  round(probs[2].item() * 100, 1),
            'neutral': round(probs[1].item() * 100, 1),
            'negative': round(probs[0].item() * 100, 1)
        }
    }


def predict_sklearn(text):
    """Prédiction avec Naive Bayes."""
    if SKLEARN_MODEL is None: 
        return None
    
    model = SKLEARN_MODEL['model']
    vectorizer = SKLEARN_MODEL['vectorizer']
    
    X = vectorizer.transform([text])
    prediction = model.predict(X)[0]
    
    try:
        proba = model.predict_proba(X)[0]
        classes = model.classes_
        probabilities = {cls: round(float(p) * 100, 1) for cls, p in zip(classes, proba)}
        confidence = round(max(proba) * 100, 1)
    except:
        probabilities = {}
        confidence = 50.0
    
    return {
        'label': prediction,
        'confidence': confidence,
        'probabilities': probabilities
    }


# ============================================================
# ROUTES API
# ============================================================

@app.route('/')
def home():
    """Page d'accueil de l'API."""
    return jsonify({
        'name': 'SocialPulse Monastir API',
        'version': '1.0',
        'author': 'Farah Oumezzine',
        'description': 'API pour analyse de sentiment en Darija tunisien',
        'models': {
            'bert':  BERT_MODEL is not None,
            'sklearn': SKLEARN_MODEL is not None
        },
        'endpoints': {
            'GET /': 'Cette page',
            'GET /health': 'Status de l\'API',
            'GET /dashboard': 'Dashboard Web',
            'POST /predict':  'Prédire le sentiment d\'un texte',
            'POST /predict/batch': 'Prédire plusieurs textes',
            'GET /models':  'Liste des modèles disponibles'
        }
    })


@app.route('/health')
def health():
    """Vérifie le status de l'API."""
    return jsonify({
        'status':  'ok',
        'models': {
            'bert_loaded': BERT_MODEL is not None,
            'sklearn_loaded':  SKLEARN_MODEL is not None
        }
    })


@app.route('/models')
def models():
    """Liste les modèles disponibles."""
    return jsonify({
        'available_models': ['bert', 'sklearn'],
        'default': 'bert' if BERT_MODEL else 'sklearn',
        'bert':  {
            'loaded': BERT_MODEL is not None,
            'name': 'CAMeLBERT',
            'description': 'Modèle BERT pré-entraîné pour l\'arabe'
        },
        'sklearn': {
            'loaded': SKLEARN_MODEL is not None,
            'name': 'Naive Bayes / Logistic Regression',
            'description': 'Modèle classique ML'
        }
    })


@app.route('/predict', methods=['POST'])
def predict():
    """Prédit le sentiment d'un texte."""
    if not request.is_json:
        return jsonify({
            'success': False,
            'error': 'Content-Type doit être application/json'
        }), 400
    
    data = request.get_json()
    
    if 'text' not in data: 
        return jsonify({
            'success': False,
            'error': 'Le champ "text" est requis'
        }), 400
    
    text = data['text']. strip()
    
    if not text:
        return jsonify({
            'success': False,
            'error': 'Le texte ne peut pas être vide'
        }), 400
    
    model_choice = data.get('model', 'bert').lower()
    
    result = None
    model_used = None
    
    if model_choice == 'bert' and BERT_MODEL:
        result = predict_bert(text)
        model_used = 'bert'
    elif model_choice == 'sklearn' and SKLEARN_MODEL:
        result = predict_sklearn(text)
        model_used = 'sklearn'
    elif BERT_MODEL:
        result = predict_bert(text)
        model_used = 'bert'
    elif SKLEARN_MODEL:
        result = predict_sklearn(text)
        model_used = 'sklearn'
    
    if result is None:
        return jsonify({
            'success': False,
            'error':  'Aucun modèle disponible'
        }), 500
    
    return jsonify({
        'success': True,
        'text': text,
        'sentiment': result['label'],
        'confidence': result['confidence'],
        'emoji':  LABEL_EMOJI.get(result['label'], '•'),
        'probabilities': result['probabilities'],
        'model_used':  model_used
    })


@app.route('/predict/batch', methods=['POST'])
def predict_batch():
    """Prédit le sentiment de plusieurs textes."""
    if not request.is_json:
        return jsonify({
            'success': False,
            'error': 'Content-Type doit être application/json'
        }), 400
    
    data = request.get_json()
    
    if 'texts' not in data:
        return jsonify({
            'success': False,
            'error':  'Le champ "texts" est requis'
        }), 400
    
    texts = data['texts']
    
    if not isinstance(texts, list):
        return jsonify({
            'success': False,
            'error': '"texts" doit être une liste'
        }), 400
    
    if len(texts) == 0:
        return jsonify({
            'success': False,
            'error':  'La liste ne peut pas être vide'
        }), 400
    
    if len(texts) > 100:
        return jsonify({
            'success': False,
            'error':  'Maximum 100 textes par requête'
        }), 400
    
    model_choice = data.get('model', 'bert').lower()
    
    results = []
    summary = {'total': len(texts), 'positive': 0, 'negative': 0, 'neutral': 0}
    model_used = None
    
    for text in texts:
        if not text or not text.strip():
            continue
        
        text = text.strip()
        
        if model_choice == 'bert' and BERT_MODEL: 
            result = predict_bert(text)
            model_used = 'bert'
        elif SKLEARN_MODEL:
            result = predict_sklearn(text)
            model_used = 'sklearn'
        else:
            continue
        
        if result:
            results.append({
                'text': text,
                'sentiment':  result['label'],
                'confidence': result['confidence'],
                'emoji': LABEL_EMOJI. get(result['label'], '•'),
                'probabilities': result['probabilities']
            })
            
            if result['label'] in summary:
                summary[result['label']] += 1
    
    return jsonify({
        'success': True,
        'results': results,
        'summary': summary,
        'model_used': model_used
    })


# ============================================================
# ROUTES STATIC (Dashboard)
# ============================================================

@app.route('/dashboard')
def dashboard():
    """Sert le dashboard."""
    return send_from_directory(STATIC_DIR, 'index.html')


@app.route('/css/<path:filename>')
def serve_css(filename):
    """Sert les fichiers CSS."""
    return send_from_directory(os.path.join(STATIC_DIR, 'css'), filename)


@app.route('/js/<path:filename>')
def serve_js(filename):
    """Sert les fichiers JS."""
    return send_from_directory(os.path.join(STATIC_DIR, 'js'), filename)


# ============================================================
# DÉMARRAGE
# ============================================================

if __name__ == '__main__': 
    print("=" * 60)
    print("🚀 SOCIALPULSE MONASTIR - API")
    print("=" * 60)
    
    # Charger les modèles
    load_bert_model()
    load_sklearn_model()
    
    print("\n" + "-" * 60)
    print("📡 Démarrage du serveur...")
    print("   URL: http://localhost:5000")
    print("   Dashboard: http://localhost:5000/dashboard")
    print("-" * 60 + "\n")
    
    # Démarrer le serveur
    app.run(host='0.0.0.0', port=5000, debug=True)