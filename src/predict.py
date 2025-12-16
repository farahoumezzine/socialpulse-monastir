"""
SocialPulse Monastir - Script de Prédiction
============================================
Utilise BERT ou Naive Bayes pour prédire le sentiment. 

"""

import os
import sys
import pickle

LABEL_EMOJI = {'positive':  '✅', 'negative':  '❌', 'neutral':  '⚪'}
ID_TO_LABEL = {0: 'negative', 1: 'neutral', 2: 'positive'}

def load_bert_model(checkpoint_path):
    """Charge le modèle BERT depuis un checkpoint."""
    import torch
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    
    # Charger le tokenizer depuis le modèle ORIGINAL (pas le checkpoint)
    tokenizer = AutoTokenizer.from_pretrained('CAMeL-Lab/bert-base-arabic-camelbert-mix')
    
    # Charger le modèle depuis le CHECKPOINT
    model = AutoModelForSequenceClassification.from_pretrained(checkpoint_path)
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)
    model.eval()
    
    return {'model': model, 'tokenizer': tokenizer, 'device': device, 'type': 'bert'}


def load_sklearn_model(model_path):
    """Charge le modèle Naive Bayes / Logistic Regression."""
    with open(model_path, 'rb') as f:
        model_data = pickle. load(f)
    model_data['type'] = 'sklearn'
    return model_data


def predict_bert(model_data, text):
    """Prédiction avec BERT."""
    import torch
    
    model = model_data['model']
    tokenizer = model_data['tokenizer']
    device = model_data['device']
    
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
        probs = torch.nn. functional.softmax(outputs. logits, dim=-1)[0]
        pred_id = torch.argmax(probs).item()
        confidence = probs[pred_id].item()
    
    return {
        'label': ID_TO_LABEL[pred_id],
        'confidence': confidence,
        'probabilities': {
            'negative': probs[0].item(),
            'neutral': probs[1]. item(),
            'positive': probs[2].item(),
        }
    }


def predict_sklearn(model_data, text):
    """Prédiction avec Naive Bayes / Logistic Regression."""
    model = model_data['model']
    vectorizer = model_data['vectorizer']
    
    X = vectorizer.transform([text])
    prediction = model.predict(X)[0]
    
    try:
        proba = model. predict_proba(X)[0]
        classes = model.classes_
        probabilities = {cls: float(p) for cls, p in zip(classes, proba)}
        confidence = max(proba)
    except:
        probabilities = {}
        confidence = 0.5
    
    return {
        'label': prediction,
        'confidence': confidence,
        'probabilities': probabilities
    }


def predict(model_data, text):
    """Prédit selon le type de modèle."""
    if model_data['type'] == 'bert':
        return predict_bert(model_data, text)
    else:
        return predict_sklearn(model_data, text)


def main():
    # Chemins
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    bert_checkpoint = os.path.join(project_root, 'models', 'bert_checkpoints', 'checkpoint-48')
    sklearn_path = os.path.join(project_root, 'models', 'sentiment_model.pkl')
    
    # Menu de sélection
    print("=" * 60)
    print("SOCIALPULSE MONASTIR - Prediction de Sentiment")
    print("=" * 60)
    print("\nChoisissez le modele:")
    print("  1. BERT (CAMeLBERT) - 73.3% accuracy")
    print("  2. Naive Bayes/Logistic Regression - 45.5% accuracy")
    
    choice = input("\nVotre choix (1 ou 2): ").strip()
    
    # Charger le modèle
    print("\nChargement du modele...")
    
    try:
        if choice == '1':
            if os.path. exists(bert_checkpoint):
                model_data = load_bert_model(bert_checkpoint)
                print("Modele BERT charge!  (73.3% accuracy)")
            else:
                print("Checkpoint BERT non trouve!")
                print("Utilisation de Naive Bayes...")
                model_data = load_sklearn_model(sklearn_path)
        else:
            model_data = load_sklearn_model(sklearn_path)
            print("Modele Naive Bayes charge! (45.5% accuracy)")
    except Exception as e:
        print("Erreur lors du chargement:  " + str(e))
        print("\nUtilisation de Naive Bayes...")
        model_data = load_sklearn_model(sklearn_path)
    
    # Interface interactive
    print("\n" + "-" * 60)
    print("Entrez un texte en Darija.  Tapez 'quit' pour quitter.")
    print("-" * 60 + "\n")
    
    while True: 
        try: 
            text = input("Votre texte: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAu revoir!")
            break
        
        if text.lower() in ['quit', 'exit', 'q']: 
            print("\nAu revoir!")
            break
        
        if not text:
            continue
        
        # Prédire
        result = predict(model_data, text)
        emoji = LABEL_EMOJI.get(result['label'], '•')
        
        print("\n   " + emoji + " Sentiment:  " + result['label']. upper())
        print("   Confiance: " + str(round(result['confidence'] * 100, 1)) + "%")
        
        if result['probabilities']:
            print("   Probabilites:")
            for label in ['positive', 'neutral', 'negative']:
                if label in result['probabilities']: 
                    e = LABEL_EMOJI.get(label, '•')
                    p = result['probabilities'][label]
                    print("      " + e + " " + label + ": " + str(round(p * 100, 1)) + "%")
        print()


if __name__ == "__main__":
    main()