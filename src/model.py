"""
SocialPulse Monastir - Modèle de Sentiment Analysis
====================================================
Ce module définit les modèles de classification de sentiment
pour le dialecte tunisien (Darija).

Modèles disponibles:
1. Naive Bayes (baseline, rapide)
2. SVM (Support Vector Machine)
3. Logistic Regression
4. Random Forest


"""

import json
import os
import pickle
import numpy as np
from collections import Counter

# ============================================
# 1. VECTORISATION DU TEXTE
# ============================================

class DarijaVectorizer:
    """
    Vectoriseur personnalisé pour le texte Darija. 
    Convertit le texte en vecteurs numériques (Bag of Words + TF-IDF).
    """
    
    def __init__(self, max_features=1000, min_df=1, ngram_range=(1, 2)):
        """
        Args:
            max_features:  Nombre maximum de features (mots)
            min_df: Fréquence minimale pour inclure un mot
            ngram_range: Tuple (min_n, max_n) pour les n-grammes
        """
        self.max_features = max_features
        self.min_df = min_df
        self. ngram_range = ngram_range
        self.vocabulary = {}
        self.idf = {}
        self.is_fitted = False
    
    def _tokenize(self, text):
        """Tokenise le texte en mots."""
        if not text:
            return []
        return text.lower().split()
    
    def _get_ngrams(self, tokens):
        """Génère les n-grammes à partir des tokens."""
        ngrams = []
        min_n, max_n = self.ngram_range
        
        for n in range(min_n, max_n + 1):
            for i in range(len(tokens) - n + 1):
                ngram = ' '.join(tokens[i:i + n])
                ngrams.append(ngram)
        
        return ngrams
    
    def fit(self, texts):
        """
        Apprend le vocabulaire à partir des textes.
        
        Args:
            texts: Liste de textes
        """
        # Compter les occurrences de chaque n-gramme
        ngram_counts = Counter()
        doc_counts = Counter()  # Dans combien de documents chaque ngram apparaît
        
        for text in texts:
            tokens = self._tokenize(text)
            ngrams = self._get_ngrams(tokens)
            ngram_counts.update(ngrams)
            doc_counts.update(set(ngrams))  # Compter une fois par document
        
        # Filtrer par fréquence minimale et sélectionner les top features
        filtered_ngrams = [
            ngram for ngram, count in ngram_counts.items()
            if count >= self.min_df
        ]
        
        # Trier par fréquence et garder les top
        filtered_ngrams. sort(key=lambda x: ngram_counts[x], reverse=True)
        filtered_ngrams = filtered_ngrams[:self.max_features]
        
        # Créer le vocabulaire
        self.vocabulary = {ngram: idx for idx, ngram in enumerate(filtered_ngrams)}
        
        # Calculer IDF (Inverse Document Frequency)
        num_docs = len(texts)
        self.idf = {
            ngram: np.log((num_docs + 1) / (doc_counts[ngram] + 1)) + 1
            for ngram in self.vocabulary
        }
        
        self.is_fitted = True
        return self
    
    def transform(self, texts):
        """
        Transforme les textes en vecteurs TF-IDF.
        
        Args:
            texts: Liste de textes
        
        Returns:
            numpy array de shape (n_texts, n_features)
        """
        if not self.is_fitted:
            raise ValueError("Le vectoriseur n'est pas encore entraîné.  Appelez fit() d'abord.")
        
        vectors = []
        
        for text in texts:
            tokens = self._tokenize(text)
            ngrams = self._get_ngrams(tokens)
            ngram_counts = Counter(ngrams)
            
            # Créer le vecteur TF-IDF
            vector = np.zeros(len(self.vocabulary))
            
            for ngram, idx in self.vocabulary.items():
                if ngram in ngram_counts: 
                    # TF (Term Frequency)
                    tf = ngram_counts[ngram] / len(ngrams) if ngrams else 0
                    # TF-IDF
                    vector[idx] = tf * self. idf[ngram]
            
            vectors.append(vector)
        
        return np.array(vectors)
    
    def fit_transform(self, texts):
        """Fit et transform en une seule étape."""
        self.fit(texts)
        return self.transform(texts)
    
    def get_feature_names(self):
        """Retourne la liste des features (n-grammes)."""
        return list(self.vocabulary.keys())


