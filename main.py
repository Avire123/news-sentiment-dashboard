from fastapi import FastAPI, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from src.db import SessionLocal, Article, init_db

app = FastAPI(
    title="News Sentiment Monitor API",
    description="REST API for querying processed news stories and sentiment analytics",
    version="1.0.0"
)

init_db()

# Dependency to yield database sessions per request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic Schema for Response Serialization
class ArticleResponse(BaseModel):
    id: int
    url: str
    title: str
    source: str
    category: Optional[str]
    summary: Optional[str]
    published_at: datetime
    sentiment_score: Optional[float]
    sentiment_label: Optional[str]

    class Config:
        from_attributes = True

@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "service": "News Sentiment Analysis API"}

@app.get("/api/v1/articles", response_model=List[ArticleResponse], tags=["Articles"])
def get_articles(
    category: Optional[str] = Query(None, description="Filter by news category (e.g. Business, Technology)"),
    sentiment: Optional[str] = Query(None, description="Filter by sentiment label (Positive, Neutral, Negative)"),
    limit: int = Query(default=50, le=200, description="Max number of articles to retrieve"),
    db: Session = Depends(get_db)
):
    query = db.query(Article)
    
    if category:
        query = query.filter(Article.category.ilike(category))
    if sentiment:
        query = query.filter(Article.sentiment_label.ilike(sentiment))
        
    articles = query.order_by(Article.published_at.desc()).limit(limit).all()
    return articles

@app.get("/api/v1/summary", tags=["Analytics"])
def get_sentiment_summary(db: Session = Depends(get_db)):
    total = db.query(Article).count()
    positive = db.query(Article).filter(Article.sentiment_label == "Positive").count()
    neutral = db.query(Article).filter(Article.sentiment_label == "Neutral").count()
    negative = db.query(Article).filter(Article.sentiment_label == "Negative").count()
    
    return {
        "total_articles": total,
        "positive_count": positive,
        "neutral_count": neutral,
        "negative_count": negative,
        "positive_ratio": round(positive / total, 2) if total > 0 else 0,
        "negative_ratio": round(negative / total, 2) if total > 0 else 0
    }
