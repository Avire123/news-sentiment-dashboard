from typing import List, Dict, Any
from bs4 import BeautifulSoup
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from src.utils import get_logger

logger = get_logger("Transform")
analyzer = SentimentIntensityAnalyzer()

def clean_html(raw_text: str) -> str:
    if not raw_text:
        return ""
    soup = BeautifulSoup(raw_text, "html.parser")
    return soup.get_text(separator=" ", strip=True)

def process_and_score(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    processed = []
    for article in articles:
        clean_title = clean_html(article["title"])
        clean_summary = clean_html(article["summary"])
        
        full_text = f"{clean_title}. {clean_summary}".strip()
        scores = analyzer.polarity_scores(full_text)
        
        compound = scores["compound"]
        if compound >= 0.05:
            label = "Positive"
        elif compound <= -0.05:
            label = "Negative"
        else:
            label = "Neutral"

        item = article.copy()
        item["title"] = clean_title
        item["summary"] = clean_summary[:1000]
        item["sentiment_score"] = compound
        item["sentiment_label"] = label
        item["pos_score"] = scores["pos"]
        item["neu_score"] = scores["neu"]
        item["neg_score"] = scores["neg"]
        
        processed.append(item)
        
    logger.info(f"Processed and scored sentiment for {len(processed)} articles.")
    return processed
