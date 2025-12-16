"""
SocialPulse Monastir - Modèle BERT pour l'Arabe/Darija
======================================================
Utilise des modèles pré-entraînés (CAMeLBERT, AraBERT) pour 
une meilleure classification du sentiment. 

Auteur: Farah Oumezzine
Date: 2025
"""

import os
import json
import numpy as np
from collections import Counter

# ============================================
# INSTALLATION DES DÉPENDANCES
# ============================================
# Exécutez ces commandes avant d'utiliser ce fichier: 
#
# pip install transformers
# pip install torch
# pip install scikit-learn
# ============================================

try:
    import torch
    from torch. utils.data import Dataset, DataLoader
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    from transformers import TrainingArguments, Trainer
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, precision_recall_fscore_support
    BERT_AVAILABLE = True
except ImportError as e:
    BERT_AVAILABLE = False
    print(f"⚠️ Dépendances manquantes: {e}")
    print("   Installez avec: pip install transformers torch scikit-learn")


# ============================================
# CONFIGURATION DES MODÈLES
# ============================================

# Modèles disponibles pour l'arabe/dialectes
AVAILABLE_MODELS = {
    'camelbert-mix': {
        'name': 'CAMeL-Lab/bert-base-arabic-camelbert-mix',
        'description': 'CAMeLBERT Mix - Bon pour les dialectes',
    },
    'arabert': {
        'name':  'aubmindlab/bert-base-arabertv02',
        'description': 'AraBERT v2 - Arabe standard et dialectes',
    },
    'marbert': {
        'name':  'UBC-NLP/MARBERT',
        'description':  'MARBERT - Spécialisé dialectes arabes',
    },
    'multilingual':  {
        'name': 'bert-base-multilingual-cased',
        'description': 'mBERT - Multilingue (arabe, français, etc.)',
    }
}

# Labels de sentiment
LABEL_TO_ID = {'negative': 0, 'neutral': 1, 'positive':  2}
ID_TO_LABEL = {0: 'negative', 1: 'neutral', 2: 'positive'}


# ============================================
# DATASET PYTORCH
# ============================================

class SentimentDataset(Dataset):
    """
    Dataset PyTorch pour l'entraînement BERT. 
    """
    
    def __init__(self, texts, labels, tokenizer, max_length=128):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = self.texts[idx]
        label = self.labels[idx]
        
        # Tokenizer le texte
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        return {
            'input_ids':  encoding['input_ids'].squeeze(),
            'attention_mask': encoding['attention_mask'].squeeze(),
            'labels': torch.tensor(LABEL_TO_ID[label], dtype=torch.long)
        }


