"""
SocialPulse Monastir - Dashboard Streamlit
==========================================
Interface web pour l'analyse de sentiment. 

"""

import streamlit as st
import requests
import pandas as pd

# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="SocialPulse Monastir",
    page_icon="📊",
    layout="wide"
)

API_URL = "http://localhost:5000"

# ============================================================
# FONCTIONS
# ============================================================

def check_api():
    """Vérifie si l'API est en ligne."""
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False


def analyze_text(text, model="bert"):
    """Analyse le sentiment d'un texte."""
    try:
        response = requests.post(
            f"{API_URL}/predict",
            json={"text": text, "model": model},
            timeout=10
        )
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}


def analyze_batch(texts, model="bert"):
    """Analyse plusieurs textes."""
    try:
        response = requests.post(
            f"{API_URL}/predict/batch",
            json={"texts": texts, "model": model},
            timeout=30
        )
        return response. json()
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================================
# INTERFACE
# ============================================================

# Header
st.title("📊 SocialPulse Monastir")
st.markdown("**Analyse de Sentiment en Darija Tunisien**")
st.markdown("---")

# Sidebar
with st.sidebar:
    st. header("⚙️ Configuration")
    
    # API Status
    api_online = check_api()
    if api_online:
        st.success("🟢 API en ligne")
    else:
        st.error("🔴 API hors ligne")
        st.warning("Lancez l'API avec:  `python src/api.py`")
    
    st.markdown("---")
    
    # Model selection
    model = st.selectbox(
        "Modèle",
        ["bert", "sklearn"],
        format_func=lambda x: "🤖 BERT (CAMeLBERT)" if x == "bert" else "📈 Naive Bayes"
    )
    
    st.markdown("---")
    
    # Info
    st.markdown("### 📝 À propos")
    st.markdown("""
    **SocialPulse Monastir**  
    Projet NLP - Analyse de sentiment
    
   
    """)

# Main content
tab1, tab2, tab3 = st.tabs(["🔍 Analyse Simple", "📋 Analyse en Lot", "📈 Statistiques"])

# ============================================================
# TAB 1: Analyse Simple
# ============================================================

with tab1:
    st. header("🔍 Analyser un texte")
    
    # Input
    text_input = st.text_area(
        "Entrez votre texte en Darija ou en Arabe",
        placeholder="Exemples:\n- الجو رائع في المنستير\n- مشكلة كبيرة وزحمة\n- jaw rawaa barcha",
        height=120
    )
    
    col1, col2 = st. columns([1, 4])
    with col1:
        analyze_btn = st.button("🔍 Analyser", type="primary", use_container_width=True)
    
    # Results
    if analyze_btn and text_input:
        if not api_online:
            st.error("❌ L'API n'est pas disponible. Lancez `python src/api.py`")
        else:
            with st.spinner("Analyse en cours..."):
                result = analyze_text(text_input, model)
            
            if result. get("success"):
                st. markdown("---")
                st.subheader("📊 Résultat")
                
                # Sentiment display
                sentiment = result["sentiment"]
                confidence = result["confidence"]
                emoji_map = {"positive": "😊", "negative": "😞", "neutral": "😐"}
                color_map = {"positive": "green", "negative": "red", "neutral": "gray"}
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"### {emoji_map.get(sentiment, '😐')}")
                    st.markdown(f"**{sentiment. upper()}**")
                
                with col2:
                    st.metric("Confiance", f"{confidence}%")
                
                with col3:
                    st.metric("Modèle", "BERT" if result["model_used"] == "bert" else "Naive Bayes")
                
                # Probabilities
                st.markdown("#### Probabilités")
                probs = result["probabilities"]
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st. progress(probs. get("positive", 0) / 100)
                    st.caption(f"✅ Positive: {probs. get('positive', 0)}%")
                with col2:
                    st. progress(probs.get("neutral", 0) / 100)
                    st.caption(f"⚪ Neutral: {probs.get('neutral', 0)}%")
                with col3:
                    st.progress(probs.get("negative", 0) / 100)
                    st.caption(f"❌ Negative: {probs.get('negative', 0)}%")
            else:
                st.error(f"❌ Erreur:  {result.get('error', 'Erreur inconnue')}")
    
    elif analyze_btn and not text_input:
        st. warning("⚠️ Veuillez entrer un texte à analyser")

