import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from config.settings import DATABASE_URL

st.set_page_config(
    page_title="News Sentiment Dashboard",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data(ttl=30)
def load_data():
    try:
        engine = create_engine(DATABASE_URL)
        query = """
            SELECT 
                id,
                title,
                source,
                category,
                summary,
                url,
                published_at,
                sentiment_score,
                sentiment_label,
                pos_score,
                neu_score,
                neg_score
            FROM articles
            ORDER BY published_at DESC
        """
        df = pd.read_sql(query, con=engine)
        if not df.empty:
            df["published_at"] = pd.to_datetime(df["published_at"])
        return df
    except Exception as e:
        st.error(f"Error loading data from database: {e}")
        return pd.DataFrame()

st.title("📈 Live News Sentiment Dashboard")
st.caption("Real-time sentiment telemetry and NLP analytics for ingested RSS news streams.")

df = load_data()

if df.empty:
    st.warning("⚠️ No articles found in the database. Ensure  is running to populate data.")
    if st.button("🔄 Refresh Data"):
        st.rerun()
else:
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

    m1, m2, m3, m4, m5 = st.columns(5)
    
    total_articles = len(filtered_df)
    pos_count = len(filtered_df[filtered_df["sentiment_label"] == "Positive"])
    neu_count = len(filtered_df[filtered_df["sentiment_label"] == "Neutral"])
    neg_count = len(filtered_df[filtered_df["sentiment_label"] == "Negative"])
    avg_score = filtered_df["sentiment_score"].mean() if total_articles > 0 else 0.0

    m1.metric("Total Stories", total_articles)
    m2.metric("Positive Stories", pos_count, delta=f"{pos_count/total_articles:.0%}" if total_articles else "0%")
    m3.metric("Neutral Stories", neu_count)
    m4.metric("Negative Stories", neg_count, delta=f"-{neg_count/total_articles:.0%}" if total_articles else "0%", delta_color="inverse")
    m5.metric("Avg Sentiment Score", f"{avg_score:.2f}")

    st.markdown("---")

    col_chart1, col_chart2 = st.columns([2, 1])

    with col_chart1:
        st.subheader("Sentiment Score Trend Over Time")
        if not filtered_df.empty:
            chart_data = filtered_df.set_index("published_at")[["sentiment_score"]].sort_index()
            st.line_chart(chart_data, color="#008080")

    with col_chart2:
        st.subheader("Sentiment Distribution")
        if not filtered_df.empty:
            dist_data = filtered_df["sentiment_label"].value_counts()
            st.bar_chart(dist_data, color="#4B0082")

    st.markdown("---")

    st.subheader("📰 Article Stream")
    
    for _, row in filtered_df.head(25).iterrows():
        label = row['sentiment_label']
        badge_color = "🟢" if label == "Positive" else ("🔴" if label == "Negative" else "⚪")
        
        with st.expander(f"{badge_color} [{row['source']}] {row['title']}"):
            st.write(f"**Published:** {row['published_at'].strftime('%Y-%m-%d %H:%M UTC')} | **Category:** {row['category']}")
            st.write(f"**Summary:** {row['summary']}")
            st.write(
                f"**Sentiment Compound:**  | "
                f"**Pos:**  | **Neu:**  | **Neg:** "
            )
            st.markdown(f"[🔗 Read full article]({row['url']})")

    if st.sidebar.button("🔄 Refresh Data Feed"):
        st.rerun()