# ============================================
# MODÈLE BERT POUR SENTIMENT
# ============================================
class BertSentimentModel:  
    """
    Modèle de sentiment analysis basé sur BERT.
    """
    
    def __init__(self, model_key='camelbert-mix', num_labels=3):
        """
        Args: 
            model_key:  Clé du modèle ('camelbert-mix', 'arabert', 'marbert', 'multilingual')
            num_labels: Nombre de classes (3: positive, negative, neutral)
        """
        if not BERT_AVAILABLE:
            raise ImportError("Installez les dépendances:  pip install transformers torch scikit-learn")
        
        self. model_key = model_key
        self. model_name = AVAILABLE_MODELS[model_key]['name']
        self.num_labels = num_labels
        
        print(f"📥 Chargement du modèle: {self.model_name}")
        print(f"   Description: {AVAILABLE_MODELS[model_key]['description']}")
        
        # Charger le tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        
        # Mapping des labels
        self.label2id = {'negative': 0, 'neutral': 1, 'positive':  2}
        self.id2label = {0: 'negative', 1: 'neutral', 2: 'positive'}

        # Charger le modèle avec les labels corrects
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.model_name,  # ← Correction ici:  self.model_name
            num_labels=3,
            id2label=self.id2label,
            label2id=self. label2id
        )
        
        # Utiliser GPU si disponible
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"   Device: {self. device}")
        
        self. model.to(self.device)
        self.is_trained = False
    
    def prepare_data(self, texts, labels, test_size=0.2):
        """
        Prépare les données pour l'entraînement.
        """
        # Diviser en train/test
        X_train, X_test, y_train, y_test = train_test_split(
            texts, labels, test_size=test_size, random_state=42, stratify=labels
        )
        
        # Créer les datasets
        train_dataset = SentimentDataset(X_train, y_train, self.tokenizer)
        test_dataset = SentimentDataset(X_test, y_test, self. tokenizer)
        
        return train_dataset, test_dataset, X_test, y_test
    
    def train(self, texts, labels, epochs=3, batch_size=8, learning_rate=2e-5):
        """
        Entraîne le modèle BERT.
        """
        print("\n🎯 Préparation de l'entraînement BERT...")
        
        # Préparer les données
        train_dataset, test_dataset, X_test, y_test = self.prepare_data(texts, labels)
        
        print(f"   • Train:  {len(train_dataset)} échantillons")
        print(f"   • Test: {len(test_dataset)} échantillons")
        
        # Configuration de l'entraînement
        training_args = TrainingArguments(
            output_dir='./models/bert_checkpoints',
            num_train_epochs=epochs,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            learning_rate=learning_rate,
            warmup_steps=100,
            weight_decay=0.01,
            logging_dir='./logs',
            logging_steps=10,
            eval_strategy='epoch',
            save_strategy='epoch',
            load_best_model_at_end=True,
            metric_for_best_model='accuracy',
        )
        
        # Fonction de calcul des métriques
        def compute_metrics(pred):
            labels = pred.label_ids
            preds = pred.predictions.argmax(-1)
            precision, recall, f1, _ = precision_recall_fscore_support(
                labels, preds, average='macro'
            )
            acc = accuracy_score(labels, preds)
            return {
                'accuracy': acc,
                'precision': precision,
                'recall': recall,
                'f1': f1,
            }
        
        # Créer le Trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=test_dataset,
            compute_metrics=compute_metrics,
        )
        
        # Entraîner
        print("\n🔄 Entraînement en cours...")
        trainer.train()
        
        # Évaluation finale
        print("\n📊 Évaluation finale...")
        results = trainer.evaluate()
        
        self.is_trained = True
        self.trainer = trainer
        
        return results
    
    def predict(self, texts):
        """
        Prédit le sentiment pour une liste de textes.
        """
        if isinstance(texts, str):
            texts = [texts]
        
        self.model.eval()
        predictions = []
        
        with torch.no_grad():
            for text in texts:
                # Tokenizer
                encoding = self.tokenizer(
                    text,
                    truncation=True,
                    padding='max_length',
                    max_length=128,
                    return_tensors='pt'
                )
                
                # Envoyer au device
                input_ids = encoding['input_ids'].to(self.device)
                attention_mask = encoding['attention_mask'].to(self.device)
                
                # Prédire
                outputs = self. model(input_ids=input_ids, attention_mask=attention_mask)
                probs = torch.nn.functional. softmax(outputs.logits, dim=-1)
                pred_id = torch.argmax(probs, dim=-1).item()
                
                predictions. append(ID_TO_LABEL[pred_id])
        
        return predictions if len(predictions) > 1 else predictions[0]
    
    def predict_with_confidence(self, texts):
        """
        Prédit avec les scores de confiance.
        """
        if isinstance(texts, str):
            texts = [texts]
        
        self.model. eval()
        results = []
        
        with torch.no_grad():
            for text in texts:
                encoding = self.tokenizer(
                    text,
                    truncation=True,
                    padding='max_length',
                    max_length=128,
                    return_tensors='pt'
                )
                
                input_ids = encoding['input_ids']. to(self.device)
                attention_mask = encoding['attention_mask'].to(self.device)
                
                outputs = self. model(input_ids=input_ids, attention_mask=attention_mask)
                probs = torch.nn.functional.softmax(outputs.logits, dim=-1)[0]
                
                pred_id = torch.argmax(probs).item()
                confidence = probs[pred_id].item()
                
                results.append({
                    'label': ID_TO_LABEL[pred_id],
                    'confidence': round(confidence, 3),
                    'probabilities': {
                        'negative': round(probs[0].item(), 3),
                        'neutral': round(probs[1]. item(), 3),
                        'positive': round(probs[2].item(), 3),
                    }
                })
        
        return results if len(results) > 1 else results[0]
    
    def save(self, output_dir):
        """
        Sauvegarde le modèle entraîné.
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        self.model.save_pretrained(output_dir)
        self.tokenizer.save_pretrained(output_dir)
        print(f"✅ Modèle sauvegardé:  {output_dir}")
    
    @classmethod
    def load(cls, model_dir):
        """
        Charge un modèle sauvegardé.
        """
        instance = cls.__new__(cls)
        instance.tokenizer = AutoTokenizer.from_pretrained(model_dir)
        instance.model = AutoModelForSequenceClassification.from_pretrained(model_dir)
        instance.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        instance.model.to(instance.device)
        instance.is_trained = True
        print(f"✅ Modèle chargé: {model_dir}")
        return instance


# ============================================
# SCRIPT D'ENTRAÎNEMENT SIMPLIFIÉ
# ============================================

def train_bert_model(training_file, model_output_dir, model_key='camelbert-mix'):
    """
    Pipeline complet d'entraînement BERT. 
    """
    print("=" * 70)
    print("🤖 SOCIALPULSE MONASTIR - Entraînement BERT")
    print("=" * 70)
    
    # Charger les données
    print(f"\n📂 Chargement:  {training_file}")
    with open(training_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    texts = [item['text'] for item in data]
    labels = [item['label'] for item in data]
    
    print(f"✅ {len(texts)} échantillons chargés")
    
    # Distribution
    counter = Counter(labels)
    print(f"\n📊 Distribution:")
    for label, count in counter.items():
        emoji = {'positive': '✅', 'negative': '❌', 'neutral': '⚪'}.get(label, '•')
        print(f"   {emoji} {label}: {count}")
    
    # Créer et entraîner le modèle
    model = BertSentimentModel(model_key=model_key)
    results = model.train(texts, labels, epochs=3, batch_size=8)
    
    # Afficher les résultats
    print("\n" + "=" * 60)
    print("📊 RÉSULTATS FINAUX")
    print("=" * 60)
    print(f"   Accuracy:   {results['eval_accuracy']*100:.1f}%")
    print(f"   Precision: {results['eval_precision']:.3f}")
    print(f"   Recall:    {results['eval_recall']:.3f}")
    print(f"   F1-Score:  {results['eval_f1']:. 3f}")
    
    # Sauvegarder
    model.save(model_output_dir)
    
    # Test
    print("\n" + "=" * 60)
    print("🧪 TEST")
    print("=" * 60)
    
    test_texts = [
        "jaw rawaa barcha fi mestir",
        "mochkla kbira zahma",
        "ghodwa fama match",
    ]
    
    for text in test_texts:
        result = model.predict_with_confidence(text)
        emoji = {'positive': '✅', 'negative': '❌', 'neutral': '⚪'}.get(result['label'], '•')
        print(f"\n   📌 \"{text}\"")
        print(f"      {emoji} {result['label']} ({result['confidence']:.1%})")
    
    return model, results


# ============================================
# MAIN
# ============================================

if __name__ == "__main__": 
    # Vérifier les dépendances
    if not BERT_AVAILABLE: 
        print("\n❌ Dépendances manquantes!")
        print("\n📦 Installez avec ces commandes:")
        print("   pip install transformers")
        print("   pip install torch")
        print("   pip install scikit-learn")
        exit(1)
    
    # Chemins
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    training_file = os.path.join(project_root, 'data', 'processed', 'training_dataset_augmented.json')
    model_output = os.path.join(project_root, 'models', 'bert_sentiment')
    
    # Vérifier le fichier
    if not os.path.exists(training_file):
        # Essayer le fichier non-augmenté
        training_file = os.path.join(project_root, 'data', 'processed', 'training_dataset. json')
        if not os.path.exists(training_file):
            print(f"❌ Fichier non trouvé: {training_file}")
            exit(1)
    
    # Menu de sélection du modèle
    print("=" * 70)
    print("🤖 CHOIX DU MODÈLE BERT")
    print("=" * 70)
    print("""
  1️⃣  CAMeLBERT Mix (recommandé pour dialectes)
  2️⃣  AraBERT v2 (arabe standard + dialectes)
  3️⃣  MARBERT (spécialisé dialectes)
  4️⃣  mBERT Multilingual (arabe + français)
    """)
    
    choice = input("Votre choix (1-4): ").strip()
    
    model_keys = {'1': 'camelbert-mix', '2': 'arabert', '3': 'marbert', '4': 'multilingual'}
    model_key = model_keys.get(choice, 'camelbert-mix')
    
    # Entraîner
    model, results = train_bert_model(training_file, model_output, model_key)