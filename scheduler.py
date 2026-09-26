from apscheduler.schedulers.blocking import BlockingScheduler
from config.settings import FETCH_INTERVAL_MINUTES
from src.db import init_db, save_articles
from src.ingest import fetch_all_feeds
from src.transform import process_and_score
from src.utils import get_logger

logger = get_logger("Scheduler")

def run_pipeline():
    logger.info("Starting scheduled ETL pipeline execution...")
    try:
        raw_articles = fetch_all_feeds()
        if raw_articles:
            processed_articles = process_and_score(raw_articles)
            inserted = save_articles(processed_articles)
            logger.info(f"ETL pipeline completed. Inserted {inserted} new records.")
        else:
            logger.info("No raw articles fetched.")
    except Exception as e:
        logger.error(f"ETL pipeline run failed: {e}")

if __name__ == "__main__":
    init_db()
    # Trigger an immediate pipeline run on startup
    run_pipeline()

    # Schedule background jobs on interval
    scheduler = BlockingScheduler()
    scheduler.add_job(run_pipeline, "interval", minutes=FETCH_INTERVAL_MINUTES)
    logger.info(f"Scheduler initialized. Set to run every {FETCH_INTERVAL_MINUTES} minutes.")
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler execution stopped by user.")