# ============================================
# 2. MODÈLES DE CLASSIFICATION
# ============================================

class NaiveBayesClassifier:
    """
    Classificateur Naive Bayes multinomial.
    Simple mais efficace pour la classification de texte.
    """
    
    def __init__(self, alpha=1.0):
        """
        Args: 
            alpha: Paramètre de lissage (Laplace smoothing)
        """
        self.alpha = alpha
        self.class_priors = {}
        self.feature_probs = {}
        self.classes = []
    
    def fit(self, X, y):
        """
        Entraîne le modèle. 
        
        Args:
            X: Matrice de features (n_samples, n_features)
            y: Labels (n_samples,)
        """
        self.classes = list(set(y))
        n_samples, n_features = X.shape
        
        for cls in self.classes:
            # Indices des échantillons de cette classe
            cls_indices = [i for i, label in enumerate(y) if label == cls]
            cls_samples = X[cls_indices]
            
            # Prior:  P(classe)
            self.class_priors[cls] = len(cls_indices) / n_samples
            
            # Likelihood: P(feature | classe)
            # Avec lissage de Laplace
            feature_counts = cls_samples.sum(axis=0) + self.alpha
            total_count = feature_counts.sum()
            self.feature_probs[cls] = feature_counts / total_count
        
        return self
    
    def predict_proba(self, X):
        """
        Prédit les probabilités pour chaque classe. 
        
        Args:
            X: Matrice de features
        
        Returns:
            Dict {classe: probabilités}
        """
        probas = {cls: [] for cls in self.classes}
        
        for sample in X:
            sample_probas = {}
            for cls in self.classes:
                # Log probability pour éviter underflow
                log_prob = np.log(self.class_priors[cls])
                log_prob += np.sum(sample * np.log(self.feature_probs[cls] + 1e-10))
                sample_probas[cls] = log_prob
            
            # Normaliser (softmax)
            max_log = max(sample_probas.values())
            exp_probs = {cls: np.exp(p - max_log) for cls, p in sample_probas.items()}
            total = sum(exp_probs.values())
            
            for cls in self.classes:
                probas[cls].append(exp_probs[cls] / total)
        
        return probas
    
    def predict(self, X):
        """
        Prédit la classe pour chaque échantillon. 
        
        Args:
            X: Matrice de features
        
        Returns:
            Liste de prédictions
        """
        probas = self.predict_proba(X)
        predictions = []
        
        for i in range(len(X)):
            best_cls = max(self.classes, key=lambda cls: probas[cls][i])
            predictions.append(best_cls)
        
        return predictions


