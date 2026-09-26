import logging
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import dateutil.parser

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)

def parse_published_date(raw_date: str) -> datetime:
    if not raw_date:
        return datetime.now(timezone.utc)
    try:
        dt = parsedate_to_datetime(raw_date)
    except Exception:
        try:
            dt = dateutil.parser.parse(raw_date)
        except Exception:
            dt = datetime.now(timezone.utc)
            
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt
