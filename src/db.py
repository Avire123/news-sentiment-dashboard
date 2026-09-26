from datetime import datetime, timezone
from typing import List, Dict, Any
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from config.settings import DATABASE_URL
from src.utils import get_logger

logger = get_logger("Database")

Engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=Engine)
Base = declarative_base()

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    url = Column(String(2048), unique=True, nullable=False, index=True)
    title = Column(String(512), nullable=False)
    source = Column(String(128), nullable=False)
    category = Column(String(64), nullable=True)
    summary = Column(Text, nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=False)
    ingested_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    sentiment_score = Column(Float, nullable=True)
    sentiment_label = Column(String(32), nullable=True)
    pos_score = Column(Float, nullable=True)
    neu_score = Column(Float, nullable=True)
    neg_score = Column(Float, nullable=True)

def init_db():
    Base.metadata.create_all(bind=Engine)
    logger.info("Database initialized.")

def save_articles(articles_data: List[Dict[str, Any]]) -> int:
    if not articles_data:
        return 0

    session = SessionLocal()
    inserted_count = 0
    try:
        for article in articles_data:
            stmt = sqlite_insert(Article).values(article)
            stmt = stmt.on_conflict_do_nothing(index_elements=['url'])
            result = session.execute(stmt)
            if result.rowcount > 0:
                inserted_count += 1
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Error saving articles: {e}")
        raise
    finally:
        session.close()

    return inserted_count