class LogisticRegressionClassifier:
    """
    Classificateur par Régression Logistique.
    Plus puissant que Naive Bayes, gère mieux les features corrélées.
    """
    
    def __init__(self, learning_rate=0.1, n_iterations=1000, lambda_reg=0.01):
        """
        Args: 
            learning_rate: Taux d'apprentissage
            n_iterations: Nombre d'itérations
            lambda_reg: Paramètre de régularisation L2
        """
        self.learning_rate = learning_rate
        self.n_iterations = n_iterations
        self.lambda_reg = lambda_reg
        self. weights = {}
        self.biases = {}
        self.classes = []
    
    def _sigmoid(self, z):
        """Fonction sigmoïde."""
        return 1 / (1 + np. exp(-np.clip(z, -500, 500)))
    
    def _softmax(self, z):
        """Fonction softmax pour multi-classe."""
        exp_z = np.exp(z - np.max(z, axis=1, keepdims=True))
        return exp_z / np. sum(exp_z, axis=1, keepdims=True)
    
    def fit(self, X, y):
        """
        Entraîne le modèle avec descente de gradient.
        
        Args:
            X: Matrice de features (n_samples, n_features)
            y: Labels (n_samples,)
        """
        self.classes = list(set(y))
        n_samples, n_features = X.shape
        n_classes = len(self.classes)
        
        # Encoder les labels en one-hot
        class_to_idx = {cls: idx for idx, cls in enumerate(self.classes)}
        y_onehot = np.zeros((n_samples, n_classes))
        for i, label in enumerate(y):
            y_onehot[i, class_to_idx[label]] = 1
        
        # Initialiser les poids
        self.W = np.random.randn(n_features, n_classes) * 0.01
        self.b = np.zeros((1, n_classes))
        
        # Descente de gradient
        for iteration in range(self.n_iterations):
            # Forward pass
            z = np.dot(X, self.W) + self.b
            probas = self._softmax(z)
            
            # Calculer le gradient
            error = probas - y_onehot
            dW = (1 / n_samples) * np.dot(X.T, error) + self.lambda_reg * self.W
            db = (1 / n_samples) * np.sum(error, axis=0, keepdims=True)
            
            # Mise à jour
            self.W -= self.learning_rate * dW
            self.b -= self.learning_rate * db
        
        return self
    
    def predict_proba(self, X):
        """
        Prédit les probabilités pour chaque classe. 
        """
        z = np.dot(X, self.W) + self.b
        probas_matrix = self._softmax(z)
        
        probas = {cls: probas_matrix[: , idx]. tolist() 
                  for idx, cls in enumerate(self.classes)}
        return probas
    
    def predict(self, X):
        """
        Prédit la classe pour chaque échantillon.
        """
        probas = self. predict_proba(X)
        predictions = []
        
        for i in range(len(X)):
            best_cls = max(self.classes, key=lambda cls: probas[cls][i])
            predictions.append(best_cls)
        
        return predictions


# ============================================
# 3. MODÈLE PRINCIPAL AVEC GESTION DU DÉSÉQUILIBRE
# ============================================

