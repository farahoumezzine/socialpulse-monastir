import pandas as pd
from bertopic import BERTopic
from umap import UMAP
from hdbscan import HDBSCAN

class TopicEventAnalyzer:
    def __init__(self):
        # Configuration optimisée pour la démo (petits datasets)
        umap_model = UMAP(n_neighbors=5, n_components=5, min_dist=0.0, metric='cosine')
        hdbscan_model = HDBSCAN(min_cluster_size=5, metric='euclidean', cluster_selection_method='eom', prediction_data=True)
        
        self.topic_model = BERTopic(
            embedding_model="paraphrase-multilingual-MiniLM-L12-v2", 
            umap_model=umap_model,
            hdbscan_model=hdbscan_model,
            verbose=True
        )

    def extract_topics(self, docs, timestamps):
        # 1. Fit du modèle
        topics, probs = self.topic_model.fit_transform(docs)
        topic_info = self.topic_model.get_topic_info()
        
        # 2. Topics over time avec binning forcé
        topics_over_time = self.topic_model.topics_over_time(
            docs, 
            timestamps, 
            nr_bins=20 # Divise la période en 20 tranches temporelles
        )
        
        return topics, topic_info, topics_over_time

    def detect_anomalies(self, topics_over_time, threshold=1.5):
        alerts = []
        
        # --- CORRECTION ICI ---
        # On utilise la fonction sorted() de Python qui marche sur tous les types
        all_timestamps = sorted(topics_over_time['Timestamp'].unique())
        
        for topic_id in topics_over_time['Topic'].unique():
            if topic_id == -1: continue 
            
            # Isoler les données de ce topic
            df_topic = topics_over_time[topics_over_time['Topic'] == topic_id].copy()
            
            # 1. Créer un index complet avec toutes les dates pour combler les trous
            full_index_df = pd.DataFrame({'Timestamp': all_timestamps})
            
            # 2. Fusionner pour avoir les lignes manquantes
            merged_df = pd.merge(full_index_df, df_topic, on='Timestamp', how='left')
            
            # 3. Remplir les NaN (Fréquence nulle quand pas de message)
            merged_df['Frequency'] = merged_df['Frequency'].fillna(0)
            merged_df['Topic'] = topic_id # Remettre l'ID
            
            # Stats sur la courbe complète (y compris les zéros)
            mean_freq = merged_df['Frequency'].mean()
            std_freq = merged_df['Frequency'].std()
            
            if std_freq == 0: continue

            merged_df['z_score'] = (merged_df['Frequency'] - mean_freq) / std_freq
            
            # Détection des pics
            spikes = merged_df[merged_df['z_score'] > threshold]
            
            for _, row in spikes.iterrows():
                # On ne garde que les vrais pics (Frequency >= 2 messages)
                if row['Frequency'] < 2: continue

                keywords = self.topic_model.get_topic(topic_id)
                if keywords:
                    top_words = ", ".join([word[0] for word in keywords[:3]])
                else:
                    top_words = "Sujet inconnu"
                
                alerts.append({
                    "Date": row['Timestamp'],
                    "Topic_ID": topic_id,
                    "Keywords": top_words,
                    "Volume": int(row['Frequency']),
                    "Severity": "CRITICAL" if row['z_score'] > 2.5 else "WARNING"
                })
                
        return pd.DataFrame(alerts)
