import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from config.settings import DATABASE_URL
from src.db import init_db, save_articles
from src.ingest import fetch_all_feeds
from src.transform import process_and_score

# Streamlit Page Configuration
st.set_page_config(
    page_title="News Sentiment Dashboard",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database schema automatically on boot
init_db()

@st.cache_data(ttl=30)
def load_data():
    try:
        engine = create_engine(DATABASE_URL)
        query = """
            SELECT 
                id, title, source, category, summary, url,
                published_at, sentiment_score, sentiment_label,
                pos_score, neu_score, neg_score
            FROM articles
            ORDER BY published_at DESC
        """
        df = pd.read_sql(query, con=engine)
        if not df.empty:
            df['published_at'] = pd.to_datetime(df['published_at'])
        return df
    except Exception:
        return pd.DataFrame()

# Main Header
st.title("📈 Live News Sentiment Dashboard")
st.caption("Real-time sentiment telemetry and NLP analytics for ingested RSS news streams.")

df = load_data()

# Auto-populate if database is empty on Streamlit Share
if df.empty:
    with st.spinner("Initializing database and fetching live RSS feeds..."):
        raw_data = fetch_all_feeds()
        if raw_data:
            processed = process_and_score(raw_data)
            save_articles(processed)
            st.rerun()

if not df.empty:
    # Sidebar Filters
    st.sidebar.header("Filter Telemetry")
    categories = ["All"] + sorted([c for c in df["category"].dropna().unique() if c])
    selected_category = st.sidebar.selectbox("Category", categories)
    
    sentiments = ["All"] + sorted([s for s in df["sentiment_label"].dropna().unique() if s])
    selected_sentiment = st.sidebar.selectbox("Sentiment", sentiments)
    search_query = st.sidebar.text_input("Search Headlines & Summaries", "")

    filtered_df = df.copy()
    if selected_category != "All":
        filtered_df = filtered_df[filtered_df["category"] == selected_category]
    if selected_sentiment != "All":
        filtered_df = filtered_df[filtered_df["sentiment_label"] == selected_sentiment]
    if search_query:
        filtered_df = filtered_df[
            filtered_df["title"].str.contains(search_query, case=False, na=False) |
            filtered_df["summary"].str.contains(search_query, case=False, na=False)
        ]

    # Metrics
    m1, m2, m3, m4, m5 = st.columns(5)
    total = len(filtered_df)
    pos = len(filtered_df[filtered_df["sentiment_label"] == "Positive"])
    neu = len(filtered_df[filtered_df["sentiment_label"] == "Neutral"])
    neg = len(filtered_df[filtered_df["sentiment_label"] == "Negative"])
    avg_score = filtered_df["sentiment_score"].mean() if total > 0 else 0.0

    m1.metric("Total Stories", total)
    m2.metric("Positive Stories", pos)
    m3.metric("Neutral Stories", neu)
    m4.metric("Negative Stories", neg)
    m5.metric("Avg Score", f"{avg_score:.2f}")

    st.markdown("---")

    # Visualizations
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("Sentiment Score Trend")
        st.line_chart(filtered_df.set_index("published_at")[["sentiment_score"]].sort_index())
    with col2:
        st.subheader("Sentiment Distribution")
        st.bar_chart(filtered_df["sentiment_label"].value_counts())