class SentimentModel:
    """
    Modèle principal de sentiment analysis pour Darija tunisien.
    Gère le déséquilibre des classes et combine plusieurs approches.
    """
    
    def __init__(self, model_type='naive_bayes', handle_imbalance=True):
        """
        Args: 
            model_type: 'naive_bayes' ou 'logistic_regression'
            handle_imbalance: Appliquer des techniques pour gérer le déséquilibre
        """
        self.model_type = model_type
        self.handle_imbalance = handle_imbalance
        self.vectorizer = DarijaVectorizer(max_features=500, ngram_range=(1, 2))
        
        if model_type == 'naive_bayes':
            self.classifier = NaiveBayesClassifier(alpha=1.0)
        elif model_type == 'logistic_regression':
            self. classifier = LogisticRegressionClassifier(
                learning_rate=0.1, 
                n_iterations=500,
                lambda_reg=0.01
            )
        else:
            raise ValueError(f"Type de modèle inconnu: {model_type}")
        
        self.class_weights = {}
        self.is_trained = False
    
    def _calculate_class_weights(self, y):
        """
        Calcule les poids des classes pour gérer le déséquilibre.
        """
        counter = Counter(y)
        total = len(y)
        n_classes = len(counter)
        
        weights = {}
        for cls, count in counter.items():
            # Poids inversement proportionnel à la fréquence
            weights[cls] = total / (n_classes * count)
        
        return weights
    
    def _oversample(self, X, y):
        """
        Suréchantillonne les classes minoritaires.
        """
        counter = Counter(y)
        max_count = max(counter.values())
        
        X_resampled = list(X)
        y_resampled = list(y)
        
        for cls, count in counter.items():
            if count < max_count:
                # Indices des échantillons de cette classe
                cls_indices = [i for i, label in enumerate(y) if label == cls]
                
                # Nombre d'échantillons à ajouter
                n_to_add = max_count - count
                
                # Dupliquer aléatoirement
                for _ in range(n_to_add):
                    idx = np.random.choice(cls_indices)
                    X_resampled.append(X[idx])
                    y_resampled.append(y[idx])
        
        return X_resampled, y_resampled
    
    def train(self, texts, labels):
        """
        Entraîne le modèle complet.
        
        Args:
            texts: Liste de textes
            labels: Liste de labels ('positive', 'negative', 'neutral')
        """
        print(f"\n🎯 Entraînement du modèle ({self.model_type})...")
        
        # Vectoriser les textes
        print("   📊 Vectorisation des textes...")
        X = self.vectorizer.fit_transform(texts)
        y = labels
        
        # Gérer le déséquilibre si demandé
        if self.handle_imbalance:
            print("   ⚖️ Gestion du déséquilibre des classes...")
            self.class_weights = self._calculate_class_weights(y)
            
            # Suréchantillonnage
            X_list = [X[i] for i in range(len(X))]
            X_resampled, y_resampled = self._oversample(X_list, list(y))
            X = np.array(X_resampled)
            y = y_resampled
            
            print(f"   📈 Dataset après suréchantillonnage:  {len(y)} échantillons")
        
        # Entraîner le classificateur
        print("   🔄 Entraînement du classificateur...")
        self.classifier. fit(X, y)
        
        self.is_trained = True
        print("   ✅ Entraînement terminé!")
        
        return self
    
    def predict(self, texts):
        """
        Prédit le sentiment pour une liste de textes.
        
        Args:
            texts: Liste de textes ou un seul texte
        
        Returns:
            Liste de prédictions
        """
        if not self.is_trained:
            raise ValueError("Le modèle n'est pas entraîné. Appelez train() d'abord.")
        
        # Gérer le cas d'un seul texte
        if isinstance(texts, str):
            texts = [texts]
        
        # Vectoriser
        X = self.vectorizer. transform(texts)
        
        # Prédire
        predictions = self.classifier.predict(X)
        
        return predictions
    
    def predict_with_confidence(self, texts):
        """
        Prédit le sentiment avec le niveau de confiance.
        
        Args:
            texts: Liste de textes ou un seul texte
        
        Returns:
            Liste de dict {'label': str, 'confidence': float, 'probabilities': dict}
        """
        if not self.is_trained:
            raise ValueError("Le modèle n'est pas entraîné.  Appelez train() d'abord.")
        
        # Gérer le cas d'un seul texte
        single_input = isinstance(texts, str)
        if single_input:
            texts = [texts]
        
        # Vectoriser
        X = self.vectorizer.transform(texts)
        
        # Prédire avec probabilités
        probas = self.classifier.predict_proba(X)
        
        results = []
        for i in range(len(texts)):
            probs = {cls: probas[cls][i] for cls in probas}
            best_cls = max(probs, key=probs.get)
            
            results.append({
                'label': best_cls,
                'confidence':  round(probs[best_cls], 3),
                'probabilities': {k: round(v, 3) for k, v in probs. items()}
            })
        
        if single_input:
            return results[0]
        return results
    
    def save(self, filepath):
        """
        Sauvegarde le modèle entraîné.
        
        Args:
            filepath: Chemin du fichier de sauvegarde
        """
        if not self.is_trained:
            raise ValueError("Le modèle n'est pas entraîné.")
        
        model_data = {
            'model_type': self.model_type,
            'handle_imbalance': self.handle_imbalance,
            'vectorizer':  self.vectorizer,
            'classifier': self.classifier,
            'class_weights': self.class_weights,
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"✅ Modèle sauvegardé:  {filepath}")
    
    @classmethod
    def load(cls, filepath):
        """
        Charge un modèle sauvegardé.
        
        Args:
            filepath:  Chemin du fichier de sauvegarde
        
        Returns: 
            Instance de SentimentModel
        """
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        model = cls(
            model_type=model_data['model_type'],
            handle_imbalance=model_data['handle_imbalance']
        )
        model.vectorizer = model_data['vectorizer']
        model.classifier = model_data['classifier']
        model.class_weights = model_data['class_weights']
        model.is_trained = True
        
        print(f"✅ Modèle chargé: {filepath}")
        return model


# ============================================
# 4. ÉVALUATION DU MODÈLE
# ============================================