# ============================================================
# TAB 2: Analyse en Lot
# ============================================================

with tab2:
    st.header("📋 Analyse en lot")
    
    batch_input = st.text_area(
        "Entrez plusieurs textes (un par ligne)",
        placeholder="الجو رائع\nمشكلة كبيرة\nغدوة فما ماتش",
        height=150
    )
    
    batch_btn = st.button("🔍 Analyser tout", type="primary", key="batch_btn")
    
    if batch_btn and batch_input:
        if not api_online:
            st.error("❌ L'API n'est pas disponible")
        else:
            texts = [t.strip() for t in batch_input.split("\n") if t.strip()]
            
            if texts:
                with st.spinner(f"Analyse de {len(texts)} textes..."):
                    result = analyze_batch(texts, model)
                
                if result. get("success"):
                    st.markdown("---")
                    
                    # Summary
                    st.subheader("📊 Résumé")
                    summary = result["summary"]
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total", summary["total"])
                    with col2:
                        st.metric("✅ Positive", summary["positive"])
                    with col3:
                        st.metric("⚪ Neutral", summary["neutral"])
                    with col4:
                        st.metric("❌ Negative", summary["negative"])
                    
                    # Chart
                    chart_data = pd.DataFrame({
                        "Sentiment": ["Positive", "Neutral", "Negative"],
                        "Count": [summary["positive"], summary["neutral"], summary["negative"]]
                    })
                    st.bar_chart(chart_data. set_index("Sentiment"))
                    
                    # Table
                    st.subheader("📋 Détails")
                    df = pd.DataFrame(result["results"])
                    if not df.empty:
                        df = df[["text", "sentiment", "confidence"]]
                        df.columns = ["Texte", "Sentiment", "Confiance (%)"]
                        st.dataframe(df, use_container_width=True)
                else:
                    st.error(f"❌ Erreur: {result.get('error')}")
            else:
                st.warning("⚠️ Aucun texte à analyser")

# ============================================================
# TAB 3: Statistiques
# ============================================================

with tab3:
    st.header("📈 Statistiques")
    
    if not api_online:
        st.warning("⚠️ L'API doit être en ligne pour afficher les statistiques")
    else:
        st.info("💡 Analysez des textes pour voir les statistiques ici")
        
        # Example analysis
        st.markdown("### 🧪 Test rapide")
        
        if st.button("Lancer un test avec des exemples"):
            test_texts = [
                "الجو رائع في المنستير",
                "مشكلة كبيرة وزحمة",
                "غدوة فما ماتش",
                "المهرجان كان ممتاز",
                "الترانسبور خايب برشا",
                "jaw rawaa barcha",
                "zahma kbira"
            ]
            
            with st.spinner("Analyse des exemples..."):
                result = analyze_batch(test_texts, model)
            
            if result. get("success"):
                summary = result["summary"]
                
                col1, col2 = st. columns(2)
                
                with col1:
                    st.markdown("#### Distribution")
                    chart_data = pd.DataFrame({
                        "Sentiment": ["Positive", "Neutral", "Negative"],
                        "Count":  [summary["positive"], summary["neutral"], summary["negative"]]
                    })
                    st.bar_chart(chart_data.set_index("Sentiment"))
                
                with col2:
                    st.markdown("#### Résultats")
                    for r in result["results"]:
                        emoji = {"positive": "✅", "negative": "❌", "neutral": "⚪"}.get(r["sentiment"], "•")
                        st.write(f"{emoji} {r['text'][: 30]}...  → **{r['sentiment']}** ({r['confidence']}%)")

# Footer
st.markdown("---")
st.markdown("**SocialPulse Monastir** | 2025")