def evaluate_model(model, X_test, y_test):
    """
    Évalue les performances du modèle.
    
    Args:
        model:  Modèle entraîné
        X_test: Textes de test
        y_test: Labels de test
    
    Returns:
        dict:  Métriques d'évaluation
    """
    predictions = model.predict(X_test)
    
    # Accuracy
    correct = sum(1 for p, t in zip(predictions, y_test) if p == t)
    accuracy = correct / len(y_test)
    
    # Métriques par classe
    classes = list(set(y_test))
    metrics = {}
    
    for cls in classes:
        # True Positives, False Positives, False Negatives
        tp = sum(1 for p, t in zip(predictions, y_test) if p == cls and t == cls)
        fp = sum(1 for p, t in zip(predictions, y_test) if p == cls and t != cls)
        fn = sum(1 for p, t in zip(predictions, y_test) if p != cls and t == cls)
        
        # Precision, Recall, F1
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        metrics[cls] = {
            'precision': round(precision, 3),
            'recall': round(recall, 3),
            'f1': round(f1, 3),
            'support': sum(1 for t in y_test if t == cls)
        }
    
    # Macro averages
    macro_precision = np.mean([m['precision'] for m in metrics. values()])
    macro_recall = np.mean([m['recall'] for m in metrics.values()])
    macro_f1 = np.mean([m['f1'] for m in metrics.values()])
    
    return {
        'accuracy': round(accuracy, 3),
        'macro_precision': round(macro_precision, 3),
        'macro_recall': round(macro_recall, 3),
        'macro_f1': round(macro_f1, 3),
        'per_class':  metrics,
        'confusion':  {
            'predictions': predictions,
            'actuals': y_test
        }
    }


def print_evaluation_report(metrics):
    """
    Affiche un rapport d'évaluation formaté.
    """
    print("\n" + "=" * 60)
    print("RAPPORT D'EVALUATION")
    print("=" * 60)
    
    accuracy = metrics['accuracy'] * 100
    print("\nAccuracy globale: " + str(round(accuracy, 1)) + "%")
    
    print("\nMetriques macro:")
    print("   Precision: " + str(metrics['macro_precision']))
    print("   Recall:    " + str(metrics['macro_recall']))
    print("   F1-Score:  " + str(metrics['macro_f1']))
    
    print("\nMetriques par classe:")
    print("   Classe       Precision   Recall      F1-Score    Support")
    print("   " + "-" * 56)
    
    for cls, m in metrics['per_class'].items():
        if cls == 'positive':
            emoji = "[+]"
        elif cls == 'negative':
            emoji = "[-]"
        else: 
            emoji = "[o]"
        
        p = str(m['precision'])
        r = str(m['recall'])
        f1 = str(m['f1'])
        s = str(m['support'])
        
        # Formatage manuel pour éviter les erreurs
        cls_padded = cls + " " * (10 - len(cls))
        p_padded = p + " " * (12 - len(p))
        r_padded = r + " " * (12 - len(r))
        f1_padded = f1 + " " * (12 - len(f1))
        
        print("   " + emoji + " " + cls_padded + p_padded + r_padded + f1_padded + s)
    
    print("=" * 60)
# ============================================
# TEST
# ============================================

if __name__ == "__main__":
    # Test rapide
    print("🧪 Test du module model. py")
    
    # Données de test
    texts = [
        "jaw rawaa barcha hbel",
        "khayeb yesser mochkla",
        "lyoum fama match",
        "behi mezyen bnin",
        "taab fdhiha kharba",
        "ghodwa ardh film"
    ]
    labels = ['positive', 'negative', 'neutral', 'positive', 'negative', 'neutral']
    
    # Créer et entraîner le modèle
    model = SentimentModel(model_type='naive_bayes', handle_imbalance=True)
    model.train(texts, labels)
    
    # Tester
    test_text = "jaw behi barcha"
    result = model.predict_with_confidence(test_text)
    print(f"\n📝 Test:  '{test_text}'")
    print(f"   → Label: {result['label']}")
    print(f"   → Confiance: {result['confidence']}")
    print(f"   → Probabilités: {result['probabilities